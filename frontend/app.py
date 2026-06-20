"""
MediRuta — frontend Streamlit (3 tabs)
Tab 1: Diagnóstico → Módulo → Documentos → Estudios
Tab 2: Directorio de médicos del INEN
Tab 3: Medicamentos para tu diagnóstico
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()

from ai.motor_especialidad import clasificar, _cargar_datos
from ai.ocr_extractor import extraer_diagnostico
from ai.estudios_extractor import obtener_estudios, CATEGORIAS_LABEL
from ai.medicamentos_extractor import obtener_medicamentos
from backend.app.scraping.requisitos_scraper import scrapear_url

# ---------------------------------------------------------------------------
# Datos y constantes
# ---------------------------------------------------------------------------

URL_INEN_REQUISITOS = "https://portal.inen.sld.pe/procedimiento-de-atencion-2/"

REQUISITOS_FALLBACK = [
    "DNI vigente (original y fotocopia)",
    "Hoja de Referencia con diagnóstico, código CIE-10, N° historia clínica y N° colegiatura del médico",
    "Carnet de asegurado o constancia de vigencia de derechos (EsSalud / SIS)",
    "Resultados de exámenes auxiliares recientes (si los tiene)",
]

MODULO_COLORES = {
    "0": "#6c757d", "1": "#0077b6", "2": "#e63946",
    "3": "#e07b39", "4": "#6a0572",
}

MODULO_ETIQUETAS = {
    "0": "Orientación",
    "1": "Cabeza, Cuello y Tórax",
    "2": "Ginecología y Mama",
    "3": "Aparato Digestivo",
    "4": "Tejidos Blandos y Hematología",
}


@st.cache_data(show_spinner=False)
def cargar_medicos() -> list[dict]:
    path = Path(__file__).parent.parent / "data" / "medicos_inen.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)["medicos"]

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_requisitos_inen() -> list[dict]:
    try:
        return scrapear_url(URL_INEN_REQUISITOS, verbose=False)
    except Exception:
        return []

def crear_mapa(lat, lng, nombre):
    m = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(nombre, max_width=300),
        tooltip=nombre,
        icon=folium.Icon(color="red", icon="plus-sign", prefix="glyphicon"),
    ).add_to(m)
    return m

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="MediRuta",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.modulo-mini {
    border-left: 5px solid var(--mc);
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    border-radius: 0 6px 6px 0;
    background: #fafafa;
}
.modulo-mini strong { font-size: 0.9rem; }
.modulo-mini small  { color: #666; font-size: 0.78rem; display: block; margin-top: 0.1rem; }
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
.medico-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    background: #fff;
}
.medico-card h4 { margin: 0 0 0.2rem 0; font-size: 1rem; }
.medico-card small { color: #666; }
.medico-clinica {
    display: inline-block;
    background: #f0f4ff;
    border-radius: 12px;
    padding: 0.15rem 0.6rem;
    font-size: 0.78rem;
    margin: 0.2rem 0.2rem 0 0;
    color: #0077b6;
}
.pill-modulo {
    display: inline-block;
    border-radius: 12px;
    padding: 0.15rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: white;
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("# 🏥 MediRuta")
st.markdown("*Tu ruta exacta al especialista correcto.*")
st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "📋 Diagnóstico y Documentos",
    "👨‍⚕️ Médicos del INEN",
    "💊 Medicamentos",
])

# ============================================================
# TAB 1 — Diagnóstico, módulo, documentos, estudios
# ============================================================
with tab1:
    datos_hospital = _cargar_datos()
    col_input, col_guia = st.columns([3, 2], gap="large")

    with col_guia:
        st.markdown("### Módulos del INEN")
        st.caption("Referencia — el sistema te dice cuál es el tuyo")
        for m in datos_hospital["modulos"]:
            color = MODULO_COLORES.get(m["id"], "#333")
            label = m["nombre"].split("—")[1].strip() if "—" in m["nombre"] else m["nombre"]
            st.markdown(
                f'<div class="modulo-mini" style="--mc:{color}">'
                f'<strong>Módulo {m["id"]} — {label}</strong>'
                f'<small>{m["descripcion"][:85]}…</small>'
                f'<small style="color:{color}">👨‍⚕️ {m["medicos_especialidad"]}</small>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_input:
        st.markdown("### Ingresa tu diagnóstico")

        modo = st.radio(
            "Modo:",
            ["✍️ Texto libre", "📷 Foto de la hoja de referencia"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if modo == "✍️ Texto libre":
            col_d, col_c = st.columns([3, 1])
            with col_d:
                diagnostico_texto = st.text_input(
                    "Diagnóstico",
                    placeholder="Ej: Cáncer de cuello uterino estadio IIA",
                )
            with col_c:
                cie10_texto = st.text_input(
                    "CIE-10 (opcional)",
                    placeholder="Ej: C53",
                ).strip()
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
                        st.error("No se pudo leer el documento. Usa el modo texto.")

        buscar = st.button(
            "🔍 Ver mi módulo y documentos",
            type="primary",
            use_container_width=True,
            disabled=not diagnostico_texto.strip(),
        )

    # --- Resultados Tab 1 ---
    if buscar:
        if len(diagnostico_texto.strip()) < 4:
            st.error("Diagnóstico no reconocido. Intente con más detalle (ej: 'cáncer de pulmón', 'linfoma no Hodgkin').")
            st.stop()
        with st.spinner("Analizando tu diagnóstico…"):
            resultado = clasificar(diagnostico_texto.strip(), cie10_texto or None)
        st.session_state["resultado"] = resultado
        st.session_state["diagnostico_usado"] = diagnostico_texto.strip()
        st.session_state["modulo_nombre"] = resultado["nombre"]
        st.toast("¡Resultados listos! Desplázate hacia abajo ↓", icon="✅")

    if "resultado" in st.session_state:
        resultado = st.session_state["resultado"]
        color_modulo = MODULO_COLORES.get(resultado["id"], "#1a472a")
        icono_conf = {"alta": "🟢", "media": "🟡", "baja": "🔴"}.get(resultado.get("confianza", "baja"), "🔴")

        st.divider()
        r1, r2 = st.columns([3, 2])

        with r1:
            st.markdown(
                f'<div class="resultado-card" style="--mc:{color_modulo}">'
                f'<h3>Resultado para: {st.session_state["diagnostico_usado"]}</h3>'
                f'<h2>Módulo {resultado["id"]} &nbsp;{icono_conf}</h2>'
                f'<strong style="color:#b7e4c7">{resultado["nombre"]}</strong>'
                f'<p style="margin-top:0.5rem">{resultado["descripcion"]}</p>'
                f'<div class="doctor-tag">👨‍⚕️ {resultado.get("medicos_especialidad","")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if resultado.get("confianza") != "alta":
                st.info("Confianza media/baja — confirma el módulo en **Admisión General (Módulo 0)** al llegar.")
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
                f"📍 {datos_hospital['direccion']}  \n"
                f"📞 {datos_hospital['telefono']}  \n"
                f"🕖 Admisión: Lun–Vie · 7:00 am – 1:00 pm  \n"
                f"**→ Preguntar por Módulo {resultado['id']}**"
            )

        # Documentos
        st.markdown("---")
        st.markdown("#### 📋 Documentos que debes llevar")
        with st.spinner("Obteniendo lista oficial del INEN…"):
            bloques = obtener_requisitos_inen()
        if bloques:
            for bloque in bloques:
                st.markdown(f"**{bloque['titulo']}**")
                for item in bloque["items"]:
                    st.markdown(f"- {item}")
            st.caption("✅ Fuente: portal.inen.sld.pe — datos en tiempo real.")
        else:
            st.warning("No se pudo conectar al INEN. Lista general:")
            for item in REQUISITOS_FALLBACK:
                st.markdown(f"- {item}")
        st.info("💡 Lleva **originales y fotocopias** de cada documento.")

        # Estudios clínicos
        st.markdown("---")
        st.markdown("#### 🩻 Estudios que debes llevar o tener pendientes")
        st.caption("Lo que el especialista revisará en la primera consulta.")
        with st.spinner("Generando lista de estudios…"):
            estudios = obtener_estudios(
                diagnostico=st.session_state["diagnostico_usado"],
                modulo_id=resultado["id"],
                modulo_nombre=resultado["nombre"],
            )
        fuente_tag = (
            "✨ Lista personalizada por IA para tu diagnóstico"
            if estudios.get("fuente") == "claude"
            else "📋 Lista base por módulo"
        )
        st.caption(fuente_tag)

        iconos_cat = {"imagen": "🖥️", "patologia": "🔬", "laboratorio": "🧪", "otros": "🩺"}
        cols_est = st.columns(2)
        cat_items = [(k, v) for k, v in CATEGORIAS_LABEL.items() if estudios.get(k)]
        for idx, (clave, titulo) in enumerate(cat_items):
            with cols_est[idx % 2]:
                with st.expander(f"{iconos_cat[clave]} {titulo}", expanded=True):
                    for item in estudios[clave]:
                        st.markdown(f"- {item}")
        if estudios.get("nota"):
            st.info(f"💬 **Consejo:** {estudios['nota']}")
        st.warning("⚠️ Lista orientativa. El médico puede pedir estudios adicionales.")

        st.divider()
        st.caption(
            "MediRuta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I  \n"
            "Herramienta orientativa. Confirma la información con el INEN antes de acudir."
        )

# ============================================================
# TAB 2 — Directorio de médicos
# ============================================================
with tab2:
    st.markdown("### Médicos del INEN")
    st.caption("Busca por nombre, especialidad o módulo. Datos de demo — fuente real: portal.inen.sld.pe y CMP.")

    medicos = cargar_medicos()

    # Filtros
    fc1, fc2 = st.columns([2, 2])
    with fc1:
        busqueda = st.text_input(
            "🔍 Buscar por nombre o especialidad",
            placeholder="Ej: Cardenas, Ginecología, Mama…",
        ).lower()
    with fc2:
        opciones_modulo = ["Todos los módulos"] + [
            f"Módulo {k} — {v}" for k, v in MODULO_ETIQUETAS.items()
        ]
        filtro_modulo = st.selectbox("Filtrar por módulo", opciones_modulo)

    modulo_sel = None
    if filtro_modulo != "Todos los módulos":
        modulo_sel = filtro_modulo.split(" ")[1]

    # Filtrar
    resultado_medicos = [
        m for m in medicos
        if (not busqueda or busqueda in m["nombre"].lower() or busqueda in m["especialidad"].lower()
            or busqueda in m["subespecialidad"].lower())
        and (modulo_sel is None or m["modulo_inen"] == modulo_sel)
    ]

    if not resultado_medicos:
        st.info("No se encontraron médicos con esos filtros.")
    else:
        st.caption(f"{len(resultado_medicos)} médico(s) encontrado(s)")
        cols_med = st.columns(2)
        for idx, m in enumerate(resultado_medicos):
            color = MODULO_COLORES.get(m["modulo_inen"], "#333")
            etiqueta_mod = MODULO_ETIQUETAS.get(m["modulo_inen"], "")
            clinicas_html = "".join(
                f'<span class="medico-clinica">🏥 {c}</span>' for c in m.get("clinicas_privadas", [])
            ) or '<span style="color:#999;font-size:0.8rem">Solo INEN</span>'
            with cols_med[idx % 2]:
                st.markdown(
                    f'<div class="medico-card">'
                    f'<span class="pill-modulo" style="background:{color}">Módulo {m["modulo_inen"]} · {etiqueta_mod}</span><br>'
                    f'<h4>{m["nombre"]}</h4>'
                    f'<small><b>CMP {m["cmp"]}</b> · {m["especialidad"]}</small><br>'
                    f'<small style="color:#444;margin-top:0.3rem;display:block">{m["subespecialidad"]}</small>'
                    f'<small style="color:#555;margin-top:0.3rem;display:block">🎓 {m["formacion"]}</small>'
                    f'<small style="color:#555;display:block;margin-top:0.2rem">🕖 INEN: {m.get("horario_inen","—")}</small>'
                    f'<div style="margin-top:0.5rem"><small><b>También atiende en:</b></small><br>{clinicas_html}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    st.divider()
    st.caption(
        "¿Quieres verificar el CMP de un médico? → "
        "[cmp.org.pe/verificacion](https://cmp.org.pe/verificacion/)  \n"
        "Datos de demo — en producción se actualiza desde el portal oficial del INEN y el registro CMP."
    )

# ============================================================
# TAB 3 — Medicamentos
# ============================================================
with tab3:
    st.markdown("### Medicamentos para tu diagnóstico")
    st.caption("Información orientativa para que llegues informado a tu consulta con el oncólogo.")

    # Pre-llenar desde Tab 1 si ya se buscó
    diag_t3 = st.session_state.get("diagnostico_usado", "")
    mod_nombre_t3 = st.session_state.get("modulo_nombre", "")

    if diag_t3:
        st.info(f"Usando diagnóstico de la pestaña anterior: **{diag_t3}**")
    else:
        diag_t3 = st.text_area(
            "Diagnóstico",
            placeholder="Ej: Cáncer de cuello uterino estadio IIA",
            height=80,
        )
        mod_nombre_t3 = ""

    buscar_meds = st.button(
        "💊 Ver medicamentos",
        type="primary",
        disabled=not diag_t3.strip(),
    )

    if buscar_meds:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.warning(
                "Se necesita la API key de Anthropic para esta función. "
                "Agrégala en el archivo `.env` del proyecto."
            )
        else:
            with st.spinner("Consultando información de medicamentos…"):
                meds = obtener_medicamentos(diag_t3.strip(), mod_nombre_t3)
            if meds:
                st.session_state["meds"] = meds
            else:
                st.error("No se pudo obtener la información. Intenta de nuevo.")

    if "meds" in st.session_state:
        meds = st.session_state["meds"]

        # Disponibilidad y costo
        disp = meds.get("disponibilidad_publica", "")
        costo = meds.get("costo_referencial", "")
        if disp or costo:
            dc1, dc2 = st.columns(2)
            with dc1:
                color_disp = {"Sí": "🟢", "Parcial": "🟡", "No": "🔴"}.get(disp, "⚪")
                st.metric("Disponibilidad en ESSALUD/SIS", f"{color_disp} {disp}")
            with dc2:
                st.metric("Costo referencial (particular)", costo or "—")

        st.markdown("---")

        cat_meds = [
            ("primera_linea",  "💉 Primera línea",  "Tratamiento estándar de primera elección"),
            ("segunda_linea",  "🔄 Segunda línea",  "Alternativas si hay resistencia o intolerancia"),
            ("soporte",        "🛡️ Soporte",         "Medicamentos para manejar efectos secundarios"),
        ]
        for clave, titulo, subtitulo in cat_meds:
            items = meds.get(clave, [])
            if items:
                with st.expander(f"{titulo}", expanded=True):
                    st.caption(subtitulo)
                    for item in items:
                        st.markdown(f"- {item}")

        if meds.get("nota_paciente"):
            st.info(f"💬 **Para recordar:** {meds['nota_paciente']}")

    st.divider()
    st.error(
        "⚠️ **Esta información es solo orientativa.** Los medicamentos y dosis los define "
        "exclusivamente el médico oncólogo según tu caso específico. No te automediques."
    )
    st.caption(
        "MediRuta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I"
    )
