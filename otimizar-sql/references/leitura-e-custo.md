# Reduzir leitura e custo

No BigQuery on-demand, o custo é proporcional aos bytes lidos das colunas referenciadas. Reduzir leitura é a otimização de maior retorno.

## Colunas

- Selecione só as colunas usadas. Colunas grandes (`STRING` longa, `JSON`, `ARRAY`, `STRUCT`) pesam mais.
- `SELECT * EXCEPT (coluna_grande)` reduz a leitura quando a lista completa é longa. Prefira colunas explícitas na entrega.
- `LIMIT` não reduz bytes lidos em tabela não clusterizada. Para explorar sem custo, use a aba de pré-visualização, `bq head` ou `TABLESAMPLE`.

## Partição

- Filtre direto na coluna de partição, com constante ou parâmetro: `WHERE data_evento >= DATE '2026-01-01' AND data_evento < DATE '2026-02-01'`.
- Não envolva a coluna em função (`WHERE DATE(ts) = ...` em coluna `TIMESTAMP` particionada, `FORMAT_DATE(...)`, `CAST`). Compare com o dry run: se os bytes não caírem, a poda não ocorreu.
- Em tabela por ingestão, filtre `_PARTITIONTIME` ou `_PARTITIONDATE`.
- Subconsulta como valor do filtro de partição pode impedir a poda estática. Calcule a data antes (variável em script ou parâmetro) quando a poda for essencial.
- Tabela com `require_partition_filter` recusa consulta sem filtro de partição. Não desative essa opção sem decisão do usuário.
- Tabelas fragmentadas por data (`tabela_20260101`, `tabela_*`) são piores que uma tabela particionada. Recomende a migração como DDL.

## Clustering

- Filtre pelas colunas de clustering, na ordem definida na tabela. Filtro só na segunda coluna sem a primeira poda menos.
- O clustering reduz bytes lidos de forma que o dry run pode não refletir. Meça com um job real dentro do teto de bytes, com cache desligado, ou declare inconclusivo.
- Clustering vale para colunas de alta cardinalidade filtradas com frequência (ids, códigos, categorias).

## Filtros

- Aplique filtros de negócio antes de join e agregação, quando o resultado for equivalente.
- Filtre a tabela grande antes de juntá-la, em CTE ou subconsulta com `WHERE`.
- `WHERE` com `LIKE '%texto%'` e `REGEXP_CONTAINS` leem tudo. Prefira igualdade, `STARTS_WITH` ou um índice de busca (`SEARCH INDEX`), que é DDL e vai como recomendação.

## Amostragem e aproximação

- `TABLESAMPLE SYSTEM (10 PERCENT)` lê uma fração dos blocos. Serve para explorar e nunca para resultado de entrega.
- `APPROX_COUNT_DISTINCT`, `APPROX_QUANTILES` e `APPROX_TOP_COUNT` são muito mais baratos que as versões exatas, com erro pequeno. Só com aprovação do usuário.

## Objetos que reduzem leitura (recomendações de DDL)

- Tabela particionada e clusterizada pelos filtros mais comuns.
- Tabela resumo (agregada) ou view materializada para consultas repetidas sobre a mesma agregação.
- Colunas `DATE` derivadas para filtrar, em vez de função sobre `TIMESTAMP`.
- `SEARCH INDEX` para busca textual em colunas de texto.

## Modelo de cobrança

- On-demand cobra bytes lidos, com mínimo por tabela referenciada. Capacidade (slots) cobra slot-hora, e bytes deixam de ser o custo direto: nesse modelo meça slot-ms.
- Defina `--maximum_bytes_billed` em toda execução real para impedir custo inesperado.
- Cache de resultado só vale para a mesma query, sem funções voláteis e sem mudança nas fontes. Para medir de verdade, desligue o cache (`--nouse_cache`).
- Para tarifa e cálculo de custo, use o estudo de custo da skill `modelar-sql` (`references/custos-bigquery.md`) ou a página oficial de preços. Não fixe tarifa nesta skill.
