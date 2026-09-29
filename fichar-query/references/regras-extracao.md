# Regras de extração por seção

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

