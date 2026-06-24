import json
from pathlib import Path

with open(Path(__file__).parent.parent / "data" / "tarifario_inen_2024.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total: {len(data)} procedimientos")

for q in ["biopsia", "tomografia", "quimio", "cirugia"]:
    count = sum(1 for p in data if q in (p.get("descripcion") or "").lower())
    print(f'"{q}": {count} resultados')

print()
print("Ejemplo biopsia:")
for r in [p for p in data if "biopsia" in (p.get("descripcion") or "").lower()][:3]:
    print(f"  {r['descripcion']}")
    print(f"    SIS: S/{r['tarifa_sis']}  |  EsSalud: S/{r['essalud_ffaa_pnp']}  |  Privado: S/{r['privado_iafa']}")
