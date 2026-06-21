"""
Scraper de médicos staff del INEN.

Fuente: Portal de Transparencia del INEN (Ley N° 27806)
  Relación de Personal Nombrado — publicación oficial semestral.
  URL: portal.inen.sld.pe/informacion-de-personal/

El PDF tiene tablas con 7 columnas detectadas automáticamente por pdfplumber:
  N° | APELLIDOS Y NOMBRES | DNI | CONDICIÓN LABORAL | CARGO | AREA | DEPENDENCIA INTERNA

Filtramos CARGO que contenga "MEDICO" (excluyendo "TECNOLOGO MEDICO" y similares)
y mapeamos AREA + DEPENDENCIA al módulo INEN correspondiente.

Uso:
    python backend/app/scraping/medicos_scraper.py

Guarda los resultados en data/medicos_inen.json.
"""
import io
import json
import re
from pathlib import Path

import pdfplumber
import requests

URL_PDF = "https://portal.inen.sld.pe/wp-content/uploads/2023/08/Relacion-de-Personal-Nombrado.pdf"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MediRutaBot/0.1)"}

AREA_A_MODULO = {
    "cabeza": "1", "cuello": "1", "torax": "1", "tórax": "1",
    "pulmon": "1", "pulmón": "1", "tiroides": "1", "laringe": "1",
    "mama": "2", "ginecol": "2", "mastol": "2",
    "abdomen": "3", "gastro": "3", "digestivo": "3",
    "higado": "3", "hígado": "3", "pancreas": "3", "páncreas": "3",
    "colon": "3", "recto": "3",
    "hemato": "4", "linfoma": "4", "sarcoma": "4",
    "urolog": "4", "prostata": "4", "próstata": "4",
    "dermato": "4", "nervioso": "4", "cerebro": "4", "pediatr": "4",
}

MODULO_NOMBRES = {
    "0": "Módulo 0 — Orientación y Admisión",
    "1": "Módulo 1 — Tumores de Cabeza, Cuello y Tórax",
    "2": "Módulo 2 — Ginecología y Mama",
    "3": "Módulo 3 — Tumores Abdominales",
    "4": "Módulo 4 — Hematología, Urología y Otros",
}


def _normalizar(texto: str | None) -> str:
    if not texto:
        return ""
    return re.sub(r"\s+", " ", texto.replace("\n", " ")).strip()


def _capitalizar(s: str) -> str:
    minusculas = {"de", "del", "la", "las", "los", "y", "e", "en", "a"}
    partes = s.strip().split()
    return " ".join(
        p.capitalize() if (i == 0 or p.lower() not in minusculas) else p.lower()
        for i, p in enumerate(partes)
    )


def _inferir_modulo(area: str, dep: str) -> str:
    texto = (area + " " + dep).lower()
    for kw, mod in AREA_A_MODULO.items():
        if kw in texto:
            return mod
    return "0"


def _es_medico_valido(cargo: str) -> bool:
    c = cargo.lower()
    es_medico = "medico" in c or "médico" in c
    es_excluido = any(x in c for x in ["tecnologo", "tecnólogo", "biologo", "farmac"])
    return es_medico and not es_excluido


def extraer_medicos_pdf(verbose: bool = True) -> list[dict]:
    if verbose:
        print("Descargando PDF de transparencia INEN...")
    r = requests.get(URL_PDF, headers=HEADERS, timeout=30)
    r.raise_for_status()
    if verbose:
        print(f"  {len(r.content) // 1024} KB — OK")

    medicos: list[dict] = []
    vistos: set[str] = set()

    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        if verbose:
            print(f"  {len(pdf.pages)} páginas")

        for page in pdf.pages:
            tabla = page.extract_table()
            if not tabla:
                continue

            for fila in tabla:
                # Cada fila tiene exactamente 7 columnas (pueden ser None)
                if len(fila) < 7:
                    continue

                cargo_raw = _normalizar(fila[4])
                if not _es_medico_valido(cargo_raw):
                    continue

                nombre_raw = _normalizar(fila[1])
                if not nombre_raw or len(nombre_raw) < 5:
                    continue
                # Saltar encabezado
                if re.match(r"^(APELLIDO|NOMBRE|N°)", nombre_raw, re.I):
                    continue

                nombre_key = nombre_raw.upper()
                if nombre_key in vistos:
                    continue
                vistos.add(nombre_key)

                area = _normalizar(fila[5])
                dep  = _normalizar(fila[6])
                modulo = _inferir_modulo(area, dep)

                medicos.append({
                    "id": str(len(medicos) + 1).zfill(3),
                    "nombre": _capitalizar(nombre_raw),
                    "dni": _normalizar(fila[2]) or None,
                    "cmp": None,
                    "condicion_laboral": _normalizar(fila[3]),
                    "cargo": _capitalizar(cargo_raw),
                    "area": _capitalizar(area) if area else "INEN",
                    "dependencia": _capitalizar(dep) if dep else "",
                    "modulo_inen": modulo,
                    "modulo_nombre": MODULO_NOMBRES.get(modulo, ""),
                    "clinicas_privadas": [],
                    "horario_inen": "Consultar en admisión INEN",
                    "_fuente": URL_PDF,
                })

    if verbose:
        print(f"\n  Médicos extraídos: {len(medicos)}")
    return medicos


def guardar(medicos: list[dict], verbose: bool = True):
    out_path = Path(__file__).parent.parent.parent.parent / "data" / "medicos_inen.json"
    data = {
        "_nota": "Datos extraídos del Portal de Transparencia del INEN (Ley N°27806). Solo personal con cargo MEDICO ESPECIALISTA / MEDICO. Fuente pública oficial.",
        "_fuente": URL_PDF,
        "_actualizacion": "2023 (Relación de Personal Nombrado — INEN)",
        "medicos": medicos,
    }
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if verbose:
        print(f"Guardado en {out_path} ({len(medicos)} médicos)")


if __name__ == "__main__":
    medicos = extraer_medicos_pdf(verbose=True)
    if medicos:
        print("\nMuestra (primeros 20 médicos):")
        for m in medicos[:20]:
            print(f"  {m['nombre'][:42]:<42} | {m['area'][:32]:<32} | mod {m['modulo_inen']}")
        guardar(medicos)
    else:
        print("No se extrajeron médicos.")
