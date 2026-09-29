# Comandos prontos: BigQuery, PTAX e cálculo de custo

Use os scripts em `scripts/` primeiro; este arquivo documenta o que eles executam, para casos manuais e diagnósticos. Ajuste projeto, região e limite em cada comando. Sem limite definido pelo usuário, não execute consulta que processe dados.

## Dry run de leitura

`scripts/bq_leitura.py` valida sintaxe via CLI, executa dry run, recusa `statementType` diferente de `SELECT` e, com `--executar`, roda a query com teto e cache desligado. Equivalente manual:

```bash
bq query --headless --dry_run --use_legacy_sql=false \
  --project_id=<PROJETO> --location=<REGIAO> \
  --format=prettyjson < qNN_arquivo.sql
```

O JSON tem `totalBytesProcessed` e `statementType`. Recuse `statementType` diferente de `SELECT` em qualquer execução. Execução real com teto:

```bash
bq query --use_legacy_sql=false --headless \
  --project_id=<PROJETO> --location=<REGIAO> \
  --maximum_bytes_billed=<LIMITE> \
  --format=prettyjson < qNN_arquivo.sql
```

`--maximum_bytes_billed` é o teto autorizado, não garantia de custo menor. `LIMIT` não reduz bytes lidos. Registre `jobId`, bytes e amostra como evidência.

## Inventário de tamanhos

`scripts/tamanhos.py` executa esta consulta por tabela; equivalente manual:

```sql
SELECT table_id, row_count, size_bytes,
       size_bytes - num_rows * 8 AS bytes_estimados_aprox,
       last_modified_time
FROM `<PROJETO>.<DATASET>.__TABLES__`
WHERE table_id IN ('<TABELA1>', '<TABELA2>')
```

Para detalhe de armazenamento lógico/físico, ativo/longa duração, use `INFORMATION_SCHEMA.TABLE_STORAGE` (pode exigir cobrança de metadados; declare o limite):

```sql
SELECT table_id, storage_information.total_logical_bytes,
       storage_information.total_physical_bytes,
       storage_information.active_logical_bytes,
       storage_information.long_term_logical_bytes,
       storage_information.last_updated_time
FROM `<PROJETO>.<REGIAO>.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_id IN ('<TABELA1>', '<TABELA2>')
```

Registre data da medição e origem. Views não têm armazenamento próprio; percorra as fontes e deduplique tabelas-base antes de somar.

## Câmbio PTAX (média dos 30 dias corridos completos anteriores)

`scripts/ptax_media.py` calcula D-30..D-1 (America/Sao_Paulo), consulta a API e retorna média, contagem e URL. Equivalente manual:

```bash
curl -s "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='%3CMM-DD-YYYY%3E'&@dataFinalCotacao='%3CMM-DD-YYYY%3E'&\$format=json&\$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao&\$top=100&\$skip=0"
```

Datas no formato exigido pela API: `MM-DD-YYYY`, com apóstrofos. Não use ISO aqui. Filtre por `dataHoraCotacao` a cotação de fechamento de cada dia publicado (maior horário do dia), use `cotacaoVenda`, não preencha dias sem publicação e não use 30 pregões. Siga `$skip` quando houver paginação. Calcule a média com precisão decimal e registre período, contagem, método, URL e momento da consulta.

## Custo e comparação de otimização

`scripts/custo.py` aplica as fórmulas com `decimal.Decimal` e, com `--comparar`, avalia o limiar de 30% sem arredondamento prévio. Fórmulas:

```text
custo_usd = Decimal(bytes_base) / Decimal(2**40) * tarifa_usd_por_tib
custo_brl = custo_usd * media_ptax_venda
reducao = (custo_canonica - custo_otimizada) / custo_canonica
```

Use `totalBytesProcessed` do dry run como base estimada ou `totalBytesBilled` de job concluído como base faturada bruta; rotule a origem. Tarifa on-demand e de armazenamento por região: veja a fotografia e as regras de revalidação em `custos-bigquery.md`. Não aplique margens arbitrárias. Custo canônico zero: percentual indefinido, sem economia demonstrável.

## Auditoria dos artefatos

`scripts/auditoria.py` varre a pasta do modelo e reporta: títulos das seções fixas, links relativos quebrados, IDs duplicados, `.sql` fora do mapa, referências a variantes descartadas e validade do YAML de controle. Equivalente manual: confira cada ponto da lista em `validacao.md`. Execute antes de solicitar G05 e corrija o que for erro local; pendência legítima permanece declarada, não escondida.
