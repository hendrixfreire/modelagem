---
name: explicar-query
description: "Explica e avalia uma query SQL de ponta a ponta: contrato da saída, mapa e explicação de cada CTE, cardinalidade dos joins, riscos semânticos e plano de validação, sem executar nada. Use quando o usuário invocar /explicar-query ou pedir para explicar, entender, ler ou avaliar uma query específica. Não use para otimização isolada de performance nem para extração estrutural sem análise (use fichar-query)."
disable-model-invocation: true
argument-hint: "[arquivo .sql | query | referência]"
version: 0.3.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sql, cte, explicacao, documentacao]
    related_skills: [fichar-query, comentar-query]
---

# Explicar Query

Explique uma query SQL de forma rastreável e avalie sua correção semântica. Trate a query como uma linha de produção: tabelas são fontes, CTEs são etapas, `JOIN`s conectam conjuntos, filtros removem registros e o `SELECT` final define o produto entregue.

Não comece pela primeira linha. Descubra primeiro o contrato da saída, depois mapeie o fluxo e só então inspecione expressões e riscos.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Os nomes de ferramentas citados (`read_file`, `search_files`, `clarify`) seguem o Hermes. Antes de agir, identifique o ambiente atual e use a ferramenta equivalente disponível nele para ler, buscar arquivos e fazer perguntas ao usuário.

## Quando usar

Use quando o usuário invocar `/explicar-query` e fornecer uma query SQL, um arquivo SQL ou uma referência recuperável para a query, ou quando pedir para aprender a ler, explicar ou avaliar uma query específica.

Não use para otimização isolada de performance sem avaliação semântica: uma query rápida ainda pode produzir dados errados.

## Referências (carregue sob demanda)

| Etapa | Ler |
| --- | --- |
| Passos 1 a 4: contrato geral, mapa das CTEs, explicação de cada CTE, relações e ordem | [contrato-ctes-relacoes.md](references/contrato-ctes-relacoes.md) |
| Passos 5 a 8: riscos semânticos, saída final, plano de validação, pergunta final | [riscos-saida-validacao.md](references/riscos-saida-validacao.md) |

Leia a primeira referência antes de começar a análise e a segunda antes de avaliar riscos.

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

### Estratégia de leitura em quatro passadas

Analise nesta ordem, mesmo que a query esteja escrita de outra forma:

1. **Contrato:** comece pelo `SELECT` final e defina o que uma linha representa.
2. **Mapa:** identifique fontes, CTEs, ramificações e dependências sem entrar nos detalhes das expressões.
3. **Inspeção:** percorra cada CTE e acompanhe mudanças de granularidade, chaves, filtros e campos.
4. **Validação:** procure multiplicação, perda de registros, `NULL`, limites de datas, deduplicação e incoerência de métricas; performance vem por último.

Use como ordem lógica de leitura, quando aplicável: `FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` → funções de janela → `QUALIFY` → `SELECT` → `DISTINCT` → `ORDER BY` → `LIMIT`. Avise que essa é uma ferramenta mental e que detalhes da execução dependem do dialeto e do otimizador.


Os oito passos, na ordem: (1) contrato geral, (2) mapa das CTEs, (3) explicação de cada CTE, (4) relações e ordem, (5) riscos semânticos, (6) saída final, (7) plano de validação, (8) pergunta final. Detalhes nas referências.

## Formato da resposta

Use esta ordem:

1. **Resumo**
2. **Contrato geral da query**
3. **Mapa das CTEs**
4. **Quadro de granularidade e chaves**
5. **CTEs, uma por vez**
6. **Relações entre CTEs e motivo da sequência**
7. **Saída final e dicionário de campos**
8. **Erros confirmados, riscos possíveis e inferências**
9. **Plano de validação**
10. **Pergunta sobre nova estrutura**

Use português direto. Defina termos técnicos na primeira ocorrência. Preserve nomes de tabelas, CTEs, campos, funções e valores exatamente como aparecem na query.

## Limites

- Avalie sem executar a query, salvo se o usuário pedir execução e houver acesso autorizado ao ambiente.
- Não faça alterações no `gcloud` sem permissão explícita do usuário.
- Não afirme intenção de negócio sem evidência no SQL ou no contexto.
- Diferencie erro confirmado, risco possível e preferência de estilo.
- Não transforme a avaliação em otimização de performance. Avalie custo e performance somente depois da semântica e cite-os quando houver construção relevante ou evidência do plano de execução.
- Não use `DISTINCT` como explicação suficiente para duplicidades; identifique a etapa que pode tê-las criado.
- Não trate o nome de uma coluna como prova de unicidade ou cardinalidade.
- Não confunda ordem de leitura lógica com garantia da ordem física de execução do banco.

## Verificação

Antes de concluir, confirme em silêncio:

- toda CTE foi explicada;
- toda linha executável foi coberta;
- todos os filtros e condições de junção foram explicados;
- toda transformação de campo foi descrita;
- toda window function foi explicada;
- toda relação e mudança de granularidade foi mapeada;
- cada `JOIN` tem cardinalidade classificada ou marcada como indeterminada;
- chaves esperadas e possíveis multiplicações foram registradas;
- a sequência das CTEs foi justificada;
- todos os campos finais identificáveis foram documentados;
- `NULL`, datas, deduplicação e métricas foram avaliados;
- o plano de validação cobre unicidade, volume, cobertura e reconciliação;
- fatos, erros confirmados, riscos possíveis e preferências de estilo estão separados;
- a pergunta final foi feita sem antecipar a reescrita.
