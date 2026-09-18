#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compara duas fichas-query e mostra o que mudou entre versoes da query.

Uso:
  python3 comparar_fichas.py <ficha-antiga.md> <ficha-nova.md>

Le os arquivos com open(): nunca use leitores que truncam linhas longas para
regerar ou comparar fichas.
"""

import re
import sys

SECOES = {
    '1. Fontes de dados': ('Objeto', 'Alias na query'),
    '2. CTEs': ('Bloco',),
    '3. Filtros aplicados': ('Local', 'Cláusula', 'Condição'),
    '5. Saída final': ('Bloco', 'Campo'),
    '6. Expressões': ('Bloco', 'Campo exposto'),
    '8. Configuração do modelo': ('Item',),
}


def le(caminho):
    return open(caminho, encoding='utf-8').read()


def tabelas(texto):
    """devolve {secao: (cabecalho, [linhas])} e, para a secao 4, subsecoes."""
    out, subs = {}, {}
    for parte in re.split(r'^## ', texto, flags=re.M)[1:]:
        titulo = parte.split('\n')[0].strip()
        linhas = [l for l in parte.split('\n') if l.startswith('|')]
        if linhas:
            cab = [c.strip() for c in linhas[0].strip().strip('|').split(' | ')]
            dados = [[c.strip() for c in l.strip().strip('|').split(' | ')] for l in linhas[2:]]
        else:
            cab, dados = [], []
        out[titulo] = (cab, dados)
        for sub in re.split(r'^### ', parte, flags=re.M)[1:]:
            nome = sub.split('\n')[0].strip()
            ls = [l for l in sub.split('\n') if l.startswith('|')]
            subs[nome] = [[c.strip() for c in l.strip().strip('|').split(' | ')] for l in ls[2:]]
    return out, subs


def chave_secao(cab, linha, colunas):
    idx = [cab.index(c) for c in colunas if c in cab]
    return tuple(linha[i] for i in idx)


def compara(antiga, nova):
    ta, sa = tabelas(le(antiga))
    tb, sb = tabelas(le(nova))
    saida = [f'# Diferenças entre {antiga.split("/")[-1]} e {nova.split("/")[-1]}', '']
    mudou = False

    for secao, colunas in SECOES.items():
        pa = ta.get(secao, ([], []))[1]
        pb = tb.get(secao, ([], []))[1]
        ca, cb = ta.get(secao, ([], []))[0], tb.get(secao, ([], []))[0]
        if not pa and not pb:
            continue
        if ca != cb:
            saida += [f'## {secao}', f'- cabeçalho: {ca} -> {cb}', '']
            mudou = True
            continue
        ka = {chave_secao(ca, l, colunas): l for l in pa}
        kb = {chave_secao(cb, l, colunas): l for l in pb}
        novos = [k for k in kb if k not in ka]
        sumidos = [k for k in ka if k not in kb]
        alterados = [k for k in ka if k in kb and ka[k] != kb[k]]
        if novos or sumidos or alterados:
            mudou = True
            saida.append(f'## {secao}')
            for k in sumidos:
                saida.append(f'- removido: {" | ".join(ka[k])}')
            for k in novos:
                saida.append(f'+ adicionado: {" | ".join(kb[k])}')
            for k in alterados:
                for i, (x, y) in enumerate(zip(ka[k], kb[k])):
                    if x != y:
                        saida.append(f'~ {k}: coluna {ca[i]}: "{x[:60]}" -> "{y[:60]}"')
            saida.append('')

    blocos_a = set(re.findall(r'^### (.+)$', le(antiga), re.M))
    blocos_b = set(re.findall(r'^### (.+)$', le(nova), re.M))
    if blocos_a != blocos_b:
        mudou = True
        saida.append('## Blocos')
        for b in sorted(blocos_a - blocos_b):
            saida.append(f'- bloco removido: {b}')
        for b in sorted(blocos_b - blocos_a):
            saida.append(f'+ bloco adicionado: {b}')
        saida.append('')

    for nome_a, nome_b in zip(sorted(sa), sorted(sb)):
        if nome_a != nome_b:
            continue
        la, lb = sa[nome_a], sb[nome_b]
        if la != lb:
            mudou = True
            saida.append(f'## Campos — {nome_b}')
            for x, y in zip(la, lb):
                if x != y:
                    saida.append(f'~ {" | ".join(x[:2])}: {" | ".join(x[2:])[:70]} -> {" | ".join(y[2:])[:70]}')
            for extra in la[len(lb):]:
                saida.append(f'- removido: {" | ".join(extra)}')
            for extra in lb[len(la):]:
                saida.append(f'+ adicionado: {" | ".join(extra)}')
            saida.append('')

    if not mudou:
        saida.append('Nenhuma diferença nas seções comparadas.')
    return '\n'.join(saida)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    print(compara(sys.argv[1], sys.argv[2]))
