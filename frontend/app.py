"""
CitaCorrecta — frontend Streamlit
Wizard: diagnostico → modulo INEN → checklist de documentos → mapa
"""
import sys
from pathlib import Path

# Ajustar PYTHONPATH para que los imports del monorepo funcionen correctamente
# independientemente del directorio desde donde se corra streamlit
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()  # carga .env si existe (desarrollo local)

from ai.motor_especialidad import clasificar, _cargar_datos
from ai.ocr_extractor import extraer_diagnostico
from backend.app.scraping.requisitos_scraper import scrapear_url

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

URL_INEN_REQUISITOS = "https://portal.inen.sld.pe/procedimiento-de-atencion-2/"
URL_REBAGLIATI_SALUD_MENTAL = "https://www.essalud.gob.pe/servicio-de-salud-mental/"

REQUISITOS_GENERALES_ESSALUD = [
    "DNI vigente (original y fotocopia)",
    "Hoja de Referencia emitida por su medico tratante (con codigo CIE-10, N° de historia clinica y N° de colegiatura del medico)",
    "Carnet de asegurado o constancia de vigencia de derechos EsSalud",
    "Resultados de examenes auxiliares recientes (si los tiene)",
]

CONFIANZA_COLOR = {"alta": "🟢", "media": "🟡", "baja": "🔴"}
CONFIANZA_LABEL = {"alta": "Alta", "media": "Media", "baja": "Baja — verificar en admision"}

# ---------------------------------------------------------------------------
# Helpers cacheados
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def obtener_requisitos_inen() -> list[dict]:
    """Scraping con cache de 1 hora. Si falla, devuelve lista vacia."""
    try:
        return scrapear_url(URL_INEN_REQUISITOS, verbose=False)
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def obtener_requisitos_salud_mental() -> list[dict]:
    try:
        return scrapear_url(URL_REBAGLIATI_SALUD_MENTAL, verbose=False)
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

# CSS minimo para mejorar la apariencia
st.markdown(
    """
    <style>
    .modulo-card {
        background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .modulo-card h2 { color: white; margin-bottom: 0.3rem; }
    .modulo-card p  { color: #d8f3dc; margin: 0; }
    .doctor-badge {
        background: rgba(255,255,255,0.15);
        border-radius: 6px;
        padding: 0.4rem 0.8rem;
        display: inline-block;
        margin-top: 0.6rem;
        font-size: 0.9rem;
    }
    .checklist-item { padding: 0.3rem 0; border-bottom: 1px solid #eee; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

col_logo, col_titulo = st.columns([1, 8])
with col_logo:
    st.markdown("## 🏥")
with col_titulo:
    st.markdown("# CitaCorrecta")
    st.markdown("*Llega a la cita correcta, con los papeles correctos, a la primera.*")

st.divider()

# ---------------------------------------------------------------------------
# Seccion de input
# ---------------------------------------------------------------------------

st.subheader("1. Cuéntanos tu caso")

modo = st.radio(
    "¿Cómo quieres ingresar el diagnóstico?",
    ["✍️ Escribir el diagnóstico", "📷 Subir foto de la hoja de referencia"],
    horizontal=True,
)

diagnostico_texto = ""
cie10_texto = ""
nombre_paciente = ""

if modo == "✍️ Escribir el diagnóstico":
    col_diag, col_cie = st.columns([3, 1])
    with col_diag:
        diagnostico_texto = st.text_area(
            "Diagnóstico",
            placeholder="Ej: Cáncer de cuello uterino estadio IIA  /  Adenocarcinoma gástrico  /  Linfoma no Hodgkin",
            height=100,
        )
    with col_cie:
        cie10_texto = st.text_input(
            "Código CIE-10 (opcional)",
            placeholder="Ej: C53",
        ).strip()
else:
    archivo = st.file_uploader(
        "Sube la foto de tu hoja de referencia o informe médico",
        type=["jpg", "jpeg", "png", "webp"],
        help="La imagen es procesada por IA — no se almacena en ningún servidor.",
    )

    if archivo is not None:
        st.image(archivo, caption="Imagen cargada", width=400)
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.warning(
                "⚠️ La variable ANTHROPIC_API_KEY no está configurada. "
                "Ingresa el diagnóstico manualmente.",
                icon="⚠️",
            )
        else:
            with st.spinner("Leyendo el documento con IA..."):
                datos_ocr = extraer_diagnostico(archivo.read())
            if datos_ocr.get("diagnostico"):
                st.success("✅ Diagnóstico extraído del documento")
                diagnostico_texto = datos_ocr["diagnostico"] or ""
                cie10_texto = datos_ocr["cie10"] or ""
                nombre_paciente = datos_ocr["paciente"] or ""
                st.info(
                    f"**Diagnóstico:** {diagnostico_texto}  \n"
                    f"**CIE-10:** {cie10_texto or 'No encontrado'}  \n"
                    f"**Paciente:** {nombre_paciente or 'No encontrado'}"
                )
            else:
                st.error(
                    "No se pudo extraer el diagnóstico de la imagen. "
                    "Intenta con una foto más clara o ingresa el diagnóstico manualmente."
                )

# ---------------------------------------------------------------------------
# Boton principal
# ---------------------------------------------------------------------------

buscar = st.button("🔍 Buscar mi módulo y documentos", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

if buscar or ("resultado" in st.session_state):
    if buscar:
        if not diagnostico_texto.strip():
            st.error("Ingresa un diagnóstico para continuar.")
            st.stop()
        with st.spinner("Analizando tu diagnóstico..."):
            resultado = clasificar(diagnostico_texto.strip(), cie10_texto or None)
        st.session_state["resultado"] = resultado
        st.session_state["diagnostico_usado"] = diagnostico_texto.strip()

    resultado = st.session_state["resultado"]
    datos_hospital = _cargar_datos()

    st.divider()
    st.subheader("2. Tu especialidad en el INEN")

    # Card principal del modulo
    confianza_icon = CONFIANZA_COLOR.get(resultado.get("confianza", "baja"), "🔴")
    confianza_label = CONFIANZA_LABEL.get(resultado.get("confianza", "baja"), "")

    st.markdown(
        f"""
        <div class="modulo-card">
            <h2>Módulo {resultado['id']} &nbsp; {confianza_icon}</h2>
            <h3 style="color:#b7e4c7; margin-top:0">{resultado['nombre']}</h3>
            <p>{resultado['descripcion']}</p>
            <div class="doctor-badge">👨‍⚕️ {resultado.get('medicos_especialidad', '')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if resultado.get("confianza") != "alta":
        st.info(
            f"**Confianza:** {confianza_label}. "
            "Te recomendamos confirmar el módulo correcto en Admisión General (Módulo 0) "
            "antes de hacer cola."
        )

    if resultado.get("razon"):
        with st.expander("¿Cómo llegamos a este resultado?"):
            st.write(resultado["razon"])
            st.caption(f"Método: {resultado.get('metodo', 'reglas')}")

    # ---------------------------------------------------------------------------
    # Documentos
    # ---------------------------------------------------------------------------

    st.divider()
    st.subheader("3. Documentos que debes llevar")

    with st.spinner("Obteniendo la lista oficial de documentos..."):
        bloques_requisitos = obtener_requisitos_inen()

    if bloques_requisitos:
        for bloque in bloques_requisitos:
            st.markdown(f"**{bloque['titulo']}**")
            for item in bloque["items"]:
                st.markdown(f"- {item}")
        st.caption(
            "Fuente: portal.inen.sld.pe — "
            f"actualizado automáticamente desde la fuente oficial."
        )
    else:
        st.warning(
            "No se pudo obtener la lista actualizada del sitio web del INEN. "
            "Mostrando los requisitos generales (verifica en admisión):"
        )
        for item in REQUISITOS_GENERALES_ESSALUD:
            st.markdown(f"- {item}")

    st.info(
        "💡 **Tip:** Lleva originales Y fotocopias de todos los documentos. "
        "Algunos módulos los solicitan por separado."
    )

    # ---------------------------------------------------------------------------
    # Mapa
    # ---------------------------------------------------------------------------

    st.divider()
    st.subheader("4. ¿Dónde queda el INEN?")

    coords = datos_hospital["coordenadas"]
    nombre_hospital = (
        f"{datos_hospital['nombre_completo']} — "
        f"{datos_hospital['direccion']} — "
        f"Tel: {datos_hospital['telefono']}"
    )

    mapa = crear_mapa(coords["lat"], coords["lng"], nombre_hospital)

    col_mapa, col_info = st.columns([3, 2])
    with col_mapa:
        st_folium(mapa, width=550, height=380)
    with col_info:
        st.markdown(f"**{datos_hospital['nombre_completo']}**")
        st.markdown(f"📍 {datos_hospital['direccion']}")
        st.markdown(f"📞 {datos_hospital['telefono']}")
        st.markdown(
            f"**Módulo a buscar al llegar:** Módulo {resultado['id']}"
        )
        st.markdown("---")
        st.markdown(
            "**Horario de Admisión (general):**  \n"
            "Lunes a Viernes · 7:00 am – 1:00 pm  \n"
            "*(Verifica horario de tu módulo específico en el INEN)*"
        )

    # ---------------------------------------------------------------------------
    # Footer
    # ---------------------------------------------------------------------------

    st.divider()
    st.caption(
        "CitaCorrecta · Proyecto final Data Science con Python · Universidad del Pacífico 2026-I  \n"
        "Esta herramienta es orientativa. Confirma siempre la información directamente "
        "con el INEN antes de acudir."
    )
