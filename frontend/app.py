"""
CitaCorrecta — frontend Streamlit
Wizard: diagnostico → modulo INEN → checklist de documentos → mapa
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()

from ai.motor_especialidad import clasificar, _cargar_datos
from ai.ocr_extractor import extraer_diagnostico
from ai.estudios_extractor import obtener_estudios, CATEGORIAS_LABEL
from backend.app.scraping.requisitos_scraper import scrapear_url

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

URL_INEN_REQUISITOS = "https://portal.inen.sld.pe/procedimiento-de-atencion-2/"

REQUISITOS_FALLBACK = [
    "DNI vigente (original y fotocopia)",
    "Hoja de Referencia con diagnóstico, código CIE-10, N° historia clínica y N° colegiatura del médico",
    "Carnet de asegurado o constancia de vigencia de derechos (EsSalud) / SIS",
    "Resultados de exámenes auxiliares recientes (si los tiene)",
]

CONFIANZA_ICONO = {"alta": "🟢", "media": "🟡", "baja": "🔴"}

EJEMPLOS = [
    ("Cáncer de cuello uterino estadio IIA", "C53"),
    ("Adenocarcinoma gástrico antral", "C16"),
    ("Linfoma no Hodgkin difuso de células B", "C83"),
    ("Cáncer de pulmón células no pequeñas", "C34"),
    ("Tumor de mama derecha", "C50"),
]

MODULO_COLORES = {
    "0": "#6c757d",
    "1": "#0077b6",
    "2": "#e63946",
    "3": "#e07b39",
    "4": "#6a0572",
}

# ---------------------------------------------------------------------------
# Helpers cacheados
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_requisitos_inen() -> list[dict]:
    try:
        return scrapear_url(URL_INEN_REQUISITOS, verbose=False)
    except Exception:
        return []


def crear_mapa(lat: float, lng: float, nombre: str, zoom: int = 15) -> folium.Map:
    m = folium.Map(location=[lat, lng], zoom_start=zoom)
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(nombre, max_width=300),
        tooltip=nombre,
        icon=folium.Icon(color="red", icon="plus-sign", prefix="glyphicon"),
    ).add_to(m)
    return m


# ---------------------------------------------------------------------------
# Configuracion de pagina
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CitaCorrecta",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stat-box {
        background: #f8f9fa;
        border-left: 4px solid #e63946;
        padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .stat-num { font-size: 1.8rem; font-weight: 700; color: #e63946; line-height: 1; }
    .stat-desc { font-size: 0.85rem; color: #555; margin-top: 0.2rem; }
    .modulo-mini {
        border-left: 5px solid var(--mc);
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.5rem;
        border-radius: 0 6px 6px 0;
        background: #fafafa;
    }
    .modulo-mini strong { font-size: 0.9rem; }
    .modulo-mini small { color: #666; font-size: 0.78rem; display: block; margin-top: 0.1rem; }
    .resultado-card {
        border-left: 6px solid var(--mc);
        background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 100%);
        color: white;
        padding: 1.4rem 1.6rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1rem;
    }
    .resultado-card h3 { color: #b7e4c7; margin: 0 0 0.3rem 0; font-size: 1rem; }
    .resultado-card h2 { color: white; margin: 0 0 0.5rem 0; }
    .resultado-card p  { color: #d8f3dc; margin: 0; font-size: 0.9rem; }
    .doctor-tag {
        display: inline-block;
        background: rgba(255,255,255,0.18);
        border-radius: 20px;
        padding: 0.25rem 0.8rem;
        font-size: 0.82rem;
        margin-top: 0.7rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("# 🏥 CitaCorrecta")
st.markdown(
    "**Llega a la cita correcta, con los papeles correctos, a la primera.**  \n"
    "Ingresa tu diagnóstico → te decimos a qué módulo del INEN ir y qué documentos llevar."
)

# Stats del problema — anclan el "por qué"
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div class="stat-box">'
        '<div class="stat-num">3 am</div>'
        '<div class="stat-desc">Hora en que pacientes hacen cola en hospitales MINSA de Lima '
        '(Defensoría del Pueblo)</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="stat-box">'
        '<div class="stat-num">105 días</div>'
        '<div class="stat-desc">Espera promedio para endocrinología en Lima EsSalud '
        '(informe técnico EsSalud)</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="stat-box">'
        '<div class="stat-num">5 módulos</div>'
        '<div class="stat-desc">El INEN organiza su atención en módulos por tipo de cáncer — '
        'ir al módulo equivocado significa empezar de cero</div></div>',
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Layout principal: input (izq) | guia de modulos (der)
# ---------------------------------------------------------------------------

col_input, col_guia = st.columns([3, 2], gap="large")

with col_guia:
    st.markdown("### Módulos del INEN")
    st.caption("Referencia rápida — el sistema te dirá cuál es el tuyo")

    datos = _cargar_datos()
    for m in datos["modulos"]:
        color = MODULO_COLORES.get(m["id"], "#333")
        st.markdown(
            f'<div class="modulo-mini" style="--mc:{color}">'
            f'<strong>Módulo {m["id"]} — {m["nombre"].split("—")[1].strip() if "—" in m["nombre"] else m["nombre"]}</strong>'
            f'<small>{m["descripcion"][:90]}…</small>'
            f'<small style="color:{color}; margin-top:0.2rem">👨‍⚕️ {m["medicos_especialidad"]}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

with col_input:
    st.markdown("### Ingresa tu diagnóstico")

    modo = st.radio(
        "Modo de entrada:",
        ["✍️ Texto libre", "📷 Foto de la hoja de referencia"],
        horizontal=True,
        label_visibility="collapsed",
    )

    diagnostico_texto = st.session_state.get("_diag_prefill", "")
    cie10_texto = st.session_state.get("_cie_prefill", "")

    if modo == "✍️ Texto libre":
        col_d, col_c = st.columns([3, 1])
        with col_d:
            diagnostico_texto = st.text_area(
                "Diagnóstico",
                value=diagnostico_texto,
                placeholder="Ej: Cáncer de cuello uterino estadio IIA",
                height=90,
            )
        with col_c:
            cie10_texto = st.text_input(
                "CIE-10 (opcional)",
                value=cie10_texto,
                placeholder="Ej: C53",
            ).strip()

        # Botones de ejemplo para el demo
        st.caption("Prueba rápida:")
        cols_ej = st.columns(len(EJEMPLOS))
        for i, (diag, cie) in enumerate(EJEMPLOS):
            etiqueta = diag.split(" ")[1] if diag.startswith("Cáncer") else diag.split(" ")[0]
            if cols_ej[i].button(etiqueta, key=f"ej_{i}", use_container_width=True):
                st.session_state["_diag_prefill"] = diag
                st.session_state["_cie_prefill"] = cie
                st.rerun()

    else:
        archivo = st.file_uploader(
            "Sube la foto (JPG / PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Solo se usa para extraer el diagnóstico — no se almacena.",
        )
        if archivo is not None:
            st.image(archivo, width=380)
            if not os.environ.get("ANTHROPIC_API_KEY"):
                st.warning("Configura ANTHROPIC_API_KEY en tu `.env` para usar OCR.")
            else:
                with st.spinner("Leyendo documento con IA…"):
                    ocr = extraer_diagnostico(archivo.read())
                if ocr.get("diagnostico"):
                    st.success("✅ Diagnóstico extraído")
                    diagnostico_texto = ocr["diagnostico"]
                    cie10_texto = ocr.get("cie10") or ""
                    st.info(
                        f"**Diagnóstico:** {diagnostico_texto}  \n"
                        f"**CIE-10:** {cie10_texto or '—'}  \n"
                        f"**Paciente:** {ocr.get('paciente') or '—'}"
                    )
                else:
                    st.error("No se pudo leer el documento. Intenta con el modo texto.")

    buscar = st.button(
        "🔍 Ver mi módulo y documentos",
        type="primary",
        use_container_width=True,
        disabled=not diagnostico_texto.strip(),
    )

# ---------------------------------------------------------------------------
# Resultados (full width, debajo del layout principal)
# ---------------------------------------------------------------------------

if buscar:
    with st.spinner("Analizando tu diagnóstico…"):
        resultado = clasificar(diagnostico_texto.strip(), cie10_texto or None)
    st.session_state["resultado"] = resultado
    st.session_state["diagnostico_usado"] = diagnostico_texto.strip()

if "resultado" in st.session_state:
    resultado = st.session_state["resultado"]
    datos_hospital = _cargar_datos()
    color_modulo = MODULO_COLORES.get(resultado["id"], "#1a472a")

    st.divider()

    # ---- Módulo recomendado ----
    r1, r2 = st.columns([3, 2])
    with r1:
        icono_conf = CONFIANZA_ICONO.get(resultado.get("confianza", "baja"), "🔴")
        st.markdown(
            f'<div class="resultado-card" style="border-color:{color_modulo}">'
            f'<h3>Resultado para: {st.session_state["diagnostico_usado"]}</h3>'
            f'<h2>Módulo {resultado["id"]} &nbsp;{icono_conf}</h2>'
            f'<strong style="color:#b7e4c7">{resultado["nombre"]}</strong>'
            f'<p style="margin-top:0.5rem">{resultado["descripcion"]}</p>'
            f'<div class="doctor-tag">👨‍⚕️ {resultado.get("medicos_especialidad","")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if resultado.get("confianza") != "alta":
            st.info(
                "Confianza media/baja. Confirma el módulo en **Admisión General (Módulo 0)** "
                "al llegar al INEN."
            )
        if resultado.get("razon"):
            with st.expander("¿Cómo determinamos esto?"):
                st.write(resultado["razon"])
                st.caption(f"Método: {resultado.get('metodo','reglas')}")

    with r2:
        st.markdown("#### 📍 Dónde ir")
        coords = datos_hospital["coordenadas"]
        mapa = crear_mapa(
            coords["lat"], coords["lng"],
            f"{datos_hospital['nombre_completo']} — {datos_hospital['direccion']}",
        )
        st_folium(mapa, width=380, height=260)
        st.markdown(
            f"**{datos_hospital['nombre_completo']}**  \n"
            f"📍 {datos_hospital['direccion']}  \n"
            f"📞 {datos_hospital['telefono']}  \n"
            f"🕖 Admisión: Lun–Vie · 7:00 am – 1:00 pm"
        )

    # ---- Documentos ----
    st.markdown("---")
    st.markdown("#### 📋 Documentos que debes llevar")

    with st.spinner("Obteniendo lista oficial del INEN…"):
        bloques = obtener_requisitos_inen()

    if bloques:
        for bloque in bloques:
            st.markdown(f"**{bloque['titulo']}**")
            for item in bloque["items"]:
                st.markdown(f"- {item}")
        st.caption("✅ Fuente: portal.inen.sld.pe — datos obtenidos en tiempo real.")
    else:
        st.warning("No se pudo conectar al sitio del INEN. Lista general de referencia:")
        for item in REQUISITOS_FALLBACK:
            st.markdown(f"- {item}")
        st.caption("⚠️ Verifica la lista actualizada en portal.inen.sld.pe antes de ir.")

    st.info(
        "💡 **Tip:** Lleva **originales y fotocopias** de cada documento. "
        "Algunos módulos los retienen por separado."
    )

    # ---- Estudios clínicos ----
    st.markdown("---")
    st.markdown("#### 🩻 Estudios que podrías necesitar presentar")
    st.caption(
        "Además de los documentos administrativos, el especialista revisará los estudios "
        "clínicos que ya hayas hecho. Lleva todo lo que tengas."
    )

    tiene_api = bool(os.environ.get("ANTHROPIC_API_KEY"))
    spinner_msg = (
        "Generando lista personalizada con IA para tu diagnóstico…"
        if tiene_api
        else "Cargando lista por módulo…"
    )
    with st.spinner(spinner_msg):
        estudios = obtener_estudios(
            diagnostico=st.session_state["diagnostico_usado"],
            modulo_id=resultado["id"],
            modulo_nombre=resultado["nombre"],
        )

    fuente_tag = (
        "✨ Lista personalizada por IA para tu diagnóstico específico"
        if estudios.get("fuente") == "claude"
        else "📋 Lista base por módulo (activa la API key para personalización por diagnóstico)"
    )
    st.caption(fuente_tag)

    iconos_cat = {
        "imagen":      "🖥️",
        "patologia":   "🔬",
        "laboratorio": "🧪",
        "otros":       "🩺",
    }

    cols_est = st.columns(2)
    cat_items = [(k, v) for k, v in CATEGORIAS_LABEL.items() if estudios.get(k)]
    for idx, (clave, titulo) in enumerate(cat_items):
        with cols_est[idx % 2]:
            with st.expander(f"{iconos_cat[clave]} {titulo}", expanded=True):
                for item in estudios[clave]:
                    st.markdown(f"- {item}")

    if estudios.get("nota"):
        st.info(f"💬 **Consejo del especialista:** {estudios['nota']}")

    st.warning(
        "⚠️ Esta lista es orientativa. El médico que te atienda puede solicitar "
        "estudios adicionales según tu caso. No canceles la consulta si no tienes todos."
    )

    # ---- Footer ----
    st.divider()
    st.caption(
        "CitaCorrecta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I  \n"
        "Esta herramienta es orientativa. Confirma siempre la información directamente con el INEN."
    )
