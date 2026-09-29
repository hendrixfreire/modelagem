# Anti-padrões e alternativas

| Anti-padrão | Efeito no BigQuery | Alternativa |
| --- | --- | --- |
| `SELECT *` em tabela larga | Lê todas as colunas e muda com o schema | Colunas explícitas, ou `SELECT * EXCEPT (...)` em exploração |
| Função sobre coluna de partição (`DATE(ts)`, `CAST`, `FORMAT_DATE`) | Pode impedir a poda de partições | Comparar a coluna direto com constante ou parâmetro; conferir no dry run |
| `LIMIT` para "economizar" | Não reduz bytes em tabela sem clustering | Filtro de partição, `TABLESAMPLE` ou pré-visualização |
| Subconsulta correlacionada | Reavaliação por linha | Window function ou agregação com join |
| `SELECT DISTINCT` para esconder duplicação de join | Ordenação e embaralhamento extras, resultado ocultando o erro | Corrigir a chave ou a granularidade do join |
| `ORDER BY` global sem `LIMIT` | Ordenação em um só nó | Ordenar só na saída final; usar `LIMIT` |
| Junção por `OR` ou desigualdade | Produto parcial ou total | Reduzir cada lado antes; separar em `UNION ALL` com prova de equivalência |
| `CROSS JOIN` sem filtro | Explosão de linhas | Condição de junção explícita |
| `NOT IN (subconsulta)` | Vazio se houver `NULL`; plano ruim | `NOT EXISTS` |
| `REGEXP_CONTAINS` e `LIKE '%x%'` em tabela grande | Varredura completa | Filtro de partição antes; `SEARCH INDEX` como DDL |
| UDF em JavaScript sobre volume alto | Lento, sem otimização do plano | Função SQL nativa ou UDF SQL |
| Mesma CTE referenciada várias vezes com custo alto | Pode ser reavaliada a cada referência | Reduzir a CTE; recomendar tabela intermediária como DDL |
| Tabelas fragmentadas por data (`tabela_*`) | Metadados por fragmento e poda limitada | Tabela particionada |
| `CAST` na condição de junção | Impede uso eficiente da chave | Padronizar o tipo na origem |
| DML linha a linha (`INSERT` em loop, `UPDATE` pontual repetido) | Cada instrução é um job com cota e custo | Uma instrução em lote ou `MERGE`; fora do escopo de somente leitura |
| `COUNT(DISTINCT)` exato em volume alto sem necessidade | Embaralhamento pesado | `APPROX_COUNT_DISTINCT` com aprovação do usuário |
| Consulta repetida idêntica em dashboards | Reprocessa a cada abertura | Tabela resumo, view materializada ou cache de BI (recomendações) |

## O que não se aplica ao BigQuery

Não recomende estas técnicas de bancos relacionais tradicionais:

- criar índices B-tree (`CREATE INDEX`), índices cobrindo, parciais ou compostos;
- `INCLUDE`, dicas de índice e de plano;
- tabelas temporárias como padrão de reuso (dentro de `modelar-sql` são proibidas);
- `OFFSET/FETCH` como paginação eficiente;
- prepared statements para desempenho.

O equivalente no BigQuery é partição, clustering, tabelas resumo, views materializadas e `SEARCH INDEX`.
