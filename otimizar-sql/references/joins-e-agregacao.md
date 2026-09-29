# Joins, agregações, janelas e deduplicação

Toda reescrita abaixo exige prova de equivalência. Diferenças de multiplicidade e de `NULL` são as mais comuns.

## Joins

- Junte por chaves do mesmo tipo nos dois lados. Chave `INT64` é mais barata que `STRING`. Evite `CAST` na condição de junção.
- Reduza cada lado antes do join: filtre, selecione só as colunas necessárias e agregue quando a granularidade permitir.
- Evite `CROSS JOIN` e junção por desigualdade ou por `OR` na condição `ON`. Elas geram produto parcial ou total. Se a desigualdade for inevitável, restrinja cada lado antes.
- Junção explode linhas quando a chave não é única. Verifique unicidade com `GROUP BY chave HAVING COUNT(*) > 1` antes de otimizar.
- O otimizador reordena joins. Confirme no plano (`references/plano-e-monitoramento.md`) em vez de reordenar por hábito.
- Chave desbalanceada (poucos valores concentram muitas linhas) deixa um slot mais lento que os outros. O plano mostra isso como estágio com máximo muito maior que a média. Filtre o valor dominante ou trate-o em separado.
- `LEFT JOIN` para `INNER JOIN`, `IN` para join e `OR` para `UNION ALL` mudam o resultado quando há linhas sem correspondência ou duplicidade. Use só com prova de equivalência.

## Subconsultas

- Substitua subconsulta correlacionada por window function ou agregação única com join:

```sql
-- Antes: correlacionada, reavaliada por linha
SELECT p.id_produto, p.preco
FROM produtos AS p
WHERE p.preco > (
    SELECT AVG(p2.preco)
    FROM produtos AS p2
    WHERE p2.id_categoria = p.id_categoria
);

-- Depois: uma passada com window function
SELECT id_produto, preco
FROM (
    SELECT
        id_produto,
        preco,
        AVG(preco) OVER (PARTITION BY id_categoria) AS preco_medio_categoria
    FROM produtos
)
WHERE preco > preco_medio_categoria;
```

- Prefira `EXISTS` a `IN` com subconsulta grande quando só interessa a existência, respeitando a semântica de `NULL`.
- `NOT IN` com subconsulta que devolve `NULL` elimina todas as linhas. Use `NOT EXISTS`.

## Agregação

- Junte várias contagens condicionais em uma única leitura:

```sql
SELECT
    COUNTIF(status = 'pendente') AS qtd_pendente,
    COUNTIF(status = 'enviado') AS qtd_enviado,
    COUNTIF(status = 'entregue') AS qtd_entregue
FROM pedidos;
```

- Agregue antes de juntar para reduzir o volume do join, sem mudar a granularidade final.
- `COUNT(DISTINCT x)` exato é caro em volume alto. A versão aproximada exige aprovação (`leitura-e-custo.md`).
- `GROUP BY` em muitas colunas de alta cardinalidade custa embaralhamento. Agrupe só pelo necessário.

## Deduplicação e janelas

- Para manter um registro por chave, prefira `QUALIFY ROW_NUMBER() OVER (PARTITION BY chave ORDER BY critério, desempate) = 1`. Sempre inclua desempate determinístico.
- Alternativa: `ARRAY_AGG(t ORDER BY critério DESC LIMIT 1)[OFFSET(0)]` com `GROUP BY chave`, que evita ordenar a partição inteira.
- `PARTITION BY` com chave de baixíssima cardinalidade concentra tudo em um slot. Isso aparece no plano como estágio lento.
- Um `ORDER BY` dentro de janela ordena a partição inteira. Não repita a mesma janela com definições diferentes: declare uma janela nomeada (`WINDOW w AS (...)`) e reutilize.

## UNNEST e tipos aninhados

- `UNNEST` multiplica linhas. Filtre antes quando possível e confira a granularidade da saída.
- Leia só os campos aninhados necessários (`t.endereco.cidade`), e não o `STRUCT` inteiro.
- Prefira `STRUCT` e `ARRAY` a junções quando a relação pai-filho é sempre lida junta. Isso é decisão de modelagem, então vai como recomendação.

## Ordenação e limite

- `ORDER BY` global sobre tabela grande é caro e roda em um só nó no estágio final. Use só na saída final e, se possível, com `LIMIT`.
- `ORDER BY ... LIMIT N` é barato comparado a `ORDER BY` sem limite.
- Paginação por `OFFSET` lê e descarta as linhas anteriores. Use paginação por chave (`WHERE id > @ultimo_id ORDER BY id LIMIT N`).
