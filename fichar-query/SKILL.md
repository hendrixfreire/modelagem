---
name: fichar-query
description: Use ao fichar uma query SQL ou um model .sqlx do Dataform. Gera ficha-query-<ID>.md com fontes, blocos, filtros, campos por bloco e saída final, sem análise.
version: 0.6.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sql, fichamento, documentacao, extracao, dataform, bigquery]
    related_skills: [explicando_query, validacao-semantica-sql, bigquery-cost-estimation]
---

# Fichar Query

Extraia as informações estruturais de uma query e grave tudo em `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md` com tabelas.

Esta skill só extrai. Não analise, não valide, não comente, não recomende, não reescreva a query.

## Vocabulário

- **Bloco:** cada `SELECT` que produz linhas. Inclui CTE, subquery, operando de `UNION` e `SELECT` principal.
- **Operando:** cada bloco que participa de uma `UNION` ou `UNION ALL`. Os operandos de nível mais alto são os que a `UNION` final da query une. Os operandos dentro de uma subquery são aninhados.
- **Rótulo de bloco:** nome curto, único e autoexplicativo, que dispensa legenda. Use o nome do objeto de origem do bloco. Bloco que lê subquery recebe `subquery`. Quando o mesmo objeto aparecer em mais de um bloco, acrescente `(ocorrência N)`.
- **Código de bloco:** identificador usado para referenciar o bloco em todo o documento. CTE recebe `CTE 01`, `CTE 02` e assim por diante, na ordem de declaração. Os demais blocos recebem `BL 01`, `BL 02` e assim por diante, na ordem de aparecimento na query. O bloco que produz a saída final recebe `SAÍDA`.
- **Regra de referência:** toda célula que aponta para outro bloco usa o código, nunca o rótulo. A definição do bloco usa `<código> — <rótulo>`, no título da subseção da seção 4 e na coluna `Bloco` da seção 2.

## Como executar

### Caminho padrão: script

```bash
python3 ~/.agents/skills/modelagem/fichar-query/scripts/fichar_query.py \
  "<arquivo.sql|arquivo.sqlx>" [--id ID] [--out-dir DIR] \
  [--schema-json ARQ.json] [--limite-expressao 300]
```

- `--id` padrão: nome do arquivo sem extensão. `--out-dir` padrão: `fichas-query/` no diretório atual.
- Nome do arquivo: `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md`, onde a tabela é a **primeira citada no `FROM`**, na ordem de aparecimento dos blocos. O ID entra no fim para duas queries da mesma tabela não se sobrescreverem. Com `--sem-id`, o nome fica `ficha-query - <projeto>.<dataset>.<tabela>.md`.
- Em `.sqlx`, a tabela do nome é o próprio nome do model, porque o `FROM` traz `ref()`.
- Saída `0`: gate aprovado e ficha gravada. Saída `1`: gate reprovado e **nada é gravado**.
- O script imprime o caminho completo do arquivo gravado. Informe esse caminho na resposta final.

O gate do script reprova quando encontra: tabela com número de colunas variável, `[truncated]` no conteúdo, texto fora de título ou tabela, seção 5 fora de sequência, referência a bloco sem definição, saída final sem nenhum campo.

### Caminho manual

Use quando o gate reprovar ou quando o script não cobrir a query. Siga as regras deste documento.

1. Localize a query completa com `read_file` ou `search_files`.
2. Determine o ID nesta ordem: ID informado pelo usuário; nome do arquivo de origem sem extensão; pergunte ao usuário. Monte o nome do arquivo como `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md`, com a primeira tabela citada no `FROM`.
3. Determine o diretório de saída nesta ordem: diretório informado pelo usuário; diretório do arquivo de origem; subpasta `fichas-query/` do diretório de trabalho atual.

## Regras de geração

1. A ficha nasce **sempre** do arquivo da query. Nunca leia uma ficha para regerá-la. Leitores de arquivo truncam linhas grandes, perto de 2.000 caracteres, e devolvem o texto truncado com o marcador `... [truncated]`, que você gravaria de volta. Foi assim que uma expressão de 6.497 caracteres virou 2.015 dentro do arquivo.
2. Grave o conteúdo em NFC. O SQL de origem pode trazer acentos decompostos (NFD), e isso quebra busca e diff.
3. Expressão acima de `--limite-expressao` sai da tabela: a célula `Expressão` recebe `E1`, `E2` e assim por diante, e a fórmula literal vai para a seção 6.
4. Escape `|` como `\|` dentro das células. Mantenha cada célula em uma única linha.
5. Só títulos e tabelas entram no arquivo.

## Template

```markdown
# Ficha da query — <ID>

## 1. Fontes de dados

| # | Projeto | Dataset | Objeto | Alias na query | Referenciada em |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |

## 2. CTEs

| Bloco | CTE | Origem | Consumida por |
|---|---|---|---|
| CTE 01 |  |  |  |

## 3. Filtros aplicados

| # | Local | Cláusula | Condição | Coluna(s) | Valor ou limite |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |

## 4. Campos por bloco

### <código> — <rótulo do bloco>

| # | Campo exposto | Origem | Campo na origem | Expressão |
|---|---|---|---|---|
| 1 |  |  |  |  |

## 5. Saída final

| # | Bloco | Campo | Tipo |
|---|---|---|---|
| 1 |  |  |  |

## 6. Expressões

| # | Bloco | Campo exposto | Expressão |
|---|---|---|---|
| E1 |  |  |  |

## 7. Conferência de posição

### União de <códigos>

| Posição | <código> | <código> |
|---|---|---|
| 1 |  |  |

## 8. Configuração do modelo

| # | Item | Valor |
|---|---|---|
| 1 |  |  |
```

As seções 6, 7 e 8 só existem quando se aplicam. As seções 1 a 5 existem sempre.

## Regras de extração

### Seção 1 — Fontes de dados

- Registre todo objeto citado em `FROM`, `FROM` de subquery e `JOIN`, com o nome completo `projeto.dataset.objeto`.
- Separe o nome completo nas colunas `Projeto`, `Dataset` e `Objeto`.
- Quando a query omitir o projeto, escreva `não informado` na célula `Projeto`. Não complete o nome por suposição.
- Na coluna `Alias na query`, registre o alias usado no SQL. Deixe vazio quando não houver alias.
- Na coluna `Referenciada em`, registre o código do bloco que lê a fonte.
- Registre uma linha por ocorrência. O mesmo objeto lido em dois blocos gera duas linhas.
- Não registre CTE nesta seção. CTE pertence à seção 2.
- Não registre `UNNEST` nesta seção.

### Seção 2 — CTEs

- Liste todas as CTEs na ordem declarada, inclusive `WITH RECURSIVE`.
- Na coluna `Bloco`, escreva o código `CTE nn`. Na coluna `CTE`, escreva o nome da CTE.
- Na coluna `Origem`, liste as tabelas e os códigos dos blocos que a CTE lê.
- Na coluna `Consumida por`, liste cada bloco que lê esta CTE. Escreva `SAÍDA` quando a saída final a consumir. Escreva `não consumida` quando nada a ler.
- Quando a query não tiver CTE, escreva `sem CTE` na coluna `CTE` e `—` nas demais colunas, mantendo o cabeçalho.

### Seção 3 — Filtros aplicados

- Registre toda condição de `WHERE`, `ON`, `HAVING` e `QUALIFY`, inclusive dentro de subqueries, `EXISTS` e `IN`. Condições ligadas por `AND` de nível superior geram linhas separadas.
- Na coluna `Local`, escreva o código do bloco.
- Na coluna `Cláusula`, escreva `WHERE`, `ON`, `HAVING` ou `QUALIFY`.
- Na coluna `Condição`, reproduza a condição como está escrita na query. Preserve nomes, valores, aspas e operadores.
- Na coluna `Coluna(s)`, liste as colunas usadas na condição, sem nomes de função e sem nomes de tipo.
- Na coluna `Valor ou limite`, registre o lado direito do primeiro operador de comparação de nível superior. Deixe vazio quando a condição não tiver comparação.
- Não registre filtro de particionamento como caso especial. Ele é uma condição de `WHERE` como qualquer outra.
- Não registre `CASE` de agregação condicional nem `CASE` de ajuste de valor. Esses pertencem à seção 4.

### Seção 4 — Campos por bloco

- Crie uma subseção para cada bloco que enumere campos, na ordem de aparecimento na query, exceto os operandos de nível mais alto. Estes pertencem à seção 5.
- O título da subseção usa `<código> — <rótulo do bloco>`.
- A subseção cobre CTE, subquery e operando aninhado de `UNION`.
- Quando não existir bloco com lista de campos além dos operandos da saída final, escreva `sem bloco intermediário com lista de campos`.
- Colunas:
  - `#`: posição do campo dentro do bloco, começando em 1.
  - `Campo exposto`: o nome final do campo, ou seja, o nome renomeado quando houver alias.
  - `Origem`: o código do bloco lido ou o nome `projeto.dataset.objeto` da fonte lida.
  - `Campo na origem`: o nome do campo na origem quando o campo for lido direto. Deixe vazio quando o campo for criado ou transformado.
  - `Expressão`: a expressão literal quando o campo for criado ou transformado. Deixe vazio quando o campo for lido direto.
- Nunca escreva nome de campo e expressão na mesma célula.
- Copie a expressão sem resumo, sem redução e sem paráfrase.
- Para `*`, registre o texto literal do asterisco na coluna `Campo na origem` e deixe `Expressão` vazia. Inclua `EXCEPT` ou `REPLACE` quando houver.
- Uma célula longa é aceita no arquivo, mas acima do limite ela sai da tabela pela seção 6.

### Seção 5 — Saída final

- Registre a saída da `UNION` de nível mais alto da query.
- Colunas: `#`, `Bloco`, `Campo`, `Tipo`.
- A coluna `#` é sempre sequencial de 1 até N, sem lacuna. Toda linha da tabela recebe número, inclusive a linha do asterisco.
- Para cada operando de nível mais alto que enumere campos, registre os campos na ordem das posições.
- Para cada operando de nível mais alto que use `*`, registre uma linha com o texto literal do asterisco e deixe `Tipo` vazio.
- Na coluna `Bloco`, escreva `SAÍDA` para campo criado na saída final, ou o código do bloco lido quando a linha registrar `*`.
- Na coluna `Tipo`, preencha somente quando o tipo estiver explícito no SQL, por `CAST` ou `SAFE_CAST`, ou quando vier de `--schema-json`. Não infira tipo por literal, função, agregação ou nome do campo.

### Seção 6 — Expressões

- Uma linha por expressão acima do limite, na ordem de aparecimento.
- A coluna `#` recebe `E1`, `E2` e assim por diante. A coluna `Expressão` recebe a fórmula literal, sem resumo.

### Seção 7 — Conferência de posição

- Uma subseção por `UNION` em que todos os operandos enumeram campos e nenhum usa `*`.
- Uma linha por posição, com o nome do campo em cada operando. Escreva `—` quando o operando não tiver aquela posição.
- Esta seção existe porque `UNION ALL` casa campos por posição. É dado, não análise.

### Seção 8 — Configuração do modelo

- Só para `.sqlx`. Uma linha por chave de `config` e uma linha por `pre_operations` e `post_operations`, com o texto literal.

## Dataform

- `ref("x")` e `source("a","b")` contam como fontes. Na seção 1, o objeto recebe `x` ou `a.b`, e `Projeto` e `Dataset` recebem `modelo Dataform`.
- `config { type, partitionBy, clusterBy, … }` vai para a seção 8, uma linha por chave.
- `pre_operations` e `post_operations` vão para a seção 8, com o SQL literal.

## Tipos da saída final

A coluna `Tipo` fica vazia quando a query não declara o tipo. Para preencher com o schema real, gere antes um arquivo de schema e passe `--schema-json`:

```bash
bq show --schema --format=json <projeto>:<dataset>.<tabela> > schema.json
```

**Exija autorização explícita do usuário antes de rodar comando no `gcloud`.** O script nunca fala com o GCP: ele só lê o arquivo de schema local.

## Comparar versões da query

```bash
python3 ~/.agents/skills/modelagem/fichar-query/scripts/comparar_fichas.py <ficha-antiga.md> <ficha-nova.md>
```

Mostra blocos, campos e filtros que entraram, saíram ou mudaram entre duas fichas. Use para detectar drift do modelo entre versões.

## O que o script não cobre

- Use o caminho manual quando uma CTE contiver `UNION ALL`: o gerador atual perde o nome e o código do contêiner. Registre a CTE na seção 2 e cada operando na seção 4, com códigos próprios.
- Confira o resultado contra o SQL mesmo quando o gate aprovar: o gerador atual pode incluir CTEs como fontes físicas, usar um código `BL` para o consumidor final e produzir conferência de posição para blocos que não participam da mesma união. O gate estrutural não detecta esses casos.

O script cobre `SELECT` com `WITH`, `UNION` e `UNION ALL`, subquery no `FROM`, `JOIN`, filtros de nível de bloco e `.sqlx`. Nesses casos o gate reprova e o script não grava: `UNNEST`, `LATERAL`, `PIVOT`, `MERGE`, `CREATE TABLE AS`, subquery na lista de campos e qualquer bloco que ele não consiga balancear. Nesse caso, fiche à mão pelas regras deste documento.

## Proibições

- Não escreva resumo, introdução, conclusão, contexto, risco, gap, recomendação ou observação.
- Não escreva legenda, glossário ou lista de rótulos.
- Não escreva nenhum texto fora dos títulos e das tabelas do template.
- Não escreva parágrafo explicativo dentro das seções.
- Não reordene, não una e não omita seções.
- Não reescreva a query.
- Não execute a query.
- Não execute comando no `gcloud` nem consulta faturável sem autorização explícita.
- Não grave uma ficha quando o gate reprovar.
- Não invente projeto, dataset, tipo, nome de campo ou valor ausente no SQL.

## Verificação

Antes de entregar, confirme em silêncio:

- [ ] O arquivo se chama `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md` e o caminho completo foi informado.
- [ ] O gate do script aprovou, ou a ficha manual passou por todas as checagens abaixo.
- [ ] Toda fonte de `FROM`, `FROM` de subquery e `JOIN` aparece na seção 1, uma linha por ocorrência.
- [ ] Toda CTE declarada aparece na seção 2, na ordem da query.
- [ ] Toda condição de `WHERE`, `ON`, `HAVING` e `QUALIFY` aparece na seção 3.
- [ ] Todo bloco com lista de campos, exceto os operandos de nível mais alto, tem subseção na seção 4.
- [ ] Toda linha da seção 4 tem `Campo na origem` ou `Expressão` preenchido, nunca os dois.
- [ ] Todos os campos dos operandos de nível mais alto aparecem na seção 5.
- [ ] Todo bloco tem código único: `CTE nn`, `BL nn` ou `SAÍDA`.
- [ ] A coluna `#` da seção 5 é sequencial de 1 a N, sem lacuna.
- [ ] Toda referência a bloco, nas seções 1, 2, 3, 4 e 5, usa o código.
- [ ] Todo rótulo usado na seção 1 e na seção 3 existe como subseção da seção 4 ou como operando de nível mais alto da seção 5.
- [ ] As tabelas têm número de colunas constante dentro de cada seção.
- [ ] Não existe `[truncated]` no arquivo.
- [ ] O conteúdo está em NFC.
- [ ] Nenhum texto de análise foi gravado.
- [ ] Nenhum valor foi inventado.
