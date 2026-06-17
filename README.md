# MédiRuta

> Tu ruta exacta al especialista correcto.

## El problema

Pacientes con sospecha o diagnóstico oncológico (INEN) o que necesitan una especialidad médica
en hospitales públicos (Rebagliati/EsSalud) hacen colas desde las 3am sin saber con certeza:

1. A qué especialidad/módulo deben ir según su diagnóstico.
2. Qué documentos exactos necesitan llevar (y terminan siendo rechazados por falta de uno).

## Qué hace este proyecto (MVP)

- **Identifica la especialidad correcta** a partir del diagnóstico/hoja de referencia del paciente.
- **Dice exactamente qué documentos llevar**, scrapeados directamente de las fuentes oficiales
  (INEN, EsSalud), no inventados.
- Cobertura actual: INEN (admisión general) y Rebagliati (Salud Mental como caso piloto).
  Ampliar a más especialidades de Rebagliati es parte del roadmap (ver sección de Riesgos en
  el pitch deck): no todas las ~93 especialidades tienen su información publicada en un formato
  scrapeable, así que las que no tengan fuente oficial propia usan el requisito general de EsSalud
  (DNI + Hoja de Referencia) marcado explícitamente como "general" y no como "verificado en fuente".

## Founder

TODO: tu nombre, una línea de bio, y por qué tú (founder-market fit: te pasó a ti personalmente).

Como soy solo founder, así cubro los roles clásicos con agentes de IA:
- **Claude** es mi CTO de backend (este README, el scraper, y la corrección de bugs de
  parsing de HTML fueron escritos/depurados con asistencia de Claude).
- TODO: completar a medida que se sumen frontend, OCR, etc.

## Cómo correr el proyecto localmente

```bash
git clone <url-de-este-repo>
cd MédiRuta
pip install -r requirements.txt
cp .env.example .env   # y completa tus claves ahí (nunca subas .env real)
python backend/app/scraping/requisitos_scraper.py
```

## Estructura del repositorio

```
MédiRuta/
├── README.md
├── LICENSE
├── .env.example
├── requirements.txt
├── docs/              # pitch deck, capturas, diagramas, video demo
│   └── research/      # evidencia de validación: entrevistas, encuestas
├── frontend/          # Streamlit (próximamente)
├── backend/
│   ├── app/
│   │   └── scraping/  # requisitos_scraper.py: trae requisitos reales de INEN/EsSalud
│   └── tests/
├── ai/                # prompts, motor de especialidad, agentes
├── data/               # muestras chicas de datos
├── notebooks/          # exploración / EDA
└── .github/workflows/  # CI básico
```

## Herramientas del curso usadas (y dónde)

| Herramienta | Dónde | Por qué |
|---|---|---|
| Web scraping (`requests` + `BeautifulSoup`) | `backend/app/scraping/requisitos_scraper.py` | Trae los requisitos de admisión directamente de las páginas oficiales de INEN y EsSalud, en vez de que el equipo los transcriba a mano (que se desactualiza). |
| TODO: OCR/Claude (document AI) | `backend/app/...` (próximamente) | Extraer diagnóstico y CIE-10 de la hoja de referencia/informe médico que sube el paciente. |
| TODO: Geoespacial (Folium) | `frontend/` (próximamente) | Mostrar el hospital/módulo más cercano al paciente. |

## Stack

- Python 3.11+ / `requests` / `BeautifulSoup4`
- TODO: Streamlit, Claude API, GeoPandas/Folium

## Licencia

MIT — ver [LICENSE](./LICENSE).
