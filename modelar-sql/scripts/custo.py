#!/usr/bin/env python3
"""Custo on-demand a partir de bytes e tarifa oficial.

Uso:
  python3 custo.py --bytes 34359738368 --tarifa-tib 6.25 \
      --cambio 5.42 [--frequencia 30] [--rotulo "q01 - dry run"]
  python3 custo.py --comparar --bytes-canonica 34359738368 \
      --bytes-otimizada 17179869184 --tarifa-tib 6.25 --cambio 5.42

Calcula com Decimal, sem arredondamento prévio. No modo --comparar,
avalia o limiar de redução de 30%. Tarifa por região: revalide em
https://cloud.google.com/bigquery/pricing para a região do cliente.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal

TIB = Decimal(2 ** 40)
LIMIAR = Decimal("0.30")


def custo(bytes_base: Decimal, tarifa_tib: Decimal, cambio: Decimal | None,
          frequencia: int, rotulo: str) -> dict:
    usd_execucao = bytes_base / TIB * tarifa_tib
    usd_periodo = usd_execucao * Decimal(frequencia)
    out = {
        "rotulo": rotulo,
        "bytes_base": str(bytes_base),
        "origem_bytes": "declarada_pelo_chamador(rotule_medido_ou_estimado)",
        "tarifa_usd_por_tib": str(tarifa_tib),
        "custo_usd_execucao": str(usd_execucao),
        "frequencia_execucoes": frequencia,
        "custo_usd_periodo": str(usd_periodo),
    }
    if cambio is not None:
        out["cambio_ptax"] = str(cambio)
        out["custo_brl_execucao"] = str(usd_execucao * cambio)
        out["custo_brl_periodo"] = str(usd_periodo * cambio)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bytes", dest="bytes_", type=int)
    ap.add_argument("--tarifa-tib", type=str, required=True,
                    help="Tarifa oficial da região, ex.: 6.25")
    ap.add_argument("--cambio", type=str, help="Média PTAX congelada")
    ap.add_argument("--frequencia", type=int, default=1)
    ap.add_argument("--rotulo", default="")
    ap.add_argument("--comparar", action="store_true")
    ap.add_argument("--bytes-canonica", type=int)
    ap.add_argument("--bytes-otimizada", type=int)
    args = ap.parse_args()

    tarifa = Decimal(args.tarifa_tib)
    cambio = Decimal(args.cambio) if args.cambio else None

    if args.comparar:
        if not args.bytes_canonica or not args.bytes_otimizada:
            sys.exit("Informe --bytes-canonica e --bytes-otimizada.")
        c = Decimal(args.bytes_canonica)
        o = Decimal(args.bytes_otimizada)
        if c <= 0:
            sys.exit("Custo canônico zero/negativo: percentual indefinido, "
                     "sem economia demonstrável. Não retenha variante.")
        custo_canonica = custo(c, tarifa, cambio, 1, "canonica")
        custo_variante = custo(o, tarifa, cambio, 1, "otimizada")
        reducao = (custo_canonica["custo_usd_execucao"] != "0" and
                   (Decimal(custo_canonica["custo_usd_execucao"]) -
                    Decimal(custo_variante["custo_usd_execucao"])) /
                   Decimal(custo_canonica["custo_usd_execucao"]))
        aceitar = reducao >= LIMIAR
        print(json.dumps({
            "canonica": custo_canonica,
            "otimizada": custo_variante,
            "reducao": str(reducao),
            "reducao_percentual": str(reducao * 100),
            "limiar": str(LIMIAR * 100) + "%",
            "aceitar_se_equivalente": aceitar,
        }, ensure_ascii=False, indent=2))
        return

    if args.bytes_ is None:
        sys.exit("Informe --bytes ou use --comparar.")
    print(json.dumps(custo(Decimal(args.bytes_), tarifa, cambio,
                           args.frequencia, args.rotulo),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
