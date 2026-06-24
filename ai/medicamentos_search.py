import os
import json
from anthropic import Anthropic

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client

def extraer_medicamento_receta(imagen_bytes: bytes) -> str:
    """OCR de receta médica — devuelve el nombre del medicamento principal."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return ""
    import base64
    img_b64 = base64.standard_b64encode(imagen_bytes).decode()
    prompt = (
        "Esta es una foto de una receta médica peruana. "
        "Extrae el nombre del medicamento principal (solo el nombre genérico o comercial, sin dosis ni instrucciones). "
        "Si hay varios medicamentos, elige el primero. Responde SOLO con el nombre del medicamento, sin explicación."
    )
    try:
        resp = _get_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=60,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        return resp.content[0].text.strip()
    except Exception:
        return ""

def buscar_disponibilidad(nombre: str) -> dict:
    """Consulta disponibilidad del medicamento en el sistema público peruano vía Claude."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {}

    prompt = f"""Eres un asistente especializado en el sistema de salud peruano.

El paciente busca información sobre el medicamento: {nombre}

Basándote en el Petitorio Nacional Único de Medicamentos Esenciales (PNUME) del Ministerio de Salud del Perú y el conocimiento del sistema de salud público peruano, responde con JSON:
{{
  "nombre_generico": "nombre genérico del medicamento",
  "en_pnume": true o false,
  "disponibilidad_sis": "Cubierto" | "Parcialmente cubierto" | "No cubierto" | "Consultar en farmacia SIS",
  "disponibilidad_essalud": "Cubierto" | "Parcialmente cubierto" | "No cubierto" | "Consultar en farmacia EsSalud",
  "nota": "una línea de contexto útil para el paciente peruano"
}}

Si no tienes certeza, usa "Consultar en farmacia SIS" o "Consultar en farmacia EsSalud".
Responde SOLO con JSON válido, sin texto adicional."""

    try:
        resp = _get_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return {}
