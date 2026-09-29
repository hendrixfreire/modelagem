#!/usr/bin/env python3
"""Auditoria estática da pasta do modelo.

Uso:
  python3 auditoria.py /caminho/para/modelagem

Varre a pasta do modelo e reporta problemas encontrados:
- títulos e ordem das 14 seções fixas do MODEL_SPECS.md
- YAML de controle com campos obrigatórios
- CHECKLIST.md presente com link de volta ao MODEL_SPECS.md
- links relativos quebrados em todos os .md
- IDs de query duplicados (pastas e arquivos .sql)
- .sql existente não marcado como implementada no mapa (heurística)
- referências a pastas/arquivos de variantes descartadas (sufixo
  _otimizada citado sem pasta correspondente e sem registro)
Saída: JSON com {ok, problemas[]}.
"""
import json
import re
import sys
from pathlib import Path

SECOES = [f"## {i}." for i in range(1, 15)]
TITULOS = {
    "1": "## 1. Identificação e aprovação",
    "2": "## 2. Objetivo, perguntas de negócio e consumidores",
    "3": "## 3. Escopo e exclusões",
    "4": "## 4. Modelo existente e histórico",
    "5": "## 5. Fontes de dados e cadeia de dependências",
    "6": "## 6. Granularidades, chaves e relacionamentos",
    "7": "## 7. Regras de negócio",
    "8": "## 8. Outputs e schemas",
    "9": "## 9. Atualização e tratamento temporal",
    "10": "## 10. Tamanho das tabelas e estudo de custos",
    "11": "## 11. Validações e critérios de aceite",
    "12": "## 12. Pendências e decisões",
    "13": "## 13. Mapa de queries e dependências",
    "14": "## 14. Histórico de alterações",
}
CAMPOS_YAML = ["fase_atual", "situacao", "query_em_foco",
               "versao_semantica_aprovada", "gate_pendente", "bloqueios",
               "proxima_acao", "estado_validacao"]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: auditoria.py <pasta_do_modelo>")
    pasta = Path(sys.argv[1]).resolve()
    if not pasta.is_dir():
        sys.exit(f"Pasta não encontrada: {pasta}")
    problemas: list[str] = []

    specs = pasta / "MODEL_SPECS.md"
    if not specs.is_file():
        problemas.append("MODEL_SPECS.md ausente na raiz do modelo.")
    else:
        texto = specs.read_text(encoding="utf-8")
        pos_achados = []
        for num, titulo in TITULOS.items():
            pos = texto.find(titulo)
            if pos < 0:
                problemas.append(f"Seção ausente ou título divergente: {titulo}")
            else:
                pos_achados.append((pos, num))
        if [n for _, n in sorted(pos_achados)] != [str(i) for i in range(1, 15)]:
            problemas.append("Seções fora da ordem fixa 1–14.")
        m = re.search(r"```yaml\n(.*?)```", texto, re.S)
        if not m:
            problemas.append("YAML de controle ausente na seção 1.2.")
        else:
            for campo in CAMPOS_YAML:
                if not re.search(rf"^{campo}:", m.group(1), re.M):
                    problemas.append(f"Campo do YAML de controle ausente: {campo}")
        if "cambio_congelado" not in texto and "câmbio" not in texto.lower():
            problemas.append("Seção 10.3 de câmbio não localizada.")

    if not (pasta / "GLOSSARIO.md").is_file():
        problemas.append("GLOSSARIO.md ausente na raiz do modelo.")
    if not (pasta / "CHECKLIST.md").is_file():
        problemas.append("CHECKLIST.md ausente na raiz do modelo.")
    elif specs.is_file():
        t = specs.read_text(encoding="utf-8")
        if "CHECKLIST.md" not in t:
            problemas.append("MODEL_SPECS.md não referencia CHECKLIST.md.")

    # Links relativos em todos os .md da pasta do modelo.
    for md in pasta.rglob("*.md"):
        if md.name == "SKILL.md":
            continue
        texto = md.read_text(encoding="utf-8")
        for alvo in re.findall(r"\]\((?!http)([^)#]+)\)", texto):
            caminho = (md.parent / alvo).resolve()
            if not caminho.exists():
                problemas.append(f"Link quebrado em {md.relative_to(pasta)}: {alvo}")

    # IDs únicos e .sql vs mapa.
    ids_pastas = set()
    mapa_sql: set[str] = set()
    if specs.is_file():
        mapa = specs.read_text(encoding="utf-8")
        for linha in mapa.splitlines():
            if "|" in linha and ".sql" in linha:
                for cel in linha.split("|"):
                    cel = cel.strip()
                    m2 = re.match(r"^\[(.+?\.sql)\]", cel) or \
                         (re.match(r"^[\w\-/]+\.sql$", cel) and
                          re.match(cel, cel))
                    if m2:
                        mapa_sql.add((m2.group(1) if m2 else cel)
                                     .replace("[", "").replace("]", ""))

    for sql in pasta.rglob("*.sql"):
        rel = sql.relative_to(pasta).as_posix()
        # ignora SQL de teste
        if "testes/" in rel:
            continue
        pasta_q = sql.parent.name
        m_id = re.match(r"^(q\d+)", pasta_q)
        if m_id and m_id.group(1) in ids_pastas:
            problemas.append(f"ID de query duplicado: {m_id.group(1)}")
        if m_id:
            ids_pastas.add(m_id.group(1))
        if mapa_sql and sql.name not in mapa_sql:
            problemas.append(f".sql fora do mapa (heurística): {rel}")

    # Variantes citadas sem pasta correspondente.
    nomes_md = {md.name for md in pasta.rglob("*.md")}
    for md in pasta.rglob("*.md"):
        t = md.read_text(encoding="utf-8")
        for m3 in re.finditer(r"([\w\-/]*_otimizada(?:\.sql)?)", t):
            alvo = m3.group(1)
            if (pasta / alvo).exists() or alvo in nomes_md:
                continue
            # permitido em registro genérico de descarte
            if "descartada" in t[max(0, m3.start() - 120):m3.end() + 120]:
                continue
            problemas.append(
                f"Referência a variante sem arquivo: {alvo} "
                f"em {md.relative_to(pasta)}")

    ok = not problemas
    print(json.dumps({"pasta": str(pasta), "ok": ok,
                      "problemas": problemas},
                     ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
