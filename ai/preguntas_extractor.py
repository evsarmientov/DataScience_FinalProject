import os
import json
from anthropic import Anthropic

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client

CATEGORIAS_LABEL = {
    "diagnostico":  "Sobre mi diagnóstico",
    "tratamiento":  "Sobre el tratamiento",
    "proceso_inen": "Sobre el proceso en el INEN",
    "efectos":      "Efectos secundarios y calidad de vida",
    "seguimiento":  "Seguimiento y pronóstico",
}

def obtener_preguntas(diagnostico: str, modulo_nombre: str = "") -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback()

    prompt = f"""Eres un asistente que ayuda a pacientes oncológicos peruanos a prepararse para su primera consulta con el especialista en el INEN.

Diagnóstico del paciente: {diagnostico}
Módulo INEN al que va: {modulo_nombre or "oncología general"}

Genera 3-4 preguntas concretas y simples por categoría. Deben ser preguntas que un paciente real haría, en español sencillo.

Responde SOLO con JSON válido con esta estructura:
{{
  "diagnostico": ["pregunta 1", "pregunta 2", "pregunta 3"],
  "tratamiento": ["pregunta 1", "pregunta 2", "pregunta 3"],
  "proceso_inen": ["pregunta 1", "pregunta 2", "pregunta 3"],
  "efectos": ["pregunta 1", "pregunta 2", "pregunta 3"],
  "seguimiento": ["pregunta 1", "pregunta 2"]
}}"""

    try:
        resp = _get_client().messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return _fallback()

def _fallback() -> dict:
    return {
        "diagnostico": [
            "¿Cuál es exactamente mi diagnóstico y qué significa?",
            "¿En qué etapa o estadio estoy?",
            "¿Qué tan avanzado está y qué implica para mi tratamiento?",
        ],
        "tratamiento": [
            "¿Cuáles son mis opciones de tratamiento?",
            "¿Cuál recomienda y por qué?",
            "¿Cuánto tiempo dura el tratamiento?",
            "¿Puedo seguir trabajando durante el tratamiento?",
        ],
        "proceso_inen": [
            "¿Qué estudios necesito antes de empezar?",
            "¿Con qué frecuencia tendré que venir al INEN?",
            "¿Los medicamentos estarán cubiertos por mi seguro?",
        ],
        "efectos": [
            "¿Qué efectos secundarios puedo esperar?",
            "¿Hay restricciones de alimentación o actividad física?",
            "¿Cómo manejo el dolor o el malestar en casa?",
        ],
        "seguimiento": [
            "¿Cómo sabremos si el tratamiento está funcionando?",
            "¿Con qué frecuencia habrá controles?",
        ],
    }
