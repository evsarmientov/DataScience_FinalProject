"""
Motor de especialidad para INEN.

Dado un diagnostico en texto libre (y opcionalmente un codigo CIE-10),
determina a que modulo del INEN debe ir el paciente.

Estrategia en dos capas:
  1. Coincidencia por palabras clave y prefijos CIE-10 (rapido, sin API).
  2. Si no hay coincidencia clara, Claude clasifica el texto libre (maneja
     formulaciones raras, abreviaciones medicas, etc.).
"""
import json
import os
import re
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "data" / "inen_modulos.json"


def _cargar_datos() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _modulos() -> list[dict]:
    return _cargar_datos()["modulos"]


# ---------------------------------------------------------------------------
# Capa 1: reglas
# ---------------------------------------------------------------------------

def _score_por_keywords(diagnostico_lower: str, modulo: dict) -> int:
    return sum(
        1 for kw in modulo.get("palabras_clave", [])
        if kw.lower() in diagnostico_lower
    )


def _match_por_cie10(cie10: str, modulo: dict) -> bool:
    cie10_clean = cie10.strip().upper()
    return any(cie10_clean.startswith(p) for p in modulo.get("cie10_prefijos", []))


def clasificar_por_reglas(diagnostico: str, cie10: str | None = None) -> dict | None:
    """
    Devuelve el modulo mas probable usando reglas deterministicas, o None si
    no hay coincidencia suficientemente clara.
    """
    modulos = _modulos()
    diagnostico_lower = diagnostico.lower()

    # CIE-10 tiene prioridad (es un codigo estructurado, alta precision)
    if cie10:
        for m in modulos:
            if _match_por_cie10(cie10, m):
                return {**m, "confianza": "alta", "metodo": "CIE-10"}

    # Keywords: ganador es el modulo con mas coincidencias
    scores = [
        (_score_por_keywords(diagnostico_lower, m), m)
        for m in modulos
    ]
    scores.sort(key=lambda x: -x[0])
    mejor_score, mejor_modulo = scores[0]

    # Solo aceptamos si hay al menos 1 keyword y el segundo lugar esta a
    # distancia (evitar falsos positivos por coincidencias parciales)
    segundo_score = scores[1][0] if len(scores) > 1 else 0
    if mejor_score >= 1 and mejor_score > segundo_score:
        return {**mejor_modulo, "confianza": "alta", "metodo": "keywords"}
    if mejor_score >= 2:  # empate con 2+ coincidencias en ambos: tomar el primero
        return {**mejor_modulo, "confianza": "media", "metodo": "keywords"}

    return None


# ---------------------------------------------------------------------------
# Capa 2: Claude API como fallback
# ---------------------------------------------------------------------------

def clasificar_con_claude(diagnostico: str, cie10: str | None = None) -> dict:
    """
    Usa Claude para clasificar diagnosticos que no matchean por reglas.
    Requiere ANTHROPIC_API_KEY en el entorno.
    """
    import anthropic

    modulos = _modulos()
    lista_modulos = "\n".join(
        f"  Modulo {m['id']}: {m['nombre']} — {m['descripcion']}"
        for m in modulos
    )

    user_content = f"Diagnostico: {diagnostico}"
    if cie10:
        user_content += f"\nCodigo CIE-10: {cie10}"

    prompt = f"""Eres el sistema de orientacion del INEN (Instituto Nacional de Enfermedades Neoplasicas, Lima, Peru).
Tu tarea es determinar a que modulo del INEN debe ir este paciente basandote en su diagnostico.

{user_content}

Modulos disponibles:
{lista_modulos}

Responde UNICAMENTE con un JSON valido con este formato (sin texto extra):
{{"modulo_id": "X", "confianza": "alta|media|baja", "razon": "una linea explicando la clasificacion"}}

Si el diagnostico es demasiado vago para clasificar, usa modulo_id "0" con confianza "baja"."""

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    mensaje = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    texto = mensaje.content[0].text.strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            resultado = json.loads(match.group())
            modulo_id = str(resultado.get("modulo_id", "0"))
            modulo = next((m for m in modulos if m["id"] == modulo_id), modulos[0])
            return {
                **modulo,
                "confianza": resultado.get("confianza", "media"),
                "razon": resultado.get("razon", ""),
                "metodo": "Claude API",
            }
        except (json.JSONDecodeError, KeyError):
            pass

    # Si Claude devuelve algo inesperado, fallback a modulo 0
    return {**modulos[0], "confianza": "baja", "razon": "respuesta inesperada de Claude", "metodo": "fallback"}


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def clasificar(diagnostico: str, cie10: str | None = None) -> dict:
    """
    Clasifica el diagnostico y devuelve un dict con:
      - id, nombre, descripcion, medicos_especialidad (del JSON)
      - confianza: 'alta' | 'media' | 'baja'
      - metodo: 'CIE-10' | 'keywords' | 'Claude API' | 'fallback'
      - razon: texto explicativo (solo si vino de Claude)
    """
    resultado = clasificar_por_reglas(diagnostico, cie10)
    if resultado:
        return resultado

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            return clasificar_con_claude(diagnostico, cie10)
        except Exception as e:  # red, cuota, etc.
            pass

    modulos = _modulos()
    return {
        **modulos[0],
        "confianza": "baja",
        "metodo": "fallback",
        "razon": "No se pudo clasificar — ir a admision general (Modulo 0) para orientacion.",
    }


# ---------------------------------------------------------------------------
# CLI de prueba rapida
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    casos = [
        ("Cancer de cuello uterino estadio IIA", "C53"),
        ("Adenocarcinoma gastrico antral", None),
        ("Linfoma no Hodgkin difuso de celulas B grandes", "C83"),
        ("Cancer de pulmon de celulas no pequenas", "C34"),
        ("Masa en mama derecha pendiente de biopsia", None),
        ("Diagnostico no especificado, referido por medico general", None),
    ]
    for diag, cie in casos:
        r = clasificar(diag, cie)
        print(f"\nDiagnostico: {diag}")
        print(f"  -> {r['nombre']}  [confianza={r['confianza']}, metodo={r['metodo']}]")
