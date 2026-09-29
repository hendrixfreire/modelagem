---
name: fichar-query
description: "Extrai a estrutura de uma query SQL ou de um model .sqlx do Dataform (fontes, CTEs, filtros, campos por bloco, saída final) e grava a ficha-query-<ID>.md em tabelas, sem análise. Use quando o usuário pedir para fichar, fichamento, mapear fontes e campos, extrair estrutura ou comparar versões de uma query. Não use para explicar, validar, comentar, otimizar ou reescrever a query."
disable-model-invocation: true
argument-hint: "[arquivo .sql | .sqlx] [--id ID]"
version: 0.7.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sql, fichamento, documentacao, extracao, dataform, bigquery]
    related_skills: [explicar-query, comentar-query]
---

# Fichar Query

Extraia as informações estruturais de uma query e grave tudo em `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md` com tabelas.

Esta skill só extrai. Não analise, não valide, não comente, não recomende, não reescreva a query.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Os nomes de ferramentas citados (`read_file`, `search_files`) seguem o Hermes. Use a ferramenta equivalente do ambiente atual para ler e buscar arquivos. Os scripts abaixo são Python puro e rodam em qualquer ambiente com shell.

## Referências (carregue sob demanda)

| Quando | Ler |
| --- | --- |
| Antes de gravar qualquer ficha (script ou manual) | [template.md](references/template.md) |
| Ao fichar à mão, ao conferir a saída do script ou ao tratar `.sqlx` e tipos | [regras-extracao.md](references/regras-extracao.md) |

## Vocabulário

- **Bloco:** cada `SELECT` que produz linhas. Inclui CTE, subquery, operando de `UNION` e `SELECT` principal.
- **Operando:** cada bloco que participa de uma `UNION` ou `UNION ALL`. Os operandos de nível mais alto são os que a `UNION` final da query une. Os operandos dentro de uma subquery são aninhados.
- **Rótulo de bloco:** nome curto, único e autoexplicativo, que dispensa legenda. Use o nome do objeto de origem do bloco. Bloco que lê subquery recebe `subquery`. Quando o mesmo objeto aparecer em mais de um bloco, acrescente `(ocorrência N)`.
- **Código de bloco:** identificador usado para referenciar o bloco em todo o documento. CTE recebe `CTE 01`, `CTE 02` e assim por diante, na ordem de declaração. Os demais blocos recebem `BL 01`, `BL 02` e assim por diante, na ordem de aparecimento na query. O bloco que produz a saída final recebe `SAÍDA`.
- **Regra de referência:** toda célula que aponta para outro bloco usa o código, nunca o rótulo. A definição do bloco usa `<código> — <rótulo>`, no título da subseção da seção 4 e na coluna `Bloco` da seção 2.

## Como executar

### Caminho padrão: script

`<pasta-desta-skill>` é a pasta que contém este `SKILL.md` (no Claude Code, `${CLAUDE_SKILL_DIR}`; nos demais ambientes, o diretório de onde a skill foi carregada).

```bash
python3 <pasta-desta-skill>/scripts/fichar_query.py \
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

Use quando o gate reprovar ou quando o script não cobrir a query. Siga o template e as regras de extração das referências.

1. Localize a query completa com `read_file` ou `search_files` (ou equivalente do ambiente).
2. Determine o ID nesta ordem: ID informado pelo usuário; nome do arquivo de origem sem extensão; pergunte ao usuário. Monte o nome do arquivo como `ficha-query - <projeto>.<dataset>.<tabela> - <ID>.md`, com a primeira tabela citada no `FROM`.
3. Determine o diretório de saída nesta ordem: diretório informado pelo usuário; diretório do arquivo de origem; subpasta `fichas-query/` do diretório de trabalho atual.

## Regras de geração

1. A ficha nasce **sempre** do arquivo da query. Nunca leia uma ficha para regerá-la. Leitores de arquivo truncam linhas grandes, perto de 2.000 caracteres, e devolvem o texto truncado com o marcador `... [truncated]`, que você gravaria de volta. Foi assim que uma expressão de 6.497 caracteres virou 2.015 dentro do arquivo.
2. Grave o conteúdo em NFC. O SQL de origem pode trazer acentos decompostos (NFD), e isso quebra busca e diff.
3. Expressão acima de `--limite-expressao` sai da tabela: a célula `Expressão` recebe `E1`, `E2` e assim por diante, e a fórmula literal vai para a seção 6.
4. Escape `|` como `\|` dentro das células. Mantenha cada célula em uma única linha.
5. Só títulos e tabelas entram no arquivo.

## Comparar versões da query

```bash
python3 <pasta-desta-skill>/scripts/comparar_fichas.py <ficha-antiga.md> <ficha-nova.md>
```

Mostra blocos, campos e filtros que entraram, saíram ou mudaram entre duas fichas. Use para detectar drift do modelo entre versões.

## O que o script não cobre

- Use o caminho manual quando uma CTE contiver `UNION ALL`: o gerador atual perde o nome e o código do contêiner. Registre a CTE na seção 2 e cada operando na seção 4, com códigos próprios.
- Confira o resultado contra o SQL mesmo quando o gate aprovar: o gerador atual pode incluir CTEs como fontes físicas, usar um código `BL` para o consumidor final e produzir conferência de posição para blocos que não participam da mesma união. O gate estrutural não detecta esses casos.

O script cobre `SELECT` com `WITH`, `UNION` e `UNION ALL`, subquery no `FROM`, `JOIN`, filtros de nível de bloco e `.sqlx`. Nesses casos o gate reprova e o script não grava: `UNNEST`, `LATERAL`, `PIVOT`, `MERGE`, `CREATE TABLE AS`, subquery na lista de campos e qualquer bloco que ele não consiga balancear. Nesse caso, fiche à mão pelas regras de extração.

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
