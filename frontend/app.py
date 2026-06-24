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
from ai.preguntas_extractor import obtener_preguntas, CATEGORIAS_LABEL as CATEGORIAS_PREGUNTAS
from ai.medicamentos_search import extraer_medicamento_receta, buscar_disponibilidad
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
def cargar_tarifario() -> list[dict]:
    path = Path(__file__).parent.parent / "data" / "tarifario_inen_2024.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)

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
st.warning(
    "⚠️ **Herramienta orientativa.** La información que muestra MediRuta es una guía "
    "preliminar basada en datos públicos. Cualquier consulta médica real debe hacerla "
    "con un profesional de salud. No reemplaza la atención médica.",
    icon=None,
)
st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Diagnóstico y Documentos",
    "👨‍⚕️ Médicos del INEN",
    "❓ Preguntas para tu oncólogo",
    "💊 Medicamentos",
])

# ============================================================
# TAB 1 — Diagnóstico, módulo, documentos, estudios
# ============================================================
with tab1:
    datos_hospital = _cargar_datos()

    st.markdown("### Ingresa tu diagnóstico")

    modo = st.radio(
        "Modo:",
        ["✍️ Texto libre", "📷 Foto de la hoja de referencia"],
        horizontal=True,
        label_visibility="collapsed",
    )

    diagnostico_texto = ""
    cie10_texto = ""

    if modo == "✍️ Texto libre":
        col_d, col_c, col_btn = st.columns([4, 1, 2], gap="small")
        with col_d:
            diagnostico_texto = st.text_input(
                "Diagnóstico",
                placeholder="Ej: Cáncer de cuello uterino estadio IIA",
                label_visibility="collapsed",
            )
        with col_c:
            cie10_texto = st.text_input(
                "CIE-10",
                placeholder="C53",
                label_visibility="collapsed",
            ).strip()
        with col_btn:
            buscar = st.button(
                "🔍 Ver mi ruta",
                type="primary",
                use_container_width=True,
                disabled=not diagnostico_texto.strip(),
            )
    else:
        archivo = st.file_uploader(
            "Sube la foto (JPG / PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Solo se usa para extraer el diagnóstico — no se almacena.",
        )
        buscar = False
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
                    buscar = st.button("🔍 Ver mi ruta", type="primary")
                else:
                    st.error("No se pudo leer el documento. Usa el modo texto.")

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

        # Tarifario — costos por seguro
        st.markdown("---")
        st.markdown("#### 💰 ¿Cuánto cuesta un procedimiento con tu seguro?")
        st.caption(
            "Tarifario Institucional INEN 2024 · costos oficiales diferenciados por SIS, EsSalud y privado. "
            "Fuente: RJ N°002-2024-J/INEN."
        )
        tarifario = cargar_tarifario()
        if tarifario:
            col_proc, col_btn_proc = st.columns([4, 1])
            with col_proc:
                query_proc = st.text_input(
                    "Procedimiento",
                    placeholder="Ej: biopsia, tomografía, quimioterapia, cirugía…",
                    label_visibility="collapsed",
                    key="query_proc",
                )
            with col_btn_proc:
                buscar_proc = st.button(
                    "🔍 Buscar",
                    key="btn_proc",
                    use_container_width=True,
                    disabled=not (query_proc or "").strip(),
                )

            if buscar_proc and query_proc.strip():
                q = query_proc.strip().lower()
                encontrados = [
                    p for p in tarifario
                    if q in (p.get("descripcion") or "").lower()
                ][:8]
                st.session_state["resultados_proc"] = encontrados
                st.session_state["query_proc_usado"] = query_proc.strip()

            if "resultados_proc" in st.session_state:
                resultados_proc = st.session_state["resultados_proc"]
                if not resultados_proc:
                    st.info("No se encontraron procedimientos. Prueba: 'biopsia', 'cirugía', 'tomografía', 'resonancia'…")
                else:
                    st.caption(f"{len(resultados_proc)} resultado(s) para **{st.session_state['query_proc_usado']}**")

                    def fmt_precio(val):
                        return f"S/ {val}" if val and str(val) not in ("null", "None", "") else "—"

                    for p in resultados_proc:
                        with st.expander(f"📋 {p['descripcion']}", expanded=(len(resultados_proc) == 1)):
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("SIS", fmt_precio(p.get("tarifa_sis")))
                            c2.metric("EsSalud / FFAA", fmt_precio(p.get("essalud_ffaa_pnp")))
                            c3.metric("Privado (IAFA)", fmt_precio(p.get("privado_iafa")))
                            c4.metric("Tarifa ref.", fmt_precio(p.get("tarifa_referencial")))
                            detalles = []
                            if p.get("especialidad"):
                                detalles.append(f"Especialidad: {p['especialidad']}")
                            if p.get("codigo_inen"):
                                detalles.append(f"Código INEN: {p['codigo_inen']}")
                            if detalles:
                                st.caption(" · ".join(detalles))
                    st.caption("Fuente: Tarifario Institucional Integrado INEN 2024 · RJ N°002-2024-J/INEN · Enero 2024")

        st.divider()
        st.caption(
            "MediRuta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I  \n"
            "Herramienta orientativa. Confirma la información con el INEN antes de acudir."
        )

    # Guía de módulos — al fondo, colapsada por defecto
    with st.expander("ℹ️ ¿Qué son los módulos del INEN?", expanded=False):
        st.caption("Referencia del sistema de módulos del INEN")
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

# ============================================================
# TAB 2 — Directorio de médicos
# ============================================================
with tab2:
    st.markdown("### Médicos del INEN")
    st.caption(
        "Directorio oficial extraído del Portal de Transparencia del INEN (Ley N°27806) · "
        "Relación de Personal Nombrado 2023"
    )

    medicos = cargar_medicos()

    # Pre-seleccionar módulo si viene de Tab 1
    modulo_desde_tab1 = None
    if "resultado" in st.session_state:
        modulo_desde_tab1 = st.session_state["resultado"]["id"]

    # Filtros
    fc1, fc2 = st.columns([2, 2])
    with fc1:
        busqueda = st.text_input(
            "🔍 Buscar por nombre o departamento",
            placeholder="Ej: Abugattas, Abdomen, Ginecológica…",
        ).lower()
    with fc2:
        opciones_modulo = ["Todos los módulos"] + [
            f"Módulo {k} — {v}" for k, v in MODULO_ETIQUETAS.items()
        ]
        # Pre-seleccionar módulo desde Tab 1
        idx_default = 0
        if modulo_desde_tab1:
            for i, op in enumerate(opciones_modulo):
                if op.startswith(f"Módulo {modulo_desde_tab1}"):
                    idx_default = i
                    break
        filtro_modulo = st.selectbox("Filtrar por módulo", opciones_modulo, index=idx_default)

    modulo_sel = None
    if filtro_modulo != "Todos los módulos":
        modulo_sel = filtro_modulo.split(" ")[1]

    # Filtrar
    resultado_medicos = [
        m for m in medicos
        if (not busqueda
            or busqueda in m["nombre"].lower()
            or busqueda in m.get("area", "").lower()
            or busqueda in m.get("dependencia", "").lower())
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
            area_display = m.get("area", "INEN")
            dep_display = m.get("dependencia", "")
            cargo_display = m.get("cargo", "Médico Especialista")
            formacion_display = m.get("formacion", "")
            cmp_html = f"<b>CMP {m['cmp']}</b> · " if m.get("cmp") else ""
            clinicas = m.get("clinicas_privadas", [])
            clinicas_html = (
                "".join(f'<span class="medico-clinica">🏥 {c}</span>' for c in clinicas)
                if clinicas else ""
            )
            with cols_med[idx % 2]:
                st.markdown(
                    f'<div class="medico-card">'
                    f'<span class="pill-modulo" style="background:{color}">Módulo {m["modulo_inen"]} · {etiqueta_mod}</span><br>'
                    f'<h4>{m["nombre"]}</h4>'
                    f'<small>{cmp_html}{cargo_display}</small><br>'
                    f'<small style="color:#444;margin-top:0.3rem;display:block">🏥 {area_display}</small>'
                    + (f'<small style="color:#666;display:block">↳ {dep_display}</small>' if dep_display else "")
                    + (f'<small style="color:#555;margin-top:0.3rem;display:block">🎓 {formacion_display}</small>' if formacion_display else "")
                    + f'<small style="color:#555;display:block;margin-top:0.3rem">🕖 {m.get("horario_inen","Consultar en admisión INEN")}</small>'
                    + (f'<div style="margin-top:0.5rem"><small><b>También atiende en:</b></small><br>{clinicas_html}</div>' if clinicas_html else "")
                    + f'</div>',
                    unsafe_allow_html=True,
                )

    st.divider()
    st.caption(
        "¿Quieres verificar el número CMP de un médico? → "
        "[cmp.org.pe/verificacion](https://cmp.org.pe/verificacion/)  \n"
        "Fuente: portal.inen.sld.pe/informacion-de-personal/ · Relación de Personal Nombrado (Transparencia INEN)"
    )

# ============================================================
# TAB 3 — Preguntas para el oncólogo
# ============================================================
with tab3:
    st.markdown("### Preguntas para tu oncólogo")
    st.caption("Llega preparado a tu primera consulta. Estas son las preguntas clave según tu diagnóstico.")

    diag_t3 = st.session_state.get("diagnostico_usado", "")
    mod_nombre_t3 = st.session_state.get("modulo_nombre", "")

    if diag_t3:
        st.info(f"Diagnóstico: **{diag_t3}**")
    else:
        diag_t3 = st.text_input(
            "Diagnóstico",
            placeholder="Ej: Cáncer de cuello uterino estadio IIA",
            key="diag_t3_input",
        )
        mod_nombre_t3 = ""

    buscar_preguntas = st.button(
        "❓ Generar preguntas",
        type="primary",
        disabled=not diag_t3.strip(),
    )

    if buscar_preguntas:
        with st.spinner("Preparando tu lista de preguntas…"):
            preguntas = obtener_preguntas(diag_t3.strip(), mod_nombre_t3)
        st.session_state["preguntas"] = preguntas

    if "preguntas" in st.session_state:
        preguntas = st.session_state["preguntas"]
        iconos = {
            "diagnostico":  "🔬",
            "tratamiento":  "💉",
            "proceso_inen": "🏥",
            "efectos":      "🛡️",
            "seguimiento":  "📅",
        }
        for clave, label in CATEGORIAS_PREGUNTAS.items():
            items = preguntas.get(clave, [])
            if items:
                with st.expander(f"{iconos.get(clave, '❓')} {label}", expanded=True):
                    for q in items:
                        st.markdown(f"- {q}")

        st.info("💡 **Consejo:** Lleva estas preguntas anotadas o en tu celular. El especialista agradece pacientes preparados.")

    st.divider()
    st.caption(
        "Las preguntas son generadas por IA como guía orientativa. "
        "Tu médico oncólogo es quien puede responderte según tu caso específico.  \n"
        "MediRuta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I"
    )

# ============================================================
# TAB 4 — Medicamentos (DIGEMID + disponibilidad)
# ============================================================
with tab4:
    st.markdown("### Busca tu medicamento")
    st.caption("Verifica si está disponible en SIS o EsSalud antes de ir a la farmacia.")

    modo_med = st.radio(
        "Cómo quieres buscar:",
        ["✍️ Escribir nombre", "📷 Foto de la receta"],
        horizontal=True,
        label_visibility="collapsed",
    )

    nombre_med = ""

    if modo_med == "✍️ Escribir nombre":
        col_m, col_b = st.columns([3, 1])
        with col_m:
            nombre_med = st.text_input(
                "Nombre del medicamento",
                placeholder="Ej: Paclitaxel, Tamoxifeno, Metotrexato…",
                label_visibility="collapsed",
            )
        with col_b:
            buscar_med = st.button("🔍 Buscar", type="primary", use_container_width=True, disabled=not nombre_med.strip())
    else:
        receta_img = st.file_uploader(
            "Sube la foto de tu receta (JPG / PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Solo se usa para leer el nombre del medicamento — no se almacena.",
        )
        buscar_med = False
        if receta_img is not None:
            st.image(receta_img, width=350)
            with st.spinner("Leyendo receta…"):
                nombre_med = extraer_medicamento_receta(receta_img.read())
            if nombre_med:
                st.success(f"Medicamento detectado: **{nombre_med}**")
                buscar_med = st.button("🔍 Buscar disponibilidad", type="primary")
            else:
                st.error("No se pudo leer el medicamento. Intenta con el modo texto.")

    if buscar_med and nombre_med.strip():
        with st.spinner(f"Consultando disponibilidad de {nombre_med}…"):
            resultado_med = buscar_disponibilidad(nombre_med.strip())
        if resultado_med:
            st.session_state["resultado_med"] = resultado_med
        else:
            st.error("No se pudo obtener la información. Intenta de nuevo.")

    if "resultado_med" in st.session_state:
        r = st.session_state["resultado_med"]

        st.markdown("---")
        nombre_gen = r.get("nombre_generico", nombre_med)
        en_pnume = r.get("en_pnume")
        pnume_tag = "✅ En Petitorio PNUME" if en_pnume else ("⚠️ No está en el Petitorio PNUME" if en_pnume is False else "")
        st.markdown(f"**{nombre_gen}** &nbsp; {pnume_tag}")

        col_sis, col_ess = st.columns(2)
        colores_disp = {
            "Cubierto": "🟢",
            "Parcialmente cubierto": "🟡",
            "No cubierto": "🔴",
        }
        with col_sis:
            sis = r.get("disponibilidad_sis", "Consultar en farmacia SIS")
            ic = colores_disp.get(sis, "⚪")
            st.metric("SIS", f"{ic} {sis}")
        with col_ess:
            ess = r.get("disponibilidad_essalud", "Consultar en farmacia EsSalud")
            ic = colores_disp.get(ess, "⚪")
            st.metric("EsSalud", f"{ic} {ess}")

        if r.get("nota"):
            st.info(f"💬 {r['nota']}")

        st.markdown(
            f"🔗 [Verificar en DIGEMID](https://www.digemid.minsa.gob.pe/main.asp?Seccion=845) · "
            "Busca el nombre genérico en el buscador oficial del Ministerio de Salud."
        )

        st.markdown("---")
        st.markdown("**Próximamente 🚧**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("📍 **Farmacia más cercana con stock**")
            st.caption("Geolocalización + inventario en tiempo real")
        with col_p2:
            st.markdown("💰 **Precio referencial comparado**")
            st.caption("Cadenas de farmacias vs. genérico disponible")

    st.divider()
    st.error(
        "⚠️ La disponibilidad mostrada es referencial. Confirma siempre con la farmacia del "
        "INEN, SIS o EsSalud antes de acudir. No te automediques."
    )
    st.caption(
        "MediRuta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I"
    )
