# MediRuta 🏥

> **Tu ruta exacta al especialista correcto.**

🔗 **App en vivo:** [mediruta.streamlit.app](https://mediruta.streamlit.app/)

---

## El problema

Pacientes con diagnóstico oncológico llegan al INEN sin saber a qué módulo ir, qué documentos llevar ni qué estudios tener listos. Hacen colas desde las 3am y muchos son rechazados por falta de un documento o por ir al módulo equivocado.

## Qué hace MediRuta

| Tab | Función |
|---|---|
| 📋 Diagnóstico y Documentos | Ingresa tu diagnóstico (texto libre o foto de la hoja de referencia) → identifica el módulo INEN correcto, lista documentos scrapeados en tiempo real de la web oficial y estudios clínicos generados por IA |
| 👨‍⚕️ Médicos del INEN | Directorio de 159 médicos reales extraído del Portal de Transparencia del INEN (Ley N°27806), filtrable por módulo |
| 💊 Medicamentos | Información orientativa sobre tratamientos farmacológicos por diagnóstico oncológico |

## Founder

**SARMIENTO VASQUEZ, Evelyn Valeria** — Estudiante de Data Science, Universidad del Pacífico 2026-I.

*Founder-market fit:* familiar directo atendido en el INEN. La burocracia y desorientación del sistema público son un dolor personal, no solo un caso de estudio.

## Herramientas del curso usadas

| Herramienta | Dónde en el código | Por qué |
|---|---|---|
| **Web scraping** (`requests` + `BeautifulSoup`) | `backend/app/scraping/requisitos_scraper.py` | Trae los requisitos de admisión en tiempo real desde portal.inen.sld.pe y essalud.gob.pe — no inventados ni desactualizados |
| **Selenium** | `backend/app/scraping/medicos_scraper.py` | El portal del INEN usa un page builder JS; implementamos Selenium headless para detectar la estructura de la página |
| **PDF scraping** (`pdfplumber` + `PyMuPDF`) | `backend/app/scraping/medicos_scraper.py` | Extrae el directorio médico del PDF de Relación de Personal Nombrado (Portal de Transparencia INEN) usando detección automática de tablas |
| **Claude API — OCR multimodal** | `ai/ocr_extractor.py` | Extrae diagnóstico y CIE-10 de la foto de la hoja de referencia del paciente |
| **Claude API — clasificador híbrido** | `ai/motor_especialidad.py` | 3 capas: prefijos CIE-10 → keywords → Claude como fallback; funciona sin API key para diagnósticos comunes |
| **Claude API — estudios clínicos** | `ai/estudios_extractor.py` | Genera lista de estudios (imagen, patología, laboratorio) personalizada para el diagnóstico |
| **Claude API — medicamentos** | `ai/medicamentos_extractor.py` | Información de tratamientos farmacológicos por diagnóstico oncológico |
| **Geoespacial** (`Folium`) | `frontend/app.py` | Mapa interactivo con la ubicación del INEN y el módulo al que debe ir el paciente |
| **Streamlit** | `frontend/app.py` | Frontend completo — 3 tabs, manejo de estado, upload de imágenes, caché con TTL |

## Validación con usuarios reales

3 usuarios probaron el MVP (evidencias en `docs/research/`):

- **Usuario 1:** feedback detallado — identificó que los resultados quedaban ocultos debajo de la guía de módulos → corregido en v1.1
- **Usuario 2:** *"yo lo veo bien, creo que tiene lo justo como para orientarte y se ve ordenado"*
- **Usuario 3:** validación positiva

Los usuarios 1 y 2 identificaron de forma independiente el mismo problema de UX (resultados no visibles sin scroll), confirmando que era un problema real y no aislado.

## Correr localmente

```bash
git clone https://github.com/evsarmientov/DataScience_FinalProject.git
cd DataScience_FinalProject
pip install -r requirements.txt
cp .env.example .env        # agrega tu ANTHROPIC_API_KEY
streamlit run frontend/app.py
```

## Estructura del repositorio

```
MediRuta/
├── frontend/app.py                          # Streamlit UI — 3 tabs
├── ai/
│   ├── motor_especialidad.py                # clasificador híbrido CIE-10 + keywords + Claude
│   ├── ocr_extractor.py                     # OCR multimodal (Claude vision)
│   ├── estudios_extractor.py                # estudios clínicos por diagnóstico
│   └── medicamentos_extractor.py            # información farmacológica
├── backend/app/scraping/
│   ├── requisitos_scraper.py                # scraping INEN + EsSalud (BS4)
│   └── medicos_scraper.py                   # extracción PDF transparencia (pdfplumber)
├── data/
│   ├── inen_modulos.json                    # 5 módulos INEN con keywords y prefijos CIE-10
│   ├── medicos_inen.json                    # 159 médicos reales (fuente: transparencia INEN)
│   └── estudios_por_modulo.json             # fallback de estudios por módulo
└── docs/
    └── research/                            # evidencias de validación con usuarios reales
```

## Stack

```
Python 3.11+ · Streamlit · Anthropic Claude API
requests + BeautifulSoup4 · pdfplumber · PyMuPDF · Selenium
Folium · python-dotenv
```

## Licencia

MIT
