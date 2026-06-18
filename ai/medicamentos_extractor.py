"""
Extractor de medicamentos para un diagnostico oncologico dado.

Usa Claude para generar una lista orientativa de medicamentos de primera y segunda
linea, su disponibilidad en el sistema publico peruano (ESSALUD/SIS/MINSA) y
observaciones clave para el paciente.

Nota: la informacion es ORIENTATIVA. El oncólogo tratante define el esquema real.
"""
import json
import os
import re


PROMPT_MEDICAMENTOS = """Eres un farmacólogo oncólogo orientador del sistema de salud peruano.

Un paciente peruano tiene el siguiente diagnóstico:
Diagnóstico: {diagnostico}
Módulo INEN asignado: {modulo_nombre}

Proporciona información ORIENTATIVA sobre los medicamentos que el oncólogo podría indicar.
El objetivo es que el paciente llegue informado a su consulta, no que se automedique.

Clasifica en:
- primera_linea: medicamentos estándar de primera elección (nombres genéricos)
- segunda_linea: alternativas o segunda línea si hay resistencia/intolerancia
- soporte: medicamentos de soporte (antieméticos, analgésicos, factores de crecimiento, etc.)
- disponibilidad_publica: si estos medicamentos están en el petitorio de ESSALUD/SIS/MINSA ("Sí", "Parcial", "No — solo privado")
- costo_referencial: rango de costo mensual aproximado en Perú si es particular (ej: "S/ 200 – 500 / mes")
- nota_paciente: UNA sola oración de consejo clave para el paciente sobre sus medicamentos

Responde ÚNICAMENTE con JSON válido:
{{
  "primera_linea": ["nombre genérico 1 — breve indicación", ...],
  "segunda_linea": ["...", ...],
  "soporte": ["...", ...],
  "disponibilidad_publica": "Sí / Parcial / No",
  "costo_referencial": "S/ X – Y / mes (si es particular)",
  "nota_paciente": "..."
}}

Si la información no es concluyente para este diagnóstico, usa listas vacías y explica en nota_paciente.
Máximo 4 items por lista. Usa nombres genéricos (no marcas comerciales)."""


def obtener_medicamentos(diagnostico: str, modulo_nombre: str) -> dict | None:
    """
    Devuelve informacion de medicamentos via Claude, o None si no hay API key.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    import anthropic

    prompt = PROMPT_MEDICAMENTOS.format(
        diagnostico=diagnostico,
        modulo_nombre=modulo_nombre,
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        mensaje = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = mensaje.content[0].text.strip()
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return None
