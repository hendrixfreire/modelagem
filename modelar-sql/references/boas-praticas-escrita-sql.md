# Boas práticas na escrita de queries

Referência de estilo e segurança para toda `.sql` desta skill: canônica, teste e variante. Leia ao redigir a query e ao revisá-la antes do gate.

Fonte: transcrição integral de dois vídeos, lida em 2026-09-15.

- `https://youtu.be/hhyqtLh6Oag` — 11:02, canal Database Star, 20 dicas.
- `https://youtu.be/p5PKnqGyDaE` — 13:40, 7 truques.

Onde a regra já vive em outro arquivo, esta referência aponta o arquivo e não repete a regra. Em conflito com uma invariante da `SKILL.md`, vale a invariante.

## Estilo

- Escreva palavras-chave em maiúsculo (`SELECT`, `FROM`, `JOIN`, `WHERE`), identificadores em minúsculo e identação de 4 espaços.
- Uma coluna por linha, filtro em linha própria. Mantenha o mesmo padrão em toda a pasta do modelo.
- Use alias de coluna com `AS` em toda coluna calculada. O alias serve ao leitor e à ferramenta de consumo, sobretudo quando a coluna tem função.
- Use alias de tabela curto em toda tabela. O alias é obrigatório quando a mesma tabela entra duas vezes na query.

## Estrutura

- Separe a query em CTEs nomeadas, uma responsabilidade por CTE. Subquery aninhada vira CTE. As demais regras de CTE e legibilidade da canônica estão na invariante 9 da `SKILL.md`.
- Prefira `JOIN` explícito a subquery no `SELECT`. O `JOIN ... ON` mostra a ligação e a origem de cada coluna; a subquery esconde as duas.
- Ligue tabelas com `JOIN ... ON` e colunas nomeadas nos dois lados. `NATURAL JOIN` e `USING` ligam por igualdade de nome: renomear ou acrescentar coluna muda o resultado sem aviso na query.
- `WHERE` filtra linhas. Junção entre tabelas acontece no `JOIN ... ON`. Uma condição de junção no `WHERE` pode faltar sem erro de sintaxe, e junção externa não existe nesse formato.
- Guarde a mesma lógica em um lugar só, na CTE. View e tabela temporária não estão no caminho permitido desta skill (invariante 4).
- Query repetida vira artefato com ID estável `qNN` e entra no mapa de queries, seção 13 do `MODEL_SPECS.md`.
- Junção não é lentor por natureza. Meça com dry run antes de reescrever a query para evitar junção.

## Colunas e linhas

- Selecione colunas explícitas em toda entrega, com alias, conforme a invariante 9. `SELECT *` lê coluna que a query não usa e muda o resultado quando o schema muda.
- Em consulta de exploração, restrinja as linhas com `LIMIT`.

## Agregação e nulos

- `COUNT(*)` conta linhas. `COUNT(coluna)` conta valores não nulos da coluna. Escolha pela intenção da regra de negócio `RNxx` e registre a escolha no teste correspondente.
- `DISTINCT` atende pedido de valor único. Duplicação de junção se resolve na junção, conforme a invariante 9.
- Agregação única ou window function no lugar de subquery correlacionada, preservando granularidade e multiplicidade: ver `otimizacao-sql.md`.

## Leitura e custo no BigQuery

- BigQuery não usa índice. Coluna de partição e clustering cumprem esse papel: filtro direto na coluna de partição, sem função envolvendo a coluna. Toda técnica de redução de leitura está em `otimizacao-sql.md`.
- Antes de propor variante otimizada, leia o plano de execução. No BigQuery o plano fica no detalhe do job, na aba `Execution graph` da console; o script de leitura não consulta plano. Declare essa falta de acesso quando o plano decidir a escolha.

## Itens dos vídeos fora desta skill

| Item dos vídeos | Motivo |
| --- | --- |
| Versionar scripts no Git | Invariante 11 proíbe Git nesta skill; o histórico vive na seção 14 do `MODEL_SPECS.md`. |
| Atalhos de teclado e recursos do editor | Ação humana no editor. Não altera a query. |
| Reuso por view ou tabela temporária | Invariante 4 proíbe DDL e tabela temporária; o reuso fica na CTE. |
| Chave primária surrogada, normalização, dado em um lugar só | Modelagem de esquema relacional. Esta skill escreve leitura sobre esquema existente. |
| Data dictionary do banco | Inventário de fontes na seção 5 do `MODEL_SPECS.md`; tamanho e storage em `comandos.md` (`INFORMATION_SCHEMA.TABLE_STORAGE`). |
| Diagrama de entidade e relação, documentação de colunas | `MODEL_SPECS.md` seções 5 e 8, `GLOSSARIO.md` e `CONTEXT.md`. |
| Rodar `UPDATE` ou `DELETE` como `SELECT` antes | Invariante 4 proíbe DML. O equivalente aqui é o teste de leitura em `testes/`. |
