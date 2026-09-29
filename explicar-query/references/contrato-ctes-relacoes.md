# Contrato, CTEs e relações

### 1. Identifique o contrato geral

Comece pelo último `SELECT`, não pela primeira CTE. Informe:

- dialeto SQL, somente quando identificável;
- objetivo aparente da query;
- contrato da saída no formato: “uma linha representa [entidade], no nível de [dimensões], contendo [métricas]”;
- chave ou combinação de chaves esperada na saída;
- campos finais, agregações, filtros e ordenação final;
- fontes lidas;
- granularidade inicial e granularidade final;
- chaves de relação;
- filtros globais;
- destino ou consumidor, quando informado.

Se a granularidade não puder ser determinada, declare exatamente o que falta: schema, unicidade da chave, contexto de negócio ou conteúdo expandido por `*`.

Separe fatos visíveis no SQL de interpretações de negócio. Não invente regras ausentes.

### 2. Mapeie a sequência das CTEs

Liste as CTEs na ordem declarada. Para cada CTE, registre:

- CTEs ou tabelas de origem;
- campos recebidos;
- campos criados, alterados e removidos;
- granularidade de entrada e de saída;
- CTEs posteriores que a consomem.

Depois, descreva o fluxo no formato `origem → CTE → CTE → saída final`. Inclua ramificações e junções. O mapa está completo quando toda CTE declarada aparece no fluxo.

### 3. Explique cada CTE

Antes da explicação linha a linha, responda cinco perguntas para cada CTE:

1. De onde os dados vêm?
2. O que uma linha representa na entrada?
3. Qual é a transformação principal, resumida com um verbo: filtra, classifica, deduplica, agrega, junta ou expande?
4. A granularidade muda? Se muda, de quê para quê?
5. O que uma linha representa na saída e qual é sua chave esperada?

Para cada CTE, na ordem da query, use esta estrutura:

#### `<nome_da_cte>`

**Função:** explique o que a CTE produz e qual problema ela resolve.

**Entradas e relações:** informe a origem dos dados, as chaves usadas e a cardinalidade esperada quando ela puder ser deduzida. Explique como e por que a CTE usa dados de CTEs anteriores.

**Filtros:** para cada condição de `WHERE`, `ON`, `HAVING`, `QUALIFY` ou filtro dentro de uma expressão:

- reproduza ou referencie a condição;
- explique quais registros ela mantém ou remove;
- explique por que ela existe, quando isso estiver sustentado pelo SQL ou pelo contexto;
- aponte efeitos de `NULL`, precedência de `AND`/`OR`, limites de datas e mudança de cardinalidade.

**Linha a linha:** numere ou cite as linhas da query. Explique cada linha executável e cada expressão. Para linhas apenas de formatação ou pontuação, associe-as à expressão correspondente. Não ignore:

- `SELECT`, aliases e campos diretos;
- `CASE`, `IF`, `COALESCE`, `NULLIF`, casts e funções de data ou texto;
- cálculos, agregações e tratamento de `NULL`;
- `FROM`, `JOIN` e tipo de junção;
- condições de `ON`;
- `WHERE`, `GROUP BY`, `HAVING`, `QUALIFY`, `ORDER BY` e `LIMIT`;
- `DISTINCT`, `UNION`, `UNION ALL`, `UNNEST`, pivôs e subqueries.

Para cada cláusula usada no tratamento de campos, explique:

1. o valor de entrada;
2. a transformação aplicada;
3. o motivo técnico ou de negócio;
4. o valor de saída;
5. o comportamento para `NULL`, valor inválido ou ausência de correspondência.

**Window functions:** para cada expressão com `OVER`, explique:

- a função usada;
- o objetivo;
- o conjunto definido por `PARTITION BY`;
- a ordem definida por `ORDER BY`;
- o frame, explícito ou padrão, quando ele muda o resultado;
- por que uma window function foi usada em vez de agregação comum;
- como o resultado é usado depois, inclusive em `QUALIFY` ou filtros externos.

**Saída da CTE:** descreva campos, granularidade, chave ou combinação de chaves, unicidade esperada e papel da CTE na próxima etapa.

Mantenha também um quadro de granularidade:

```text
Etapa                  Uma linha representa              Chave esperada
<origem ou CTE>        <entidade e dimensões>            <campo(s)>
```

Marque explicitamente toda construção que pode mudar o número ou o significado das linhas: `GROUP BY`, `DISTINCT`, `JOIN`, `UNION ALL`, `UNNEST`, pivôs, funções de janela seguidas de filtro e subqueries correlacionadas.

### 4. Explique as relações e a ordem

Após explicar todas as CTEs, consolide:

- dependência direta entre cada par de CTEs;
- campos transportados entre etapas;
- junções e possível efeito `1:1`, `1:N` ou `N:N`;
- filtros aplicados cedo ou tarde e seu efeito;
- agregações que mudam a granularidade;
- motivo da sequência escolhida.

Explique a ordem como uma cadeia de dependências e transformações. Não trate a ordem declarada como justificativa suficiente. Se uma etapa puder ser movida sem mudar o resultado, informe isso como observação, sem propor uma reescrita ainda.

Classifique cada relação como `1:1`, `1:N`, `N:1`, `N:N` ou indeterminada. Não deduza cardinalidade apenas porque as colunas têm o mesmo nome. Para cada `JOIN`, diga:

- a chave usada em cada lado;
- se a chave parece única;
- se o número de linhas pode aumentar;
- o que acontece com registros sem correspondência;
- se filtros posteriores anulam o efeito preservador de um `LEFT JOIN`.

