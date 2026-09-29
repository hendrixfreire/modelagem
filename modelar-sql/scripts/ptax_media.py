#!/usr/bin/env python3
"""Média da PTAX de venda nos 30 dias corridos completos anteriores.

Uso:
  python3 ptax_media.py [--data 2026-09-14] [--pasta-evidencia .]

Janela: D-30 a D-1 (America/Sao_Paulo), inclusivos. Consulta a API PTAX
do BCB, seleciona a cotação de fechamento de cada dia publicado
(maior dataHoraCotacao do dia) e calcula a média aritmética de
cotacaoVenda com Decimal. Não preenche dias sem publicação.
Sem --data, usa a data atual.
"""
import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
URL = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
       "CotacaoDolarPeriodo(dataInicial=@dataInicial,"
       "dataFinalCotacao=@dataFinalCotacao)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="Data do estudo em ISO (YYYY-MM-DD)")
    ap.add_argument("--pasta-evidencia", help="Pasta para salvar evidência JSON")
    args = ap.parse_args()

    if args.data:
        d_ref = date.fromisoformat(args.data)
    else:
        d_ref = datetime.now(FUSO).date()

    d_ini = d_ref - timedelta(days=30)
    d_fim = d_ref - timedelta(days=1)
    # A API PTAX exige MM-DD-YYYY, não ISO.
    ini_api = d_ini.strftime("%m-%d-%Y")
    fim_api = d_fim.strftime("%m-%d-%Y")

    url = (f"{URL}?@dataInicial='{ini_api}'"
           f"&@dataFinalCotacao='{fim_api}'"
           "&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"
           "&$top=1200")
    r = subprocess.run(["curl", "-s", "--max-time", "60", url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit("BCB indisponível: mantenha USD e marque BRL pendente.")

    dados = json.loads(r.stdout)
    valores = dados.get("value", [])
    if not valores:
        sys.exit("Resposta vazia da PTAX: não é câmbio zero. "
                 "Mantenha USD e marque BRL pendente.")

    # Fechamento = maior dataHoraCotacao de cada dia publicado.
    fech: dict[str, tuple[str, Decimal]] = {}
    for v in valores:
        dia = v["dataHoraCotacao"][:10]
        hor = v["dataHoraCotacao"]
        venda = Decimal(str(v["cotacaoVenda"]))
        if dia not in fech or hor > fech[dia][0]:
            fech[dia] = (hor, venda)

    cotacoes = [par[1] for par in sorted(fech.values(), key=lambda x: x[0])]
    media = sum(cotacoes, Decimal(0)) / Decimal(len(cotacoes))

    resultado = {
        "data_referencia": d_ref.isoformat(),
        "janela_inicio": d_ini.isoformat(),
        "janela_fim": d_fim.isoformat(),
        "contagem_dias_publicados": len(cotacoes),
        "media_ptax_venda": str(media),
        "url": url,
        "momento_consulta": datetime.now(FUSO).isoformat(),
        "cotas_fechamento": {d: str(c) for d, (_, c) in sorted(fech.items())},
    }
    if args.pasta_evidencia:
        with open(f"{args.pasta_evidencia}/ptax_evidencia.json", "w",
                  encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
