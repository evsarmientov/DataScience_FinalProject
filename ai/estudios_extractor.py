"""
Extractor de estudios clinicos previos requeridos para primera consulta en INEN.

Dado un diagnostico especifico y el modulo asignado, devuelve qué estudios
(imagenes, biopsias, laboratorio) el paciente deberia tener ya hechos o pedir
antes de ir al especialista.

Estrategia:
  1. Lookup estatico por modulo (siempre disponible, respuesta inmediata).
  2. Claude refina la lista para el diagnostico especifico (mas preciso, requiere API key).
"""
import json
import os
import re
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "data" / "estudios_por_modulo.json"

_CATEGORIAS = {
    "imagen":     "Imágenes (TAC / Ecografía / RX / RMN / PET)",
    "patologia":  "Patología (Biopsia / Histología / PAP)",
    "laboratorio":"Laboratorio (Hemograma / Marcadores tumorales)",
    "otros":      "Otros procedimientos (Endoscopía / Colonoscopía)",
}


def _cargar_base() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["por_modulo"]


def estudios_por_modulo(modulo_id: str) -> dict:
    """
    Fallback: lista generica por modulo, sin IA.
    Devuelve {"imagen": [...], "patologia": [...], "laboratorio": [...], "otros": [...], "nota": "..."}
    """
    base = _cargar_base()
    return base.get(str(modulo_id), base["0"])


def estudios_con_claude(diagnostico: str, modulo_id: str, modulo_nombre: str) -> dict | None:
    """
    Pide a Claude una lista especifica para este diagnostico y modulo.
    Devuelve None si no hay API key o si Claude falla.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    import anthropic

    prompt = f"""Eres un oncólogo orientador del INEN (Instituto Nacional de Enfermedades Neoplásicas, Lima, Perú).

Un paciente con el siguiente diagnóstico viene a su PRIMERA consulta de especialidad:

Diagnóstico: {diagnostico}
Módulo INEN: {modulo_nombre}

¿Qué estudios/exámenes debería traer ya realizados (o solicitarlos antes de ir) para aprovechar al máximo la primera consulta con el especialista?

Clasifica en estas 4 categorías y sé específico al diagnóstico (no genérico):
- imagen: TAC, ecografía, RX, RMN, PET, etc.
- patologia: biopsia, histología, inmunohistoquímica, PAP, etc.
- laboratorio: hemograma, marcadores tumorales, perfil bioquímico, etc.
- otros: endoscopía, colonoscopía, laringoscopía, etc. (solo si aplica)

Responde ÚNICAMENTE con un JSON válido, sin texto adicional:
{{"imagen": [...], "patologia": [...], "laboratorio": [...], "otros": [...], "nota": "una sola línea de consejo clave para este diagnóstico específico"}}

Si una categoría no aplica, deja lista vacía []. Máximo 4-5 items por categoría. Usa nombres que un paciente no-médico pueda entender (ej: "Tomografía de tórax con contraste" en vez de "TAC torácica trifásica")."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        mensaje = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = mensaje.content[0].text.strip()
        match = re.search(r"\{.*\}", texto, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return None


def obtener_estudios(diagnostico: str, modulo_id: str, modulo_nombre: str) -> dict:
    """
    Punto de entrada principal.
    Intenta Claude primero; si no hay API key o falla, usa lookup estatico.
    Siempre devuelve: {"imagen": [...], "patologia": [...], "laboratorio": [...],
                       "otros": [...], "nota": str, "fuente": "claude"|"base"}
    """
    resultado = estudios_con_claude(diagnostico, modulo_id, modulo_nombre)
    if resultado:
        return {**resultado, "fuente": "claude"}

    base = estudios_por_modulo(modulo_id)
    return {**base, "fuente": "base"}


CATEGORIAS_LABEL = _CATEGORIAS
