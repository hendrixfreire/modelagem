---
name: otimizar-sql
description: "Otimiza consultas SQL no BigQuery (GoogleSQL): reduz bytes lidos e custo, poda partições e clustering, melhora joins, agregações, janelas e deduplicação, e lê o plano de execução, preservando o resultado. Use quando o usuário pedir para otimizar, acelerar ou reduzir o custo de uma query BigQuery, ou perguntar por que ela lê muitos bytes ou está lenta. Não use para outros bancos (MySQL, PostgreSQL, SQL Server, Oracle) nem para explicar, comentar ou fichar a query."
disable-model-invocation: true
argument-hint: "[arquivo .sql | query BigQuery]"
version: 1.0.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [bigquery, sql, otimizacao, custo, performance]
    related_skills: [explicar-query, modelar-sql, bigquery-basics]
---

# Otimizar SQL no BigQuery

Reduza bytes lidos, slots consumidos e tempo de uma query BigQuery sem alterar o resultado. No BigQuery on-demand, o custo vem dos bytes lidos nas colunas selecionadas, não das linhas devolvidas. Não existem índices: partição e clustering cumprem esse papel.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Use as ferramentas equivalentes do ambiente atual para ler arquivos, executar comandos e fazer perguntas ao usuário.

## Limites

- Otimizar não muda semântica. Toda reescrita exige prova de equivalência: mesmas colunas, tipos, granularidade, multiplicidade, nulos e métricas. Sem prova, entregue como hipótese.
- Meça antes e depois com dry run (`bq query --dry_run --use_legacy_sql=false`), na mesma região e com os mesmos parâmetros. O dry run estima bytes e não executa a query.
- Execute consulta que processe dados só com limite de bytes definido (`--maximum_bytes_billed`) e autorização do usuário.
- Trate DDL (tabela particionada, clusterizada, materializada, view materializada, índice de busca) como recomendação. Não crie nem altere objetos sem autorização explícita.
- Dentro da skill `modelar-sql`, as invariantes dela prevalecem sobre esta skill: somente leitura, uma variante por gate, sem tabela temporária.
- Otimização que aproxima o resultado (`APPROX_COUNT_DISTINCT`, `TABLESAMPLE`) exige aprovação do usuário.

## Procedimento

1. **Entenda o contrato.** Identifique o que uma linha da saída representa e as fontes. Se faltar contexto, use `explicar-query` antes de otimizar.
2. **Meça a linha de base.** Rode o dry run e registre bytes estimados por tabela. Descubra partição e clustering de cada fonte (`references/plano-e-monitoramento.md`).
3. **Leia o plano.** Se houver um job executado, compare estágios, bytes lidos e embaralhados, e slot-ms (`references/plano-e-monitoramento.md`).
4. **Escolha técnicas** pela ordem de impacto: leitura primeiro, depois estrutura da query, depois execução.
5. **Prove equivalência** e meça de novo. Descarte a técnica que não reduzir bytes ou tempo de forma mensurável.
6. **Relate** antes e depois (bytes, custo estimado, tempo se medido), a técnica aplicada e o que ficou como recomendação de DDL.

## Referências (carregue sob demanda)

| Quando | Ler |
| --- | --- |
| Reduzir bytes lidos: partição, clustering, colunas, filtros, amostragem | [leitura-e-custo.md](references/leitura-e-custo.md) |
| Joins, agregações, janelas, deduplicação, `UNNEST`, subconsultas | [joins-e-agregacao.md](references/joins-e-agregacao.md) |
| Padrões que costumam custar caro e a alternativa de cada um | [anti-padroes.md](references/anti-padroes.md) |
| Plano de execução, `INFORMATION_SCHEMA`, jobs caros, armazenamento | [plano-e-monitoramento.md](references/plano-e-monitoramento.md) |

## Checklist

- [ ] Nenhum `SELECT *` na entrega; só colunas usadas.
- [ ] Filtro direto na coluna de partição, sem função sobre ela.
- [ ] Filtro nas colunas de clustering, na ordem definida na tabela.
- [ ] Filtros de negócio aplicados antes de join e agregação, quando equivalentes.
- [ ] Sem subconsulta correlacionada onde uma window function ou agregação única resolve.
- [ ] Sem `ORDER BY` desnecessário e sem `ORDER BY` global de tabela grande sem `LIMIT`.
- [ ] Sem `DISTINCT` escondendo duplicação de join.
- [ ] Chaves de join com o mesmo tipo (de preferência `INT64`) nos dois lados.
- [ ] Bytes medidos antes e depois com dry run na mesma região.
- [ ] Equivalência do resultado provada ou declarada como não provada.
