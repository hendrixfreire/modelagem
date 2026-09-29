# Plano de execução e monitoramento

Estes comandos são de leitura. Consultas em `INFORMATION_SCHEMA` também processam bytes: defina limite de bytes e a região correta, e obtenha autorização antes de executar.

## Estimar sem executar

```bash
bq query --use_legacy_sql=false --dry_run 'SELECT ... '
```

Informa os bytes que a query processaria. Compare antes e depois na mesma região, com os mesmos parâmetros. Em tabela clusterizada, o dry run tende a ser um limite superior.

## Descobrir partição e clustering de uma tabela

```bash
bq show --format=prettyjson <projeto>:<dataset>.<tabela>
```

Procure `timePartitioning`, `rangePartitioning`, `clustering` e `requirePartitionFilter` no resultado. Sem esses campos, a tabela não é particionada nem clusterizada.

Para partições existentes:

```sql
SELECT partition_id, total_rows, total_logical_bytes
FROM `<projeto>.<dataset>.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = '<tabela>'
ORDER BY partition_id DESC
LIMIT 30;
```

## Ler o plano de um job

- Na console: aba `Execution graph` do job. Cada estágio mostra tempo médio e máximo, bytes lidos e gravados, linhas.
- Sinais de problema:
  - estágio com tempo máximo muito acima da média: chave desbalanceada;
  - estágio de junção com linhas de saída muito maiores que a soma das entradas: multiplicação;
  - bytes lidos altos em estágio de leitura: poda de partição ou clustering ausente;
  - grande volume embaralhado antes de agregação: agregar antes, ou reduzir colunas.
- Por linha de comando: `bq show --format=prettyjson -j <job_id>` traz `statistics.query.queryPlan` e `totalBytesBilled`.

## Jobs mais caros (por bytes)

```sql
SELECT
    job_id,
    user_email,
    creation_time,
    total_bytes_billed,
    total_slot_ms,
    LEFT(query, 200) AS inicio_query
FROM `region-<regiao>`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
ORDER BY total_bytes_billed DESC
LIMIT 20;
```

Substitua `<regiao>` pela região dos dados (por exemplo `us` ou `southamerica-east1`). Exige permissão de visualização de jobs do projeto. Em modelo de capacidade, ordene por `total_slot_ms`.

## Armazenamento por tabela

```sql
SELECT table_name, total_logical_bytes, active_logical_bytes
FROM `region-<regiao>`.INFORMATION_SCHEMA.TABLE_STORAGE
WHERE table_schema = '<dataset>'
ORDER BY total_logical_bytes DESC
LIMIT 20;
```

Use para decidir onde particionar, clusterizar ou criar tabela resumo. Tabelas grandes e muito consultadas dão mais retorno.

## Metodologia

1. Identifique as queries mais caras (jobs) ou a query indicada pelo usuário.
2. Meça a linha de base (dry run e, se autorizado, job real com cache desligado).
3. Analise o plano e escolha a técnica de maior impacto.
4. Aplique, prove equivalência e meça de novo.
5. Registre o ganho em bytes e a técnica. Volte ao passo 3 se ainda houver estágio dominante.
