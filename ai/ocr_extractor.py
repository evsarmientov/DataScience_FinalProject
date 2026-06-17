"""
Extractor OCR para hojas de referencia medica.

Usa Claude vision (multimodal) para leer una imagen (foto de la hoja de
referencia o informe medico) y extraer el diagnostico y el codigo CIE-10.

Formatos soportados: JPEG, PNG, GIF, WEBP (los que acepta la API de Anthropic).
"""
import base64
import json
import os
import re


PROMPT_EXTRACCION = """Eres un asistente medico especializado en documentacion clinica peruana.
Analiza esta imagen de una hoja de referencia o informe medico y extrae:

1. diagnostico: el diagnostico principal (texto tal como aparece en el documento)
2. cie10: el codigo CIE-10 (ej: C53.0, K25, etc.) si aparece en el documento; null si no
3. paciente: nombre del paciente si aparece; null si no
4. medico_origen: nombre o especialidad del medico que firma la referencia; null si no

Responde UNICAMENTE con un JSON valido, sin texto adicional:
{"diagnostico": "...", "cie10": "...", "paciente": "...", "medico_origen": "..."}

Si no puedes leer el documento o la imagen no es un documento medico, usa:
{"diagnostico": null, "cie10": null, "paciente": null, "medico_origen": null}"""


def _mime_desde_bytes(datos: bytes) -> str:
    """Detecta el MIME type por los magic bytes del archivo."""
    if datos[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if datos[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if datos[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if datos[:4] == b"RIFF" and datos[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"  # asumir JPEG por defecto


def extraer_diagnostico(imagen_bytes: bytes, mime_type: str | None = None) -> dict:
    """
    Recibe los bytes de una imagen y devuelve:
      {"diagnostico": str|None, "cie10": str|None, "paciente": str|None, "medico_origen": str|None}

    Requiere ANTHROPIC_API_KEY en el entorno.
    Lanza RuntimeError si no hay API key.
    """
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no esta configurada en las variables de entorno.")

    if mime_type is None:
        mime_type = _mime_desde_bytes(imagen_bytes)

    imagen_b64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")

    client = anthropic.Anthropic(api_key=api_key)
    mensaje = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": imagen_b64,
                        },
                    },
                    {"type": "text", "text": PROMPT_EXTRACCION},
                ],
            }
        ],
    )

    texto = mensaje.content[0].text.strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"diagnostico": None, "cie10": None, "paciente": None, "medico_origen": None}
