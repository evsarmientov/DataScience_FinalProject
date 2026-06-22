"""
Enriquecedor de directorio médico INEN.

Toma los médicos de data/medicos_inen.json y para cada uno pregunta a Claude
si tiene práctica privada en alguna clínica de Lima.

Solo guarda respuestas de ALTA CONFIANZA — prefiere dejar vacío a inventar.

Uso:
    python ai/enriquecedor_medicos.py

Actualiza data/medicos_inen.json en el lugar (no crea archivo nuevo).
"""
import json
import os
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path(__file__).parent.parent / "data" / "medicos_inen.json"


PROMPT_SISTEMA = """Eres un directorio médico de Perú. Para el médico que te indico, devuelve
lo que sabes con ALTA CONFIANZA sobre tres datos:
1. Su número CMP (Colegio Médico del Perú)
2. Sus clínicas privadas en Lima donde atiende
3. Su formación académica (universidad de medicina, especialidad, subespecialidad, maestría/doctorado)

Responde SOLO con JSON válido, sin texto extra:
{
  "cmp": "12345" o null,
  "clinicas_privadas": ["Clínica Anglo Americana", "Clínica Ricardo Palma"] o [],
  "formacion": "Médico Cirujano UNMSM · Especialista Cirugía Oncológica UNMSM · Fellowship MD Anderson" o null,
  "confianza": "alta" o "baja"
}

REGLAS ESTRICTAS:
- Si no estás seguro de un campo, ese campo va null o [].
- NO inventes datos. Prefiere null a incorrecto.
- "confianza: alta" solo si tienes al menos un dato verificable del médico.
- "confianza: baja" si no reconoces al médico — así no guardamos nada."""


def enriquecer_medico(cliente: anthropic.Anthropic, medico: dict) -> dict:
    nombre = medico["nombre"]
    area = medico.get("area", "")
    dep = medico.get("dependencia", "")
    especialidad = f"{area} / {dep}".strip(" /")

    mensaje = (
        f"Médico: {nombre}\n"
        f"Hospital: INEN (Instituto Nacional de Enfermedades Neoplásicas, Lima, Perú)\n"
        f"Departamento: {especialidad}\n\n"
        "¿Cuál es su CMP, sus clínicas privadas en Lima y su formación académica?"
    )

    try:
        resp = cliente.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=PROMPT_SISTEMA,
            messages=[{"role": "user", "content": mensaje}],
        )
        texto = resp.content[0].text.strip()
        inicio = texto.find("{")
        fin = texto.rfind("}") + 1
        if inicio >= 0 and fin > inicio:
            datos = json.loads(texto[inicio:fin])
            if datos.get("confianza") == "alta":
                return {
                    "cmp": datos.get("cmp"),
                    "clinicas_privadas": datos.get("clinicas_privadas") or [],
                    "formacion": datos.get("formacion"),
                }
    except Exception:
        pass
    return {}


def main(limite: int | None = None, solo_modulos: list[str] | None = None):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no encontrada en .env")
        return

    cliente = anthropic.Anthropic(api_key=api_key)

    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    medicos = data["medicos"]

    # Filtrar por módulo si se especifica
    if solo_modulos:
        candidatos = [m for m in medicos if m["modulo_inen"] in solo_modulos]
    else:
        candidatos = medicos

    if limite:
        candidatos = candidatos[:limite]

    print(f"Enriqueciendo {len(candidatos)} médicos...")
    enriquecidos = 0

    for i, medico in enumerate(candidatos):
        # Saltar si ya tiene datos de una corrida anterior
        if medico.get("cmp") or medico.get("clinicas_privadas"):
            continue

        extra = enriquecer_medico(cliente, medico)
        if extra:
            idx_original = next(
                j for j, m in enumerate(medicos) if m["id"] == medico["id"]
            )
            if extra.get("cmp"):
                medicos[idx_original]["cmp"] = extra["cmp"]
            if extra.get("clinicas_privadas"):
                medicos[idx_original]["clinicas_privadas"] = extra["clinicas_privadas"]
            if extra.get("formacion"):
                medicos[idx_original]["formacion"] = extra["formacion"]
            enriquecidos += 1
            print(f"  [{i+1}/{len(candidatos)}] {medico['nombre'][:40]}")
            print(f"    CMP: {extra.get('cmp')} | Clínicas: {extra.get('clinicas_privadas')} | Formación: {str(extra.get('formacion',''))[:60]}")
        else:
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(candidatos)}] procesados...")

        # Pausa para no saturar la API
        time.sleep(0.3)

    # Guardar resultado
    data["medicos"] = medicos
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo: {enriquecidos} médicos enriquecidos de {len(candidatos)} procesados.")
    print(f"Guardado en {DATA_PATH}")


if __name__ == "__main__":
    import sys
    # Argumentos opcionales: --modulos 1,2,3,4  --limite 50
    args = sys.argv[1:]
    solo_modulos = None
    limite = None
    for i, a in enumerate(args):
        if a == "--modulos" and i + 1 < len(args):
            solo_modulos = args[i + 1].split(",")
        if a == "--limite" and i + 1 < len(args):
            limite = int(args[i + 1])

    # Por defecto: solo módulos 1-4 (los clínicamente relevantes)
    # Los de módulo 0 (radiodiagnóstico, anestesia, etc.) rara vez tienen clínica oncológica
    if solo_modulos is None:
        solo_modulos = ["1", "2", "3", "4"]

    main(limite=limite, solo_modulos=solo_modulos)
