import os, json, base64, fitz
from dotenv import load_dotenv
load_dotenv()
from anthropic import Anthropic
from pathlib import Path

PDF_PATH = Path(__file__).parent.parent / "docs" / "tarifario_inen_2024.pdf"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT = (
    "Esta es una página del Tarifario Institucional Integrado del INEN 2024 (Perú). "
    "Extrae TODAS las filas de la tabla de procedimientos médicos que aparezcan. "
    "Columnas: codigo_inen, cpms_minsa, cpt_sis, descripcion, tarifa_referencial, "
    "tpu, tarifa_sis, hospitalario, essalud_ffaa_pnp, privado_iafa. "
    'Responde SOLO con JSON: {"especialidad": "...", "procedimientos": [...]}. '
    'Si no hay tabla: {"especialidad": null, "procedimientos": []}'
)

doc = fitz.open(str(PDF_PATH))
print(f"Total páginas: {len(doc)}")

for i in [5, 6, 7]:
    page = doc[i]
    mat = fitz.Matrix(200 / 72, 200 / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img_b64 = base64.standard_b64encode(pix.tobytes("jpeg")).decode()

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
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
    try:
        data = json.loads(text)
        procs = data.get("procedimientos", [])
        print(f"Página {i+1}: especialidad={data.get('especialidad')!r}, procedimientos={len(procs)}")
        if procs:
            print("  Ejemplo:", json.dumps(procs[0], ensure_ascii=False))
    except Exception as e:
        print(f"Página {i+1} ERROR parse: {e}")
        print("  Raw:", text[:400])

doc.close()
