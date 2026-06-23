# MediRuta — Dossier YC-Style
**Data Science con Python 2026-I — Universidad del Pacífico**
**Docente: Alexander Quispe**

---

## 1. One-liner

> **MediRuta le dice al paciente oncológico exactamente a qué módulo del INEN ir, qué documentos llevar y qué estudios tener listos — antes de salir de casa.**

---

## 2. Founder

**SARMIENTO VASQUEZ, Evelyn Valeria**
Estudiante de Economía con especialización en Data Science, Universidad del Pacífico 2026-I.

**Founder-market fit:** Paciente activa del INEN (en observación desde 2025). Vivió en primera persona el laberinto del sistema: diagnóstico tardío, rechazo por falta de documentos, desorientación dentro del hospital, desinformación sobre especialistas. MediRuta es la herramienta que necesité y no existía.

**Cobertura de roles como solo founder con IA:**
- Producto y diseño: decisiones propias basadas en experiencia real de usuario
- Backend e ingeniería: Claude Code como CTO virtual — construyó y depuró el sistema de scraping, clasificador y API
- Data Science: Claude API (haiku) para OCR, clasificación, generación de estudios y medicamentos
- Frontend: Streamlit como framework de despliegue rápido

---

## 3. Problema

**Quién lo sufre:** Pacientes con diagnóstico oncológico reciente que deben atenderse en el INEN — muchos provenientes de provincias, con SIS, en su primer contacto con el sistema oncológico especializado. También sus familiares cuidadores.

**Qué tan doloroso:**
- Las colas en el INEN empiezan a las **2:00 am** (RPP Noticias)
- Filas de **5 cuadras** desde las 4am (La República)
- El propio Ministro de Salud declaró: *"cuando un paciente de regiones viene a Lima, termina al final de la cola, a sufrir o morir, porque el INEN está saturado"* (AP Noticias)
- Pacientes rechazados por falta de **un documento** deben volver días después — con el mismo diagnóstico, el mismo miedo, y otro día perdido
- **52.42%** de cánceres en Perú son diagnosticados en estadio avanzado (MINSA/INEN) — la demora en el primer contacto con el especialista contribuye directamente a ese número

**Cómo lo resuelven hoy sin MediRuta:**
- Preguntando en ventanilla (horario limitado, información a veces incorrecta)
- Grupos de WhatsApp de pacientes (información no verificada, desactualizada)
- Familiares que ya pasaron por el proceso (no siempre disponibles)
- "Tramitadores" informales que cobran por orientar (aprovechan la desesperación)

**Evidencia documentada** (`docs/research/`):
1. Validación con 3 usuarios reales (feedback de usabilidad, corregido en v1.1)
2. Cobertura periodística: RPP, La República, AP Noticias — colas desde 2am
3. Globocan 2022: 72,827 nuevos casos/año, 35,934 muertes/año
4. SciELO Perú: barreras informacionales documentadas en sistema público limeño
5. CADE Salud 2026: diagnóstico oportuno como prioridad nacional

---

## 4. Solución & Insight

**Qué construye MediRuta exactamente:**

Una app web con tres módulos:

- **Tab 1 — Diagnóstico y Documentos:** el paciente ingresa su diagnóstico en texto libre o sube una foto de su hoja de referencia. El clasificador híbrido identifica el módulo correcto del INEN (0–5). Un scraper en tiempo real trae los documentos necesarios desde el portal oficial. Claude genera los estudios clínicos que pedirá el especialista.

- **Tab 2 — Directorio médico:** 159 médicos reales del INEN extraídos del Portal de Transparencia Institucional (Ley N°27806). Filtrables por módulo. Cargo verificado. No inventados.

- **Tab 3 — Medicamentos:** primera y segunda línea de tratamiento, más medicamentos de soporte, para que el paciente llegue informado a la primera consulta.

**El insight no obvio:**

> El problema no es *acceso* — es *orientación*. Un paciente que llega al módulo correcto con los documentos correctos se atiende en una visita. Un paciente desorientado pierde semanas de un tiempo que no tiene.

La desorientación no es un problema secundario: es el cuello de botella que convierte diagnósticos tempranos en tardíos. MediRuta no mejora la infraestructura del sistema — elimina la fricción del primer contacto.

---

## 5. Why Now?

Este producto no era posible hace 3 años:

| Tecnología | Por qué importa ahora |
|---|---|
| **Claude API con visión (2024)** | OCR de hojas de referencia manuscritas por ~$0.001 por imagen. Antes requería PaddleOCR + modelo fine-tuned. |
| **Claude haiku (2024)** | Clasificación de especialidades médicas en lenguaje natural por ~$0.0005 por query. Viable sin financiamiento. |
| **pdfplumber (2022+)** | Extracción automática de tablas en PDFs gubernamentales sin OCR — el directorio médico del INEN vive en un PDF. |
| **Streamlit (2019+, maduro 2023)** | Una sola persona construye frontend completo desplegable en Streamlit Community Cloud en días, no semanas. |
| **Ley N°27806 — Portal de Transparencia** | El directorio médico oficial del INEN es público por ley. Con las herramientas de hoy se puede extraer y estructurar automáticamente. |

La combinación de datos abiertos + LLMs baratos + herramientas de despliegue rápido hace posible en 11 días lo que antes requería un equipo y meses.

---

## 6. Mercado

### TAM — Total Addressable Market
- **72,827** nuevos casos de cáncer por año en Perú (Globocan 2022)
- **185,000+** personas viviendo con cáncer en los últimos 5 años
- Incluyendo familias y cuidadores (~2 por paciente): **~555,000 personas** en contacto activo con el sistema oncológico cada año
- Mercado institucional: ~50 hospitales con servicio oncológico en Perú → a S/500/mes = **S/300,000/año** solo en Perú
- Expandido a Latinoamérica (sistemas públicos similares en Colombia, México, Argentina): **10x**

### SAM — Serviceable Available Market
- INEN Lima: ~40,000 pacientes activos anuales
- 5 IRENEs regionales: ~15,000 pacientes adicionales
- Total pacientes directamente servibles: **~55,000/año**
- Institucional directo: INEN + 5 IRENEs = 6 instituciones × S/499/mes = **S/35,928/año**

### SOM — Serviceable Obtainable Market (12 meses)
- **10,000 usuarios activos** (app web, gratuita)
- **1 acuerdo institucional piloto** (INEN o EsSalud Lima)
- ARR objetivo año 1: **S/6,000–12,000**

*Fuentes: Globocan 2022 vía Infobae Perú (junio 2026), MINSA/INEN estadísticas institucionales.*

---

## 7. Competencia y Moat

| Alternativa | Orientación módulo | Documentos en tiempo real | Directorio verificado | 24/7 | Costo |
|---|---|---|---|---|---|
| Ventanilla INEN | ✓ | ✓ | — | ✗ lun-vie | Gratis |
| Portal web INEN | Parcial | Desactualizado | ✗ | ✓ | Gratis |
| Grupos WhatsApp pacientes | Informal | No verificado | ✗ | ✓ | Gratis |
| "Tramitador" informal | ✓ | ✓ | ✗ | Pagando | S/50–200 |
| **MediRuta** | **✓ IA** | **✓ Tiempo real** | **✓ 159 médicos** | **✓** | **Gratis** |

**Moat (qué nos hace difíciles de copiar):**

1. **Datos propios verificados:** 159 médicos con cargos reales del portal de transparencia — no es un directorio inventado, es un activo de datos que requiere trabajo para construir y mantener actualizado.
2. **Clasificador híbrido resiliente:** funciona con prefijos CIE-10 → keywords → Claude. El 80% de consultas se resuelven sin API key. Competidores que dependen solo de un LLM son frágiles.
3. **Confianza institucional:** datos de fuente oficial (Ley N°27806). No somos un blog de salud — somos una herramienta basada en documentos públicos verificables.
4. **Founder-market fit irreplicable:** no es un proyecto de clase. La founder es paciente activa del INEN y usuario real del producto.

---

## 8. Producto — Demo y Arquitectura

**URL pública:** https://mediruta.streamlit.app
**Repositorio:** https://github.com/evsarmientov/DataScience_FinalProject

### Flujo principal del usuario
1. Ingresa diagnóstico en texto libre: *"Cáncer de mama estadio II"*
2. Clasificador híbrido identifica: **Módulo 2 — Ginecología y Mama**
3. Scraper trae en tiempo real los documentos del portal INEN
4. Claude genera los estudios que pedirá el especialista (imagen, patología, laboratorio)
5. Tab 2: directorio filtrado por módulo — médicos reales con cargo verificado
6. Tab 3: primera línea de tratamiento, segunda línea, soporte

### Diagrama de arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO (navegador)                  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
┌───────────────────────▼─────────────────────────────────┐
│           STREAMLIT FRONTEND  (frontend/app.py)         │
│                                                         │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐  │
│  │  Tab 1           │ │  Tab 2       │ │  Tab 3      │  │
│  │  Diagnóstico     │ │  Médicos     │ │  Medicam.   │  │
│  │  + Documentos    │ │  del INEN    │ │             │  │
│  └────────┬─────────┘ └──────┬───────┘ └──────┬──────┘  │
└───────────┼──────────────────┼────────────────┼─────────┘
            │                  │                │
┌───────────▼──────────────────▼────────────────▼─────────┐
│                      AI LAYER  (ai/)                     │
│                                                          │
│  ┌───────────────┐  ┌──────────────────────────────────┐ │
│  │ ocr_extractor │  │  motor_especialidad.py           │ │
│  │ (Claude Vision│  │  1. Prefijos CIE-10 (sin API)    │ │
│  │  + PyMuPDF)   │  │  2. Keywords (sin API)           │ │
│  └───────┬───────┘  │  3. Claude haiku (fallback)      │ │
│          │          └──────────────┬───────────────────┘ │
│  ┌───────▼──────────────────────────▼──────────────────┐ │
│  │         estudios_extractor.py                       │ │
│  │         medicamentos_extractor.py                   │ │
│  │         (Claude haiku — generación estructurada)    │ │
│  └───────────────────────────────────────────────────┬─┘ │
└──────────────────────────────────────────────────────┼───┘
                                                       │
┌──────────────────────────────────────────────────────▼───┐
│                   CLAUDE API (Anthropic)                  │
│              claude-haiku-4-5-20251001                   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    DATA LAYER  (data/)                   │
│                                                          │
│  medicos_inen.json         inen_modulos.json             │
│  (159 médicos reales)      (5 módulos + keywords)        │
│  Fuente: PDF Transparencia  estudios_por_modulo.json     │
│  INEN — Ley N°27806        (fallback sin API)            │
└───────────┬──────────────────────────────────────────────┘
            │ Origen de los datos
┌───────────▼──────────────────────────────────────────────┐
│                  SCRAPING LAYER (backend/)               │
│                                                          │
│  requisitos_scraper.py          medicos_scraper.py       │
│  requests + BeautifulSoup       pdfplumber + PyMuPDF     │
│  → portal.inen.sld.pe           + Selenium               │
│  → essalud.gob.pe               → PDF Transparencia INEN │
│  (documentos en tiempo real)    (extracción directorio)  │
└──────────────────────────────────────────────────────────┘
```

### Modelos e IAs usados

| Modelo / Herramienta | Uso | Por qué |
|---|---|---|
| Claude claude-haiku-4-5-20251001 | OCR hojas médicas, clasificación fallback, estudios clínicos, medicamentos | Costo ~$0.001/query, contexto largo, JSON estructurado confiable |
| pdfplumber | Extracción de tablas del PDF de transparencia INEN | Detección automática de columnas en PDFs gubernamentales con texto seleccionable |
| PyMuPDF (fitz) | Inspección de coordenadas del PDF | Complemento a pdfplumber para PDFs complejos |
| Selenium headless | Detección de estructura del portal INEN (JS-rendered) | El portal usa DSLC page builder — el contenido no está en el HTML estático |
| Folium | Mapa interactivo de la ubicación del INEN | Geolocalización del hospital con marcador del módulo destino |

---

## 9. Modelo de Negocio y Pricing

**Modelo:** Freemium B2C + SaaS B2B institucional. El paciente nunca paga. El sistema que se beneficia de tenerlo bien orientado, sí.

### Tres planes

| | **Paciente** | **Institución** | **Red de Salud** |
|---|---|---|---|
| **Precio** | Gratis — siempre | S/499/mes | S/1,499/mes |
| Clasificador de módulo | ✓ | ✓ | ✓ |
| Documentos en tiempo real | ✓ | ✓ | ✓ |
| Estudios clínicos por IA | ✓ | ✓ | ✓ |
| Directorio médico básico | ✓ | ✓ | ✓ |
| API de integración | — | ✓ | ✓ |
| Analytics de uso | — | ✓ | ✓ |
| Directorio médico premium (clínicas privadas) | — | — | ✓ |
| Multi-sede (hasta 5) | — | — | ✓ |
| Chatbot WhatsApp / Telegram | — | — | ✓ |
| **Para** | Pacientes y familias | INEN, EsSalud, IRENEs | Redes regionales, EPS, seguros |

### Contribution margin

| Plan | Precio | Costo variable/mes | Margen |
|---|---|---|---|
| Paciente | S/0 | S/0.05/query (Claude haiku) | — |
| Institución | S/499 | ~S/30–50 (API calls est.) | ~90% |
| Red de Salud | S/1,499 | ~S/80–120 (API calls est.) | ~87% |

*Costo base Claude haiku: ~$0.0008 por query. A 500 queries/día por institución = ~$12/mes.*

---

## 10. Go-to-Market

**Primeros 10 usuarios:**
- Red personal de la founder + compartir en grupos de WhatsApp de pacientes oncológicos del INEN
- Post en páginas de Facebook: "Liga Peruana de Lucha contra el Cáncer" (comunidades activas de pacientes)

**Primeros 100 usuarios:**
- Flyer con QR en sala de espera del INEN
- Recomendación de trabajadoras sociales del hospital (canal de confianza para pacientes)
- Paciente-influencer en comunidades de sobrevivientes de cáncer en redes

**Primeros 1,000 usuarios:**
- Partnership con Liga contra el Cáncer / comunicaciones del INEN
- Nota de prensa en RPP Salud / Infobae Perú (ya cubrieron el problema — la solución es la continuación natural)
- SEO orgánico: búsquedas de alta intención como *"qué documentos llevar al INEN"*, *"módulos del INEN cómo funciona"*

**Primeros contratos institucionales:**
- Presentar directamente al área de admisión del INEN como piloto gratuito (reducción de rechazos = interés alineado)
- EsSalud Prestaciones Oncológicas — propuesta de integración en portal del asegurado

---

## 11. Tracción y Señales Tempranas

| Evidencia | Detalle |
|---|---|
| App en vivo | mediruta.streamlit.app — accesible sin instalación desde el día del deploy |
| 3 usuarios beta | Probaron el MVP y dieron feedback documentado en `docs/research/` |
| Bug de UX detectado y corregido | 2 de 3 usuarios identificaron el mismo problema de layout de forma independiente → corregido en v1.1 |
| 159 médicos verificados | Único directorio médico del INEN con cargos reales y fuente oficial verificable |
| Datos de transparencia | Única app que usa el PDF de Relación de Personal del INEN (Ley N°27806) como fuente |
| Founder es usuaria real | Paciente activa del INEN en observación — usa el producto que construyó |
| Historial de commits | Commits distribuidos durante los 11 días del proyecto (no un solo push el último día) |

---

## 12. Roadmap

| Horizonte | Hito |
|---|---|
| **3 meses** | Integración con registro CMP (número de colegiatura verificado), 1,000 usuarios activos, piloto gratuito con equipo de admisión del INEN |
| **6 meses** | Expansión a IREN Norte y IREN Sur, módulo EsSalud oncología, 5,000 usuarios activos, primer contrato institucional pagado |
| **12 meses** | 5 hospitales integrados, chatbot WhatsApp vía OpenClaw, guía por tipo de seguro (SIS / EsSalud / particular), 20,000 usuarios, seed round |

---

## 13. Riesgos y Mitigación

**Riesgo 1 — Regulatorio**
MINSA podría exigir certificación como dispositivo médico de apoyo clínico o restringir el uso de datos del portal de transparencia.
*Mitigación:* todos los datos provienen de la Ley N°27806 (mandato de transparencia pública). La app es herramienta orientativa, no diagnóstico médico — el disclaimer es explícito y visible en cada sesión. No almacenamos datos de pacientes.

**Riesgo 2 — Técnico (costos de API)**
A escala, los costos de Claude API crecen con el número de usuarios. A 10,000 queries/día = ~$8/día = ~$240/mes.
*Mitigación:* el clasificador híbrido resuelve el 80% de consultas con prefijos CIE-10 y keywords sin llamar a la API. Claude se invoca solo para fallback y generación de estudios. La arquitectura está diseñada para minimizar tokens por query.

**Riesgo 3 — Adopción institucional lenta**
Los hospitales públicos peruanos tienen procesos de compra B2G que pueden tomar 12–24 meses.
*Mitigación:* la app funciona y genera valor sin integración institucional. El B2C gratuito construye tracción y prueba de concepto. El contrato institucional es el objetivo de monetización, no el prerequisito para existir.

---

## 14. The Ask

> "Si tuviera 30 segundos con un inversionista de YC:"

**Pedimos S/30,000 (~$8,000 USD) para 6 meses de runway.**

| Destino | Monto |
|---|---|
| Costos API Claude a 10,000 usuarios activos/mes | S/10,000 |
| Revisión legal del modelo de datos y disclaimer médico | S/8,000 |
| Desarrollo del módulo de integración institucional (API) | S/8,000 |
| Operaciones y hosting (6 meses) | S/4,000 |

**Milestone que desbloquea esta inversión:**
10,000 usuarios activos verificados + 1 contrato institucional firmado con INEN o EsSalud → base para un seed de S/150,000 con UTEC Ventures, Wayra o NXTP.

---

*Repositorio: github.com/evsarmientov/DataScience_FinalProject*
*Demo: mediruta.streamlit.app*
*Evelyn Valeria Sarmiento Vasquez — ev.sarmientov@alum.up.edu.pe*
