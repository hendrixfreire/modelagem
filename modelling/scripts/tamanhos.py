#!/usr/bin/env python3
"""Inventário de tamanho de tabelas BigQuery via __TABLES__ ou TABLE_STORAGE.

Uso:
  python3 tamanhos.py --projeto PROJETO --dataset DATASET \
      --tabelas t1,t2 --regiao US [--detalhado]

Sem --detalhado, usa __TABLES__ (linhas e size_bytes, barato).
Com --detalhado, usa INFORMATION_SCHEMA.TABLE_STORAGE (metadados,
pode processar bytes; declare o limite ao usuário).
"""
import argparse
import json
import subprocess
import sys
from decimal import Decimal


def bq_json(sql: str, projeto: str, regiao: str, limite: int) -> dict:
    cmd = ["bq", "query", "--headless", "--use_legacy_sql=false",
           f"--project_id={projeto}", f"--location={regiao}",
           f"--maximum_bytes_billed={limite}", "--format=prettyjson", sql]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Erro no bq:\n{r.stderr[-2000:]}")
    return json.loads(r.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--tabelas", required=True, help="lista separada por vírgula")
    ap.add_argument("--regiao", default="US")
    ap.add_argument("--limite-bytes", type=int, required=True)
    ap.add_argument("--detalhado", action="store_true")
    args = ap.parse_args()

    tabelas = [t.strip() for t in args.tabelas.split(",") if t.strip()]
    lista = ", ".join(f"'{t}'" for t in tabelas)

    if args.detalhado:
        sql = f"""
SELECT table_id,
       storage_information.total_logical_bytes AS bytes_logicos,
       storage_information.total_physical_bytes AS bytes_fisicos,
       storage_information.active_logical_bytes AS ativo_logico,
       storage_information.long_term_logical_bytes AS longa_logico,
       storage_information.last_updated_time AS atualizado
FROM `{args.projeto}.{args.regiao}.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE dataset_id = '{args.dataset}' AND table_id IN ({lista})
ORDER BY table_id"""
    else:
        sql = f"""
SELECT table_id, row_count, size_bytes, last_modified_time
FROM `{args.projeto}.{args.dataset}.__TABLES__`
WHERE table_id IN ({lista})
ORDER BY table_id"""

    dados = bq_json(sql, args.projeto, args.regiao, args.limite_bytes)
    linhas = dados.get("rows", [])
    saida = {"projeto": args.projeto, "dataset": args.dataset,
             "regiao": args.regiao, "modo": "detalhado" if args.detalhado
             else "basico", "tabelas": []}
    for row in linhas:
        f = row.get("f", [])
        item = {"tabela": f[0].get("v") if f else None}
        if args.detalhado and len(f) >= 6:
            item.update({
                "bytes_logicos": f[1].get("v"),
                "bytes_fisicos": f[2].get("v"),
                "ativo_logico": f[3].get("v"),
                "longa_logico": f[4].get("v"),
                "atualizado": f[5].get("v"),
                "gib_logicos": str(Decimal(f[1].get("v") or 0) / Decimal(2 ** 30)),
            })
        elif len(f) >= 4:
            item.update({
                "linhas": f[1].get("v"),
                "size_bytes": f[2].get("v"),
                "gib": str(Decimal(f[2].get("v") or 0) / Decimal(2 ** 30)),
                "ultima_modificacao": f[3].get("v"),
            })
        saida["tabelas"].append(item)

    from datetime import datetime, timezone
    saida["momento_consulta"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(saida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
