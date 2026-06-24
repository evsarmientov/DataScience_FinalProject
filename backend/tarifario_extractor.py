"""
Extrae el Tarifario Institucional INEN 2024 (PDF escaneado) usando Claude Vision.
Produce data/tarifario_inen_2024.json con una lista de procedimientos y tarifas.

Columnas del tarifario:
  codigo_inen, cpms_minsa, cpt_sis, descripcion,
  tarifa_referencial, tpu, tarifa_sis, hospitalario,
  essalud_ffaa_pnp, privado_iafa
"""

import os
import sys
import json
import base64
import fitz  # PyMuPDF
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic

PDF_PATH = Path(__file__).parent.parent / "docs" / "tarifario_inen_2024.pdf"
OUT_PATH = Path(__file__).parent.parent / "data" / "tarifario_inen_2024.json"

PROMPT = """Esta es una página del Tarifario Institucional Integrado del INEN 2024 (Perú).
Extrae TODAS las filas de la tabla de procedimientos médicos que aparezcan en la imagen.

Las columnas son:
1. codigo_inen
2. cpms_minsa
3. cpt_sis
4. descripcion
5. tarifa_referencial (TR)
6. tpu
7. tarifa_sis
8. hospitalario
9. essalud_ffaa_pnp
10. privado_iafa

Responde SOLO con un JSON válido de esta forma:
{
  "especialidad": "nombre de la especialidad/sección si aparece como encabezado, sino null",
  "procedimientos": [
    {
      "codigo_inen": "...",
      "cpms_minsa": "...",
      "cpt_sis": "...",
      "descripcion": "...",
      "tarifa_referencial": "...",
      "tpu": "...",
      "tarifa_sis": "...",
      "hospitalario": "...",
      "essalud_ffaa_pnp": "...",
      "privado_iafa": "..."
    }
  ]
}

Si la página no contiene tabla de procedimientos (portada, índice, firmas, texto normativo), responde:
{"especialidad": null, "procedimientos": []}

Usa null para celdas vacías o ilegibles. No omitas filas."""


def page_to_base64(page, dpi: int = 200) -> str:
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img_bytes = pix.tobytes("jpeg")
    return base64.standard_b64encode(img_bytes).decode()


def extract_page(client: Anthropic, img_b64: str, page_num: int) -> dict:
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                    {"type": "text", "text": PROMPT},
                ],
            }],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        # Tomar solo la parte JSON (hasta el primer "}" que cierra el objeto raíz)
        start = text.find("{")
        if start != -1:
            depth = 0
            for idx, ch in enumerate(text[start:], start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        text = text[start:idx + 1]
                        break
        return json.loads(text)
    except Exception as e:
        print(f"  ERROR página {page_num}: {e}", file=sys.stderr)
        return {"especialidad": None, "procedimientos": []}


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no configurado.", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    doc = fitz.open(str(PDF_PATH))
    total = len(doc)
    print(f"PDF: {total} páginas")

    all_procedures = []
    current_especialidad = None

    for i, page in enumerate(doc):
        page_num = i + 1
        print(f"Procesando página {page_num}/{total}...", end=" ", flush=True)
        img_b64 = page_to_base64(page)
        result = extract_page(client, img_b64, page_num)

        if result.get("especialidad"):
            current_especialidad = result["especialidad"]

        procs = result.get("procedimientos", [])
        for p in procs:
            p["especialidad"] = current_especialidad
            p["pagina_pdf"] = page_num

        all_procedures.extend(procs)
        print(f"{len(procs)} procedimientos extraídos")

    doc.close()

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_procedures, f, ensure_ascii=False, indent=2)

    print(f"\nTotal: {len(all_procedures)} procedimientos → {OUT_PATH}")


if __name__ == "__main__":
    main()
