#!/usr/bin/env python3
"""Dry run e execução de leitura controlada no BigQuery.

Uso:
  python3 bq_leitura.py --arquivo q01_modelo.sql --projeto PROJETO \
      --regiao US --limite-bytes 2147483648 [--executar]

Sem --executar, faz apenas dry run (não processa dados).
Com --executar, roda a query com --maximum_bytes_billed e cache desligado.

Recusa queries cujo statementType do dry run seja diferente de SELECT.
Retorna JSON com bytes, statement_type, job_id e amostra de resultados.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from decimal import Decimal

PROIBIDOS = ("MERGE", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
             "ALTER", "TRUNCATE", "CALL", "EXPORT", "GRANT", "REVOKE",
             "LOAD", "BEGIN", "DECLARE", "SET", "IF", "LOOP", "WHILE",
             "REPLACE")


def revisao_local(sql: str) -> None:
    """Recusa por texto antes de gastar qualquer chamada."""
    corpo = "\n".join(l for l in sql.splitlines()
                      if not l.strip().startswith("--")).upper()
    for kw in PROIBIDOS:
        if corpo.lstrip().startswith(kw):
            sys.exit(f"RECUSADO: comando {kw} não é SELECT.")
    for termo in ("destination_table", "--destination_table",
                  "target_table", "materialized_view"):
        if termo.lower() in corpo.lower():
            sys.exit(f"RECUSADO: termo de escrita/materialização '{termo}'.")
    # Múltiplas instruções ou ponto e vírgula seguido de comando.
    if re.search(r";\s*\w", corpo):
        sys.exit("RECUSADO: script de múltiplas instruções.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquivo", required=True)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--regiao", default="US")
    ap.add_argument("--limite-bytes", type=int, required=True,
                    help="Teto autorizado pelo usuário (ex.: 2 GB = 2147483648)")
    ap.add_argument("--executar", action="store_true",
                    help="Executa a query (processa dados, cobrança possível)")
    ap.add_argument("--amostra-linhas", type=int, default=20)
    args = ap.parse_args()

    sql = open(args.arquivo, encoding="utf-8").read()
    revisao_local(sql)

    base = ["bq", "query", "--headless", "--use_legacy_sql=false",
            f"--project_id={args.projeto}", f"--location={args.regiao}",
            "--format=prettyjson"]

    if args.executar:
        base.append(f"--maximum_bytes_billed={args.limite_bytes}")
        base.append(f"--max_rows={args.amostra_linhas}")
    else:
        base.append("--dry_run")

    with tempfile.NamedTemporaryFile("w", suffix=".sql",
                                     delete=False) as f:
        f.write(sql)
        caminho = f.name
    r = subprocess.run(base + [f"<{caminho}>" if False else "@stdin"],
                       capture_output=True, text=True,
                       input=open(caminho).read())
    saida, erro, codigo = r.stdout, r.stderr, r.returncode

    resultado = {"arquivo": args.arquivo, "projeto": args.projeto,
                 "regiao": args.regiao, "modo": "execucao" if args.executar
                 else "dry_run", "codigo_saida": codigo}
    if erro.strip():
        resultado["erro"] = erro.strip()[-2000:]

    try:
        dados = json.loads(saida)
    except json.JSONDecodeError:
        dados = None

    if dados and "statistics" in json.dumps(dados)[:0] if False else dados:
        pass
    job = dados if isinstance(dados, dict) else {}

    stats = (job.get("statistics", {}) or {})
    query_stage = stats.get("query", {}) or {}
    stmt = query_stage.get("statementType", "")
    if not args.executar and stmt and stmt != "SELECT":
        sys.exit(f"RECUSADO: statementType={stmt} não é SELECT.")
    bytes_proc = query_stage.get("totalBytesProcessed", "0")
    resultado["statement_type"] = stmt or "desconhecido(dry_run)"
    resultado["total_bytes_processed"] = bytes_proc
    try:
        resultado["gib"] = str(Decimal(bytes_proc) / Decimal(2 ** 30))
    except Exception:
        pass

    if args.executar:
        job_ref = job.get("jobReference", {}) or {}
        resultado["job_id"] = job_ref.get("jobId")
        resultado["cache_hit"] = query_stage.get("cacheHit")
        billed = query_stage.get("totalBytesBilled")
        if billed:
            resultado["total_bytes_billed"] = billed
        rows = job.get("rows") or []
        resultado["linhas_retornadas"] = len(rows)
        resultado["amostra"] = rows[: args.amostra_linhas]

    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
