# MediRuta

> **Le dice al paciente oncológico exactamente a qué módulo del INEN ir, qué documentos llevar y qué estudios tener listos — antes de salir de casa.**

🔗 **App en vivo:** [mediruta.streamlit.app](https://mediruta.streamlit.app/)
📁 **Repositorio:** [github.com/evsarmientov/DataScience_FinalProject](https://github.com/evsarmientov/DataScience_FinalProject)

---

## El problema

Pacientes con diagnóstico oncológico reciente deben atenderse en el INEN (Instituto Nacional de Enfermedades Neoplásicas). Pero el primer contacto con el sistema es un laberinto:

- Las colas en el INEN empiezan a las **2:00 am** (RPP Noticias)
- Filas de **5 cuadras desde las 4am** (La República)
- El Ministro de Salud declaró: *"cuando un paciente de regiones viene a Lima, termina al final de la cola, a sufrir o morir, porque el INEN está saturado"* (AP Noticias)
- Pacientes rechazados por falta de **un solo documento** deben volver días después — con el mismo diagnóstico y el mismo miedo
- Los pacientes no saben qué cubre su seguro (SIS / EsSalud / privado) ni qué procedimientos están contemplados
- **52.42%** de los cánceres en Perú son diagnosticados en estadio avanzado (MINSA/INEN) — la demora en el primer contacto con el especialista contribuye directamente a ese número

**Sin MediRuta, los pacientes se orientan preguntando en ventanilla (horario limitado), por grupos de WhatsApp (no verificado) o pagando "tramitadores" informales (S/50–200).**

---

## La solución — 4 módulos

### Tab 1 — Diagnóstico y Documentos
El paciente escribe su diagnóstico en lenguaje libre o sube una foto de su hoja de referencia médica.

1. **OCR multimodal** (Claude Vision): extrae diagnóstico y código CIE-10 de la imagen
2. **Clasificador híbrido** (3 capas): prefijos CIE-10 → keywords → Claude como fallback → identifica el módulo INEN correcto (0–5)
3. **Scraper en tiempo real**: trae los documentos de admisión desde el portal oficial del INEN
4. **Generación de estudios clínicos**: Claude genera imagen, patología y laboratorios que pedirá el especialista

### Tab 2 — Directorio médico
159 médicos reales del INEN extraídos del Portal de Transparencia Institucional (Ley N°27806). Cargo verificado. Filtrables por módulo. No inventados.

### Tab 3 — Preguntas para tu oncólogo
Claude genera las preguntas clave para la primera consulta, organizadas por categoría:
- Sobre el diagnóstico
- Sobre el tratamiento
- Sobre el proceso en el INEN
- Efectos secundarios y calidad de vida
- Seguimiento y pronóstico

El paciente llega preparado, no desbordado.

### Tab 4 — Medicamentos
El paciente escribe el nombre del medicamento o sube una foto de su receta (OCR). El sistema:
- Verifica disponibilidad en **SIS** y **EsSalud**
- Consulta si está en el **Petitorio Nacional PNUME**
- Enlaza directo a **DIGEMID**
- *Próximamente:* farmacia más cercana con stock y precio comparado

---

## Founder

**SARMIENTO VASQUEZ, Evelyn Valeria**
Estudiante de Economía, Universidad del Pacífico 2026-I.

**Founder-market fit:** Paciente activa del INEN (desde mayo 2026). Vivió en primera persona el laberinto del sistema: diagnóstico tardío, rechazo por falta de documentos, personas que se presentaban como especialistas sin serlo. MediRuta es la herramienta que necesité y no existía.

---

## Validación con usuarios reales — 5 usuarios

| # | Perfil | Hallazgo clave |
|---|---|---|
| 1 | Usuario general | Feedback detallado de UX: resultado oculto bajo scroll → corregido en v1.1. Pidió explícitamente una guía de seguros. |
| 2 | Usuario general | *"yo lo veo bien, creo que tiene lo justo como para orientarte y se ve ordenado"* (audio) |
| 3 | Usuario general | Validación positiva de comprensibilidad |
| 4 | Familiar de paciente INEN Lima | *"Esa información nos tomó semanas descubrirla. Está todo ahí."* (llamada telefónica) |
| 5 | Familiar de paciente IREN La Libertad | Confirmó exactitud del contenido. Señal de expansión a IRENEs regionales. (conversación en persona) |

**Correcciones aplicadas en v1.1:** layout (resultado visible sin scroll), disclaimer médico visible al entrar.
**Señal de roadmap orgánica:** 2 usuarios independientes sugirieron expansión a IRENEs sin que se les preguntara.

Evidencias completas: [`docs/research/01_validacion_usuarios.md`](docs/research/01_validacion_usuarios.md)

---

## Why Now?

| Tecnología / Dato | Por qué importa ahora |
|---|---|
| **Claude API con visión (2024)** | OCR de hojas de referencia manuscritas por ~$0.001/imagen. Antes requería modelo fine-tuned. |
| **Claude haiku (2024)** | Clasificación en lenguaje natural por ~$0.0005/query. Viable sin financiamiento. |
| **pdfplumber (2022+)** | Extracción automática de tablas en PDFs gubernamentales. El directorio médico del INEN vive en un PDF. |
| **Streamlit maduro (2023+)** | Frontend completo desplegable en días por una sola persona. |
| **Ley N°27806 — Transparencia** | El directorio médico oficial del INEN es público. Con las herramientas de hoy se puede estructurar automáticamente. |
| **Tarifario INEN 2024 (RJ N°002-2024-J/INEN)** | El INEN publicó tarifas para 1,200+ procedimientos con costos diferenciados por SIS, EsSalud y privado. Por primera vez este dato es accesible y estructurable. |

---

## Modelo de negocio

**Freemium B2C + SaaS B2B institucional. El paciente nunca paga.**

| | Paciente | Institución | Red de Salud |
|---|---|---|---|
| **Precio/mes** | Gratis — siempre | S/499 | S/1,499 |
| Clasificador + documentos + estudios | ✓ | ✓ | ✓ |
| Directorio médico | ✓ | ✓ | ✓ |
| API de integración | — | ✓ | ✓ |
| Analytics de uso | — | ✓ | ✓ |
| Multi-sede (hasta 5) | — | — | ✓ |
| Chatbot WhatsApp / Telegram | — | — | ✓ |
| **Para** | Pacientes y familias | INEN, EsSalud, IRENEs | Redes regionales, EPS, seguros |

**Margen de contribución Plan Institución: ~90%** (costo variable: ~S/30–50/mes en API calls)

---

## Mercado

| | Cifra | Fuente |
|---|---|---|
| **TAM** | 72,827 nuevos casos cáncer/año en Perú + ~555,000 personas en contacto con el sistema oncológico | Globocan 2022 |
| **SAM** | ~55,000 pacientes anuales (INEN Lima + 5 IRENEs) + 6 instituciones × S/499/mes | MINSA/INEN |
| **SOM año 1** | 10,000 usuarios activos + 1 acuerdo institucional piloto | Proyección conservadora |

---

## Mercado — Seguros

El INEN opera con tres regímenes de financiamiento que definen qué accede cada paciente:

| Seguro | Cobertura oncológica | Relevancia |
|---|---|---|
| **SIS** (Seguro Integral de Salud) | Cubre procedimientos listados en PEAS + FISSAL para diagnósticos oncológicos | ~60% de pacientes INEN |
| **EsSalud** | Cobertura amplia, tarifas propias por convenio | ~25% de pacientes INEN |
| **Privado / sin seguro** | Tarifa referencial o pago de bolsillo | ~15% |

**Tarifario INEN 2024 ya en poder del equipo** — Resolución Jefatural N°002-2024-J/INEN: 1,200+ procedimientos oncológicos con costos exactos diferenciados por tipo de seguro. Fuente oficial del Estado. Próxima integración en el módulo de seguros (roadmap 6 meses).

---

## Tecnologías del curso

| Herramienta | Módulo | Uso |
|---|---|---|
| `requests` + `BeautifulSoup` | `backend/requisitos_scraper.py` | Scraping de documentos en tiempo real desde portal.inen.sld.pe y essalud.gob.pe |
| `Selenium` headless | `backend/medicos_scraper.py` | El portal INEN usa JS — Selenium detecta la estructura para el scraping |
| `pdfplumber` + `PyMuPDF` | `backend/medicos_scraper.py`, `backend/tarifario_extractor.py` | Extracción de tablas del PDF de transparencia INEN (directorio médico + tarifario 2024) |
| **Claude API — OCR vision** | `ai/ocr_extractor.py` | Extrae diagnóstico y CIE-10 de la foto de la hoja de referencia médica |
| **Claude API — clasificador** | `ai/motor_especialidad.py` | 3 capas: prefijos CIE-10 → keywords → Claude como fallback |
| **Claude API — estudios** | `ai/estudios_extractor.py` | Lista de estudios clínicos personalizada por diagnóstico |
| **Claude API — preguntas** | `ai/preguntas_extractor.py` | Genera preguntas para el oncólogo organizadas por categoría |
| **Claude API — medicamentos** | `ai/medicamentos_search.py` | Verifica disponibilidad en SIS/EsSalud + OCR de recetas |
| `Folium` | `frontend/app.py` | Mapa interactivo con ubicación del INEN y módulo destino |
| `Streamlit` | `frontend/app.py` | Frontend completo: 4 tabs, estado de sesión, upload de imágenes, caché TTL |

---

## Roadmap

| Horizonte | Hito |
|---|---|
| **3 meses** | Verificación CMP (colegiatura médica), 1,000 usuarios activos, piloto gratuito con admisión del INEN |
| **6 meses** | **Módulo de seguros** ("¿cuánto cuesta esto con mi seguro?") usando Tarifario INEN 2024 ya identificado. Expansión a IREN Norte y IREN Sur. Primer contrato institucional pagado. |
| **12 meses** | 5 hospitales integrados, chatbot WhatsApp, cobertura de tarifas por EPS privadas, 20,000 usuarios, seed round |

---

## Arquitectura

```
Usuario (navegador)
        │ HTTPS
        ▼
STREAMLIT FRONTEND  (frontend/app.py)
  ┌─────────────────────────────────────────────────────┐
  │  Tab 1            Tab 2         Tab 3       Tab 4   │
  │  Diagnóstico      Médicos       Preguntas   Medic.  │
  │  + Documentos     INEN          Oncólogo            │
  └─────┬───────────────┬──────────────┬──────────┬─────┘
        │               │              │          │
        ▼               ▼              ▼          ▼
AI LAYER  (ai/)
  ocr_extractor.py          motor_especialidad.py
  (Claude Vision + PyMuPDF)  (CIE-10 → keywords → Claude)
  estudios_extractor.py     preguntas_extractor.py
  medicamentos_search.py    (Claude haiku — JSON estructurado)
        │
        ▼
CLAUDE API — claude-haiku-4-5-20251001

DATA LAYER  (data/)
  medicos_inen.json          inen_modulos.json
  (159 médicos reales)       (5 módulos + keywords + CIE-10)
  estudios_por_modulo.json   tarifario_inen_2024.json
  (fallback sin API)         (1,200+ procedimientos + tarifas)

SCRAPING LAYER  (backend/)
  requisitos_scraper.py      medicos_scraper.py
  requests + BeautifulSoup   pdfplumber + PyMuPDF
  portal.inen.sld.pe         PDF Transparencia INEN (Ley 27806)
  essalud.gob.pe             tarifario_extractor.py (Claude Vision OCR)
```

---

## Estructura del repositorio

```
DataScience_FinalProject/
├── frontend/
│   └── app.py                        # Streamlit UI — 4 tabs, session state
├── ai/
│   ├── motor_especialidad.py         # Clasificador híbrido CIE-10 + keywords + Claude
│   ├── ocr_extractor.py              # OCR de hojas de referencia (Claude Vision)
│   ├── estudios_extractor.py         # Estudios clínicos por diagnóstico (Claude)
│   ├── preguntas_extractor.py        # Preguntas para el oncólogo (Claude)
│   └── medicamentos_search.py        # Disponibilidad SIS/EsSalud + OCR receta (Claude)
├── backend/
│   ├── requisitos_scraper.py         # Scraping INEN + EsSalud (requests + BS4)
│   ├── medicos_scraper.py            # Extracción PDF transparencia (pdfplumber)
│   └── tarifario_extractor.py        # OCR tarifario 2024 (PyMuPDF + Claude Vision)
├── data/
│   ├── inen_modulos.json             # 5 módulos INEN con keywords y prefijos CIE-10
│   ├── medicos_inen.json             # 159 médicos reales (fuente: transparencia INEN)
│   ├── estudios_por_modulo.json      # Fallback de estudios por módulo
│   └── tarifario_inen_2024.json      # Tarifario institucional 2024 extraído por OCR
├── docs/
│   ├── pitch_deck.md                 # Dossier completo YC-style (14 secciones)
│   ├── tarifario_inen_2024.pdf       # Fuente oficial: RJ N°002-2024-J/INEN
│   └── research/
│       ├── 01_validacion_usuarios.md # Evidencias de 5 usuarios reales
│       └── 05_historia_fundadora.md  # Founder-market fit documentado
└── .env.example                      # Variables de entorno requeridas
```

---

## Correr localmente

```bash
git clone https://github.com/evsarmientov/DataScience_FinalProject.git
cd DataScience_FinalProject
pip install -r requirements.txt
cp .env.example .env        # agregar ANTHROPIC_API_KEY
streamlit run frontend/app.py
```

---

## Stack

```
Python 3.11+ · Streamlit · Anthropic Claude API (claude-haiku-4-5-20251001)
requests · BeautifulSoup4 · Selenium · pdfplumber · PyMuPDF
Folium · python-dotenv
```

---

## Entregables del proyecto

| Entregable | Estado | Enlace |
|---|---|---|
| App en vivo | ✅ Desplegada | [mediruta.streamlit.app](https://mediruta.streamlit.app/) |
| Repositorio GitHub | ✅ Público | [github.com/evsarmientov/DataScience_FinalProject](https://github.com/evsarmientov/DataScience_FinalProject) |
| Pitch deck | ✅ Completo | [`docs/pitch_deck.md`](docs/pitch_deck.md) |
| Video demo | 🔗 *(agregar link aquí)* | — |
| Validación usuarios | ✅ 5 usuarios | [`docs/research/01_validacion_usuarios.md`](docs/research/01_validacion_usuarios.md) |
| Datos oficiales fuente | ✅ Incluidos | [`docs/tarifario_inen_2024.pdf`](docs/tarifario_inen_2024.pdf) |

---

*Data Science con Python 2026-I — Universidad del Pacífico*
*Docente: Alexander Quispe*
*Evelyn Valeria Sarmiento Vasquez — ev.sarmientov@alum.up.edu.pe*
