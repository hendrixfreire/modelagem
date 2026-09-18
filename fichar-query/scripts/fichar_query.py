#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera ficha-query-<ID>.md a partir de uma query SQL ou de um model .sqlx do Dataform.

REGRA DE OURO: este script parte SEMPRE do arquivo da query. Nunca leia uma ficha
para regera-la. Leitores de arquivo truncam linhas longas (perto de 2.000
caracteres) e gravam o texto truncado de volta, corrompendo o arquivo.

Uso:
  python3 fichar_query.py "<query.sql|model.sqlx>" [--id ID] [--out-dir DIR]
                          [--schema-json ARQ.json] [--limite-expressao N] [--sem-id]

Saida: <out-dir>/ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md
       (out-dir padrao: fichas-query/)

O nome carrega a primeira tabela citada no FROM. O ID entra no fim para duas
queries da mesma tabela nao se sobrescreverem. Com --sem-id o nome fica
'ficha-query - <projeto>.<dataset>.<tabela>.md'.
Codigo de saida: 0 quando o gate de verificacao passa; 1 quando falha.
"""

import argparse
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- utilidades

def sem_comentario(sql):
    """Remove comentarios -- e /* */ preservando quebras de linha e strings."""
    out, q, i = [], None, 0
    while i < len(sql):
        c = sql[i]
        if q:
            out.append(c)
            if c == q:
                q = None
            i += 1
        elif c in '"\'':
            q = c
            out.append(c)
            i += 1
        elif sql[i:i + 2] == '--':
            j = sql.find('\n', i)
            i = len(sql) if j == -1 else j
        elif sql[i:i + 2] == '/*':
            j = sql.find('*/', i)
            i = len(sql) if j == -1 else j + 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def depth_map(texto):
    """Profundidade de parenteses por caractere. Strings contam no nivel atual."""
    d = [0] * len(texto)
    prof, q = 0, None
    for i, c in enumerate(texto):
        if q:
            d[i] = prof
            if c == q:
                q = None
        elif c in '"\'':
            q = c
            d[i] = prof
        elif c == '(':
            d[i] = prof
            prof += 1
        elif c == ')':
            prof -= 1
            d[i] = prof
        else:
            d[i] = prof
    return d


def matching_paren(texto, i):
    prof, q = 0, None
    for j in range(i, len(texto)):
        c = texto[j]
        if q:
            if c == q:
                q = None
        elif c in '"\'':
            q = c
        elif c == '(':
            prof += 1
        elif c == ')':
            prof -= 1
            if prof == 0:
                return j
    raise ValueError('parenteses nao balanceados')


def split_unions(texto):
    d = depth_map(texto)
    hits = [m for m in re.finditer(r'\bUNION\b', texto, re.I) if d[m.start()] == 0]
    if not hits:
        return [texto]
    partes, ini = [], 0
    for m in hits:
        partes.append(texto[ini:m.start()])
        fim = m.start() + re.match(r'UNION(\s+(ALL|DISTINCT))?', texto[m.start():], re.I).end()
        ini = fim
    partes.append(texto[ini:])
    return [p.strip() for p in partes if p.strip()]


def split_top(texto, sep):
    """Divide por sep em nivel 0. sep e regex ancorada."""
    d = depth_map(texto)
    partes, ini = [], 0
    for m in re.finditer(sep, texto, re.I):
        if d[m.start()] == 0:
            partes.append(texto[ini:m.start()])
            ini = m.end()
    partes.append(texto[ini:])
    return [p.strip() for p in partes if p.strip()]


def limpa(s):
    return re.sub(r'\s+', ' ', s).strip()


def celula(s):
    return limpa(s).replace('|', r'\|')


def extrai_ctes(texto):
    m = re.match(r'\s*WITH\s+', texto, re.I)
    if not m:
        return [], texto
    i, ctes = m.end(), []
    while True:
        mm = re.match(r'(?:RECURSIVE\s+)?(`?[\w.]+`?)\s+AS\s*\(', texto[i:], re.I)
        if not mm:
            break
        nome = mm.group(1).strip('`')
        abre = i + mm.end() - 1
        fecha = matching_paren(texto, abre)
        ctes.append((nome, texto[abre + 1:fecha]))
        i = fecha + 1
        mr = re.match(r'\s*,\s*', texto[i:])
        if mr:
            i += mr.end()
            continue
        break
    return ctes, texto[i:].strip()


# ---------------------------------------------------------------- modelo

class Bloco:
    """SELECT nomeado, ou container de UNION, ou a saida final."""

    def __init__(self, tipo, texto, rotulo=None):
        self.tipo = tipo          # 'select' | 'union'
        self.texto = texto
        self.rotulo = rotulo
        self.codigo = None
        self.campos = []          # [(pos, exposto, expr)]
        self.fontes = []          # [(objeto, alias)]
        self.filtros = []         # [(clausula, condicao)]
        self.filhos_from = []     # blocos lidos dentro do FROM entre parenteses
        self.origem_union = None  # para union: lista de blocos operando
        self.exibicao = None      # rotulo exibido na secao 4


PALAVRAS = {'ON', 'USING', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS', 'JOIN', 'WHERE',
            'GROUP', 'ORDER', 'BY', 'HAVING', 'QUALIFY', 'LIMIT', 'WINDOW', 'UNION',
            'SELECT', 'FROM', 'AS'}

PALAVRAS_EXPR = PALAVRAS | {'NOT', 'AND', 'OR', 'IN', 'IS', 'NULL', 'TRUE', 'FALSE', 'LIKE',
                            'BETWEEN', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'ASC', 'DESC',
                            'INTERVAL', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE',
                            'STRING', 'INT64', 'FLOAT64', 'NUMERIC', 'BIGNUMERIC', 'BOOL',
                            'BOOLEAN', 'TIMESTAMP', 'DATE', 'DATETIME', 'TIME', 'BYTES',
                            'ARRAY', 'STRUCT', 'GEOGRAPHY', 'JSON'}


def fonte_e_alias(texto, pos):
    """Le o alvo e o alias do FROM/JOIN a partir de pos (indice do F)."""
    m = re.match(r'(?:FROM|JOIN)\s+(`[^`]+`|\$\{\s*(?:ref|source)\s*\([^}]*\)\s*\}|[A-Za-z_][\w.]*)'
                 r'(?:\s+(?:AS\s+)?([A-Za-z_]\w*))?', texto[pos:], re.I)
    if not m:
        return None, None
    alvo = m.group(1).strip()
    if alvo.startswith('`'):
        alvo = alvo.strip('`')
    elif alvo.startswith('${'):
        interno = re.search(r'(?:ref|source)\s*\(([^)]*)\)', alvo)
        alvo = re.sub(r'["\s]', '', interno.group(1)).replace(',', '.') if interno else alvo
    alias = m.group(2)
    if alias and alias.upper() in PALAVRAS:
        alias = None
    return alvo, alias


def valor_ou_limite(cond):
    """Texto literal comparado na condicao, quando houver um operador de nivel 0."""
    d = depth_map(cond)
    for m in re.finditer(r'(>=|<=|<>|!=|=|>|<)', cond):
        if d[m.start()] == 0:
            return limpa(cond[m.end():])
    return ''


def colunas_da_condicao(cond):
    sem_str = re.sub(r'"[^"]*"|\'[^\']*\'', '', cond)
    sem_fun = re.sub(r'\b([A-Za-z_]\w*)\s*\(', '', sem_str)
    ids = re.findall(r'\b([A-Za-z_]\w*)\b', sem_fun)
    return [i for i in dict.fromkeys(ids) if i.upper() not in PALAVRAS_EXPR]


def analisa_bloco(texto, rotulo=None):
    """Constroi a arvore de blocos de um trecho de query."""
    ops = split_unions(texto)
    if len(ops) > 1:
        no = Bloco('union', texto)
        no.origem_union = [analisa_bloco(o) for o in ops]
        for filho in no.origem_union:
            filho.texto_absoluto = False
        return no

    t = texto.strip()
    no = Bloco('select', t, rotulo)
    if not re.match(r'SELECT\b', t, re.I):
        raise ValueError('bloco sem SELECT: ' + t[:80])

    d = depth_map(t)
    froms = [m for m in re.finditer(r'\bFROM\b', t, re.I) if d[m.start()] == 0]
    if not froms:
        raise ValueError('bloco sem FROM: ' + t[:80])
    primeiro_from = froms[0]

    # campos do SELECT de nivel 0
    lista = t[re.match(r'SELECT\s+(DISTINCT\s+)?', t, re.I).end():primeiro_from.start()]
    for p, item in enumerate(split_top(lista, r','), 1):
        item = limpa(item)
        m = re.search(r'\bAS\s+`?([A-Za-z_]\w*)`?\s*$', item, re.I)
        if m:
            exposto, expr = m.group(1), item[:m.start()].strip().rstrip(',').strip()
        else:
            expr = item
            exposto = item.split('.')[-1] if re.fullmatch(r'[A-Za-z_]\w*(\.[A-Za-z_]\w*)?', item) else item
        no.campos.append((p, exposto, expr))

    # filhos no FROM entre parenteses + fontes proprias
    faixas = []
    froms_mascarados = set()
    for m in re.finditer(r'\b(?:FROM|JOIN)\s*\(', t, re.I):
        if d[m.start()] != 0:
            continue
        abre = m.end() - 1
        fecha = matching_paren(t, abre)
        faixas.append((abre, fecha + 1))
        froms_mascarados.add(m.start())
        interno = t[abre + 1:fecha].strip()
        if interno:
            no.filhos_from.append(analisa_bloco(interno))
    mascarado = list(t)
    for a, b in faixas:
        for k in range(a, min(b, len(mascarado))):
            if mascarado[k] != '\n':
                mascarado[k] = ' '
    mascarado = ''.join(mascarado)

    dm = depth_map(mascarado)
    for m in re.finditer(r'\b(?:FROM|JOIN)\b', mascarado, re.I):
        if dm[m.start()] != 0 or m.start() in froms_mascarados:
            continue
        alvo, alias = fonte_e_alias(mascarado, m.start())
        if not alvo:
            continue
        no.fontes.append((alvo, alias))

    # filtros de nivel 0
    for m in re.finditer(r'\b(WHERE|QUALIFY|HAVING)\b', mascarado, re.I):
        if dm[m.start()] != 0:
            continue
        fim = len(mascarado)
        for m2 in re.finditer(r'\b(GROUP\s+BY|ORDER\s+BY|HAVING|QUALIFY|WINDOW|LIMIT|UNION)\b', mascarado[m.end():], re.I):
            if dm[m.end() + m2.start()] == 0:
                fim = m.end() + m2.start()
                break
        trecho = mascarado[m.end():fim]
        for c in split_top(trecho, r'\bAND\b'):
            no.filtros.append((m.group(1).upper(), limpa(c)))
    for m in re.finditer(r'\bON\b', mascarado, re.I):
        if dm[m.start()] != 0:
            continue
        fim = len(mascarado)
        for m2 in re.finditer(r'\b(JOIN|WHERE|GROUP\s+BY|ORDER\s+BY|HAVING|QUALIFY|WINDOW|LIMIT|UNION)\b', mascarado[m.end():], re.I):
            if dm[m.end() + m2.start()] == 0:
                fim = m.end() + m2.start()
                break
        trecho = mascarado[m.end():fim]
        for c in split_top(trecho, r'\bAND\b'):
            no.filtros.append(('ON', limpa(c)))
    return no


def percorre(no, saida, ordem):
    """Pre-ordem: o bloco, depois o que ele le no FROM."""
    if no.tipo == 'select':
        ordem.append(no)
        for f in no.filhos_from:
            percorre(f, saida, ordem)
    else:
        for f in no.origem_union:
            percorre(f, saida, ordem)


def resolve_alias(no_raiz):
    """nome de CTE ou alias -> bloco, para resolver 'x.*' e a coluna Origem."""
    por_rotulo = {}

    def indexa(no):
        if no.tipo == 'select':
            if no.rotulo:
                por_rotulo[no.rotulo.lower()] = no
            for f in no.filhos_from:
                indexa(f)
        else:
            for f in no.origem_union:
                indexa(f)
    indexa(no_raiz)

    mapa = dict(por_rotulo)

    def anda(no):
        if no.tipo == 'select':
            for alvo, alias in no.fontes:
                if alias and alvo.lower() in por_rotulo:
                    mapa[alias.lower()] = por_rotulo[alvo.lower()]
            # alias de subquery lida no FROM: 'FROM ( ... ) AS x'
            if no.filhos_from:
                sufixo = re.search(r'\)\s*(?:AS\s+)?([A-Za-z_]\w*)', no.texto)
                if sufixo:
                    mapa[sufixo.group(1).lower()] = no.filhos_from[0]
            for f in no.filhos_from:
                anda(f)
        else:
            for f in no.origem_union:
                anda(f)
    anda(no_raiz)
    return mapa


# ---------------------------------------------------------------- ficha

def montar(query_path, id_, out_dir, schema, limite):
    bruto = open(query_path, encoding='utf-8').read()
    sqlx = query_path.lower().endswith('.sqlx') or bool(re.search(r'^\s*config\s*\{', bruto, re.M))
    sql = sem_comentario(bruto)
    avisos = []

    config, pre_post = {}, []
    if sqlx:
        for m in re.finditer(r'\bconfig\s*\{', sql):
            fecha = matching_paren(sql, m.end() - 1)
            for linha in sql[m.end():fecha].split('\n'):
                mc = re.match(r'\s*([\w]+)\s*:\s*(.+?),?\s*$', linha)
                if mc:
                    config[mc.group(1)] = mc.group(2).strip()
        for nome in ('pre_operations', 'post_operations'):
            for m in re.finditer(r'\b' + nome + r'\s*\{', sql):
                fecha = matching_paren(sql, m.end() - 1)
                pre_post.append((nome, limpa(sql[m.end():fecha])))
        sql = re.sub(r'^\s*config\s*\{.*?\n\}\s*$', '', sql, flags=re.M | re.S)

    ctes, principal = extrai_ctes(sql)
    raiz = Bloco('union', '')
    raiz.origem_union = []
    for nome, corpo in ctes:
        raiz.origem_union.append(analisa_bloco(corpo, rotulo=nome))
    raiz.origem_union.append(analisa_bloco(principal))

    topo = raiz.origem_union[-1]
    ordem = []
    for c in raiz.origem_union:
        percorre(c, None, ordem)
    cte_names = {n.lower() for n, _ in ctes}
    n_cte = n_bl = 0
    for no in ordem:
        if no.rotulo and no.rotulo.lower() in cte_names:
            n_cte += 1
            no.codigo = f'CTE {n_cte:02d}'
        else:
            n_bl += 1
            no.codigo = f'BL {n_bl:02d}'

    def base_rotulo(no):
        if no.rotulo and no.rotulo.lower() in cte_names:
            return no.rotulo
        if no.filhos_from:
            return 'subquery'
        return no.fontes[0][0].split('.')[-1] if no.fontes else 'sem origem'

    genericos = {'subquery', 'sem origem'}
    contagem = {}
    for no in ordem:
        b = base_rotulo(no)
        contagem[b] = contagem.get(b, 0) + 1
        if b in genericos or contagem[b] == 1:
            no.exibicao = b
        else:
            no.exibicao = f'{b} (ocorrência {contagem[b]})'

    produtores = topo.origem_union if topo.tipo == 'union' else [topo]
    produtores = [p for p in produtores if p.tipo == 'select']

    alvo = resolve_alias(raiz)
    consumida = {no.codigo: [] for no in ordem if no.codigo}
    for no in ordem:
        origem_codigo = no.codigo or 'SAÍDA'
        for outra in ordem:
            if outra is no:
                continue
            nomes = [f[0].lower() for f in no.fontes]
            if outra.rotulo and outra.rotulo.lower() in nomes:
                consumida.setdefault(outra.codigo, []).append(origem_codigo)

    # primeira tabela citada no FROM, na ordem de aparicao dos blocos
    primeira_tabela = None
    for no in ordem:
        for obj, _ in no.fontes:
            if not obj.lower().startswith('ref(') and not obj.lower().startswith('source('):
                partes = obj.split('.')
                primeira_tabela = '.'.join(partes[-3:]) if len(partes) >= 3 else '.'.join(partes)
                break
        if primeira_tabela:
            break
    if primeira_tabela is None:
        partes = [p for p, _ in ctes]
        primeira_tabela = partes[0] if partes else 'sem-tabela'

    # ---- secao 1
    s1 = ['## 1. Fontes de dados', '',
          '| # | Projeto | Dataset | Objeto | Alias na query | Referenciada em |',
          '|---|---|---|---|---|---|']
    n = 0
    for no in ordem:
        for obj, alias in no.fontes:
            n += 1
            if '${' in obj or obj.lower().startswith(('ref(', 'source(')):
                proj = ds = 'modelo Dataform'
                tab = obj
            else:
                p = obj.split('.')
                if len(p) >= 3:
                    proj, ds, tab = p[0], p[1], '.'.join(p[2:])
                elif len(p) == 2:
                    proj, ds, tab = 'não informado', p[0], p[1]
                else:
                    proj, ds, tab = 'não informado', 'não informado', p[0]
            s1.append(f'| {n} | {proj} | {ds} | {tab} | {alias or "—"} | {no.codigo or "SAÍDA"} |')

    # ---- secao 2
    s2 = ['## 2. CTEs', '', '| Bloco | CTE | Origem | Consumida por |', '|---|---|---|---|']
    if ctes:
        for no in ordem:
            if not (no.rotulo and no.rotulo.lower() in cte_names):
                continue
            orgs = [o for o, _ in no.fontes]
            orgs = [b.codigo if (b := alvo.get(o.lower())) else o for o in orgs]
            cons = consumida.get(no.codigo, [])
            if no in produtores or (topo.tipo == 'select' and no is topo):
                cons = cons + ['SAÍDA']
            s2.append(f'| {no.codigo} | {no.rotulo} | {" + ".join(orgs) if orgs else "—"} | '
                      f'{", ".join(cons) if cons else "não consumida"} |')
    else:
        s2.append('| — | sem CTE | — | — |')

    # ---- secao 3
    s3 = ['## 3. Filtros aplicados', '',
          '| # | Local | Cláusula | Condição | Coluna(s) | Valor ou limite |',
          '|---|---|---|---|---|---|']
    n = 0
    for no in ordem:
        for clausula, cond in no.filtros:
            n += 1
            cols = colunas_da_condicao(cond)
            s3.append(f'| {n} | {no.codigo or "SAÍDA"} | {clausula} | {celula(cond)} | '
                      f'{", ".join(cols)} | {celula(valor_ou_limite(cond))} |')

    # ---- secao 4
    expressoes, registradas = [], {}
    def nome_origem(no, exposto, expr):
        if re.fullmatch(r'([A-Za-z_]\w*\.)?\*', expr):
            pre = expr.split('.')[0] if '.' in expr else None
            b = alvo.get(pre.lower()) if pre else None
            org = b.codigo if b else (no.fontes[0][0] if no.fontes else 'não rastreável')
            return org, '*', ''
        if re.fullmatch(r'[A-Za-z_]\w*(\.[A-Za-z_]\w*)?', expr):
            pre = expr.split('.')[0] if '.' in expr else None
            nome = expr.split('.')[-1]
            if pre:
                b = alvo.get(pre.lower())
                org = b.codigo if b else pre
            else:
                b = alvo.get(no.fontes[0][0].lower()) if no.fontes else None
                org = b.codigo if b else (no.fontes[0][0] if no.fontes else 'não rastreável')
            return org, nome, ''
        txt = expr
        if limite and len(txt) > limite:
            chave = (no.codigo, exposto)
            if chave not in registradas:
                registradas[chave] = f'E{len(expressoes) + 1}'
                expressoes.append((len(expressoes) + 1, no.codigo, exposto, txt))
            txt = registradas[chave]
        return ' + '.join(b.codigo if (b := alvo.get(f[0].lower())) else f[0] for f in no.fontes) or 'não rastreável', '', txt

    s4 = ['## 4. Campos por bloco', '']
    intermediarios = [no for no in ordem if no not in produtores]
    for no in intermediarios:
        s4 += [f'### {no.codigo} — {no.exibicao}', '',
               '| # | Campo exposto | Origem | Campo na origem | Expressão |', '|---|---|---|---|---|']
        for p, exposto, expr in no.campos:
            org, nome, x = nome_origem(no, exposto, expr)
            s4.append(f'| {p} | {celula(exposto)} | {celula(org)} | {celula(nome)} | {celula(x)} |')
        s4.append('')
    if not intermediarios:
        s4.append('sem bloco intermediário com lista de campos')

    # ---- secao 5
    tipos = {}
    if schema:
        try:
            dados = json.load(open(schema, encoding='utf-8'))
            campos = dados if isinstance(dados, list) else dados.get('schema', [])
            campos = campos.get('fields', campos) if isinstance(campos, dict) else campos
            for c in campos if isinstance(campos, list) else []:
                if isinstance(c, dict) and 'name' in c:
                    tipos[c['name'].upper()] = c.get('type', '') + (' (repetido)' if c.get('mode') == 'REPEATED' else '')
        except Exception as e:
            avisos.append(f'schema-json ignorado: {e}')

    s5 = ['## 5. Saída final', '', '| # | Bloco | Campo | Tipo |', '|---|---|---|---|']
    n = 0
    for no in produtores:
        for p, exposto, expr in no.campos:
            n += 1
            if topo.tipo == 'select' and no is topo:
                if re.fullmatch(r'([A-Za-z_]\w*\.)?\*', expr):
                    pre = expr.split('.')[0] if '.' in expr else None
                    b = alvo.get(pre.lower()) if pre else None
                    bloco = b.codigo if b else 'SAÍDA'
                else:
                    bloco = 'SAÍDA'
            else:
                bloco = no.codigo
            s5.append(f'| {n} | {bloco} | {celula(exposto)} | {tipos.get(exposto.upper(), "")} |')

    # ---- secao 6
    s6 = []
    if expressoes:
        s6 = ['## 6. Expressões', '', '| # | Bloco | Campo exposto | Expressão |', '|---|---|---|---|']
        for i, bloco, campo, txt in expressoes:
            s6.append(f'| E{i} | {bloco} | {celula(campo)} | {celula(txt)} |')

    # ---- secao 7
    sindicatos = []
    def uni(no):
        if no.tipo == 'union':
            ops = [o for o in no.origem_union if o.tipo == 'select']
            if len(ops) >= 2 and ops[0].campos and all(not any(re.fullmatch(r'([A-Za-z_]\w*\.)?\*', c[2]) for c in o.campos) for o in ops):
                sindicatos.append(ops)
            for o in no.origem_union:
                uni(o)
        else:
            for f in no.filhos_from:
                uni(f)
    uni(raiz)
    s7 = []
    if sindicatos:
        s7 = ['## 7. Conferência de posição', '']
        for ops in sindicatos:
            maxc = max(len(o.campos) for o in ops)
            s7 += [f'### União de {", ".join(o.codigo for o in ops)}', '',
                   '| Posição | ' + ' | '.join(o.codigo for o in ops) + ' |',
                   '|---|' + '---|' * len(ops)]
            for i in range(maxc):
                linha = []
                for o in ops:
                    linha.append(celula(o.campos[i][1]) if i < len(o.campos) else '—')
                s7.append(f'| {i + 1} | ' + ' | '.join(linha) + ' |')
            s7.append('')

    # ---- secao 8
    s8 = []
    if sqlx:
        s8 = ['## 8. Configuração do modelo', '', '| # | Item | Valor |', '|---|---|---|']
        i = 0
        for k, v in config.items():
            i += 1
            s8.append(f'| {i} | config.{k} | {celula(v)} |')
        for nome, corpo in pre_post:
            i += 1
            s8.append(f'| {i} | {nome} | {celula(corpo)} |')

    secoes = [s1, s2, s3, s4, s5] + [s for s in (s6, s7, s8) if s]
    corpo = f'# Ficha da query — {id_}\n\n' + '\n\n'.join('\n'.join(s) for s in secoes) + '\n'
    conteudo = unicodedata.normalize('NFC', corpo)

    # ---- gate de verificacao
    problemas = []
    for i, s in enumerate(secoes, 1):
        linhas = [l for l in s if l.startswith('|')]
        larguras = {l.count('|') - l.count(r'\|') for l in linhas}
        if len(larguras) > 1:
            problemas.append(f'seção {nome_secao(s)}: colunas desiguais {sorted(larguras)}')
    if '[truncated]' in conteudo:
        problemas.append('marcador de truncamento no conteudo')
    if re.search(r'(?m)^(?!\s*$|#|\|)', conteudo):
        problemas.append('texto fora de titulo ou tabela')
    nums = [int(c) for c in re.findall(r'(?m)^\| (\d+) \|', s5[3])] if len(s5) > 3 else []
    nums = [int(l.strip('| ').split(' | ')[0]) for l in s5 if l.startswith('|') and l.strip('| ').split(' | ')[0].isdigit()]
    if nums and nums != list(range(1, len(nums) + 1)):
        problemas.append('seção 5 fora de sequência')
    codigos = {no.codigo for no in ordem if no.codigo} | {'SAÍDA'}
    refs = set(re.findall(r'\b(?:CTE|BL) \d+\b|\bSAÍDA\b', conteudo))
    if refs - codigos:
        problemas.append(f'referência sem definição: {sorted(refs - codigos)}')
    if not n:
        problemas.append('nenhum campo na saída final')
    return conteudo, problemas, avisos, primeira_tabela


def nome_secao(s):
    return s[0].replace('## ', '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--id')
    ap.add_argument('--out-dir', default='fichas-query')
    ap.add_argument('--schema-json')
    ap.add_argument('--limite-expressao', type=int, default=300)
    ap.add_argument('--sem-id', action='store_true',
                    help='nao acrescenta o ID ao nome do arquivo')
    a = ap.parse_args()

    id_ = a.id or os.path.splitext(os.path.basename(a.query))[0]
    conteudo, problemas, avisos, tabela = montar(a.query, id_, a.out_dir, a.schema_json, a.limite_expressao)
    for av in avisos:
        print(f'aviso: {av}')
    if problemas:
        print('GATE REPROVADO — ficha NAO gravada:')
        for p in problemas:
            print(f'  - {p}')
        return 1
    seguro = re.sub(r'[^\w.\-]', '-', tabela)
    nome = f'ficha-query - {seguro}' + ('' if a.sem_id else f' - {id_}') + '.md'
    os.makedirs(a.out_dir, exist_ok=True)
    destino = os.path.join(a.out_dir, nome)
    with open(destino, 'w', encoding='utf-8') as fh:
        fh.write(conteudo)
    print(f'gate aprovado: {destino} ({len(conteudo)} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
