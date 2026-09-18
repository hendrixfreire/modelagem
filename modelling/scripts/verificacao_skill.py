#!/usr/bin/env python3
"""Verificação estática da skill modelling (estrutura, gates, templates)."""
import json
import re
from pathlib import Path

p = Path(__file__).resolve().parent.parent
docs = {str(f.relative_to(p)): f.read_text() for f in p.rglob("*.md")}
main = docs["SKILL.md"]
flow = docs["references/fluxo.md"]
ck = docs["references/checklist.md"]

fases = [f"F{i:02d}" for i in range(1, 6)]
assert re.findall(r"^## (F\d{2}) —", flow, re.M) == fases, "fases do fluxo"
assert re.findall(r"^## (F\d{2}) —", ck, re.M) == fases, "fases do checklist"
for i in range(1, 6):
    g = f"G{i:02d}"
    assert g in flow and g in ck and g in main, f"gate {g} ausente"
for nome, t in docs.items():
    assert "G06" not in t and "G07" not in t, f"resíduo de gate antigo em {nome}"
for tpl in ["MODEL_SPECS.md", "GLOSSARIO.md", "CONTEXT.md"]:
    assert (p / "templates" / tpl).is_file(), tpl
for script in ["bq_leitura.py", "ptax_media.py", "custo.py",
               "auditoria.py", "tamanhos.py"]:
    assert (p / "scripts" / script).is_file(), script
assert "templates/" in main and "scripts/" in main
assert "cambio_congelado" in main and "cambio_congelado" in flow
assert "cambio_congelado" in docs["references/custos-bigquery.md"]
secao_ctrl = main.split("## Controle do processo")[1][:700]
assert "MODEL_SPECS.md" in secao_ctrl, "retomada não orientada"
assert not list(p.rglob("*.sql"))
total = (sum(len(t) for t in docs.values())
         + sum(len(f.read_text()) for f in p.rglob("*.py"))
         + sum(len(f.read_text()) for f in (p / "templates").rglob("*.md")))
print(json.dumps({
    "verificacao": "ok",
    "fases": fases,
    "gates": [f"G0{i}" for i in range(1, 6)],
    "templates": 3,
    "scripts": 5,
    "caracteres_totais": total,
    "bigquery_executado": False,
}, ensure_ascii=False, indent=2))
