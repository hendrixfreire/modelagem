---
name: explicando_query
description: Explica queries SQL por CTE, linha, relação e saída.
disable-model-invocation: true
version: 0.1.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sql, cte, explicacao, documentacao]
    related_skills: []
---

# Explicando Query

Explique uma query SQL de forma rastreável. Mostre o papel de cada CTE, a transformação de cada linha lógica, as relações entre CTEs e o contrato da saída final.

## Quando usar

Use quando o usuário invocar `/explicando_query` e fornecer uma query SQL, um arquivo SQL ou uma referência recuperável para a query.

## Entrada e contexto

1. Localize e leia a query completa. Se o usuário indicar um arquivo, use `read_file`. Se indicar um símbolo ou projeto, use `search_files` antes de ler os arquivos relevantes.
2. Verifique se a conversa já contém contexto sobre objetivo de negócio, origem dos dados, granularidade, dialeto SQL ou resultado esperado.
3. Se não houver contexto anterior da query, interrompa a avaliação e pergunte ao usuário:

   **“Você gostaria de fornecer contexto sobre o objetivo da query antes da avaliação, ou devo seguir somente com o SQL?”**

   Ofereça duas opções: **“Fornecer contexto”** e **“Seguir sem contexto”**. Use `clarify` quando disponível.
4. Se o usuário escolher fornecer contexto, aguarde a resposta antes da avaliação. Se escolher seguir sem contexto, use somente evidências do SQL e identifique inferências como inferências.
5. Se houver contexto anterior suficiente, comece a avaliação sem repetir a pergunta.

A entrada está pronta quando a query completa e a decisão sobre contexto estiverem disponíveis.

## Procedimento

### 1. Identifique o contrato geral

Informe:

- dialeto SQL, somente quando identificável;
- objetivo aparente da query;
- fontes lidas;
- granularidade inicial e granularidade final;
- chaves de relação;
- filtros globais;
- destino ou consumidor, quando informado.

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

**Saída da CTE:** descreva campos, granularidade, unicidade esperada e papel da CTE na próxima etapa.

### 4. Explique as relações e a ordem

Após explicar todas as CTEs, consolide:

- dependência direta entre cada par de CTEs;
- campos transportados entre etapas;
- junções e possível efeito `1:1`, `1:N` ou `N:N`;
- filtros aplicados cedo ou tarde e seu efeito;
- agregações que mudam a granularidade;
- motivo da sequência escolhida.

Explique a ordem como uma cadeia de dependências e transformações. Não trate a ordem declarada como justificativa suficiente. Se uma etapa puder ser movida sem mudar o resultado, informe isso como observação, sem propor uma reescrita ainda.

### 5. Descreva a saída final

Informe primeiro a granularidade: o que uma linha representa.

Depois, crie uma tabela com uma linha para cada campo final e estas colunas:

| Campo | Origem | Transformação | Tipo provável | Significado | Regra de NULL | Observações |
|---|---|---|---|---|---|---|

Descreva todos os campos do `SELECT` final, inclusive campos vindos de `*`. Se `*` impedir uma enumeração segura, diga quais campos são identificáveis e marque o restante como dependente do schema da origem. Não invente nomes ou tipos.

Finalize a seção com:

- quantidade de linhas esperada, somente quando dedutível;
- ordenação garantida, se houver `ORDER BY` final;
- possíveis duplicidades;
- filtros ainda ativos na saída;
- limitações ou riscos semânticos encontrados.

### 6. Faça a pergunta final

Depois de entregar toda a avaliação, pergunte:

**“Você gostaria que eu sugerisse uma nova estrutura para a query, com foco em minimalismo, facilidade de leitura, comentários e organização?”**

Ofereça as opções **“Sim, sugerir nova estrutura”** e **“Não, manter somente a avaliação”**. Use `clarify` quando disponível. Não reescreva a query antes da resposta positiva.

## Formato da resposta

Use esta ordem:

1. **Resumo**
2. **Contrato geral da query**
3. **Mapa das CTEs**
4. **CTEs, uma por vez**
5. **Relações entre CTEs e motivo da sequência**
6. **Saída final e dicionário de campos**
7. **Gaps, riscos e inferências**
8. **Pergunta sobre nova estrutura**

Use português direto. Defina termos técnicos na primeira ocorrência. Preserve nomes de tabelas, CTEs, campos, funções e valores exatamente como aparecem na query.

## Limites

- Avalie sem executar a query, salvo se o usuário pedir execução e houver acesso autorizado ao ambiente.
- Não faça alterações no `gcloud` sem permissão explícita do usuário.
- Não afirme intenção de negócio sem evidência no SQL ou no contexto.
- Diferencie erro confirmado, risco possível e preferência de estilo.
- Não transforme a avaliação em otimização de performance. Cite performance somente quando a construção analisada tiver efeito direto e verificável.

## Verificação

Antes de concluir, confirme em silêncio:

- toda CTE foi explicada;
- toda linha executável foi coberta;
- todos os filtros e condições de junção foram explicados;
- toda transformação de campo foi descrita;
- toda window function foi explicada;
- toda relação e mudança de granularidade foi mapeada;
- a sequência das CTEs foi justificada;
- todos os campos finais identificáveis foram documentados;
- fatos e inferências estão separados;
- a pergunta final foi feita sem antecipar a reescrita.
