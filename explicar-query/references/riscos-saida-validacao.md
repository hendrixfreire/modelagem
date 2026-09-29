# Riscos, saída final, validação e pergunta final

### 5. Avalie riscos semânticos

Avalie nesta prioridade:

1. **Granularidade:** a saída mantém o contrato esperado?
2. **Multiplicação:** algum `JOIN`, `UNNEST` ou `UNION ALL` pode duplicar entidades ou inflar métricas?
3. **Perda de registros:** filtros e tipos de junção removem linhas intencionalmente?
4. **Deduplicação:** qual chave define duplicidade, qual registro vence e o desempate é determinístico?
5. **`NULL`:** diferencie ausência, zero e texto vazio; verifique `COUNT(*)` versus `COUNT(campo)`, `COALESCE`, `CASE` e filtros sobre campos da direita de `LEFT JOIN`.
6. **Datas:** confira fuso, tipo `DATE`/`DATETIME`/`TIMESTAMP`, limites inclusivos e exclusivos e períodos parciais.
7. **Métricas:** confirme fórmula, unidade, período, população e possibilidade de duplicação antes de `SUM`, `COUNT` ou média.
8. **Performance e custo:** avalie somente após a correção lógica; procure `SELECT *`, leitura sem filtro de partição, agregação ou ordenação repetida, `CROSS JOIN` e processamento desnecessário.

Diferencie em cada achado:

- **erro confirmado:** o SQL contradiz o contrato ou o contexto;
- **risco possível:** depende de schema, cardinalidade ou dados não disponíveis;
- **preferência de estilo:** melhora leitura, mas não muda o resultado.

### 6. Descreva a saída final

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

### 7. Proponha um plano de validação

Sem executar a query, liste as verificações mínimas que provariam o contrato. Adapte-as ao dialeto e aos campos reais; não invente identificadores. Considere:

- `COUNT(*)` por etapa para localizar perdas ou explosões de linhas;
- `COUNT(DISTINCT chave)` para comparar entidades com linhas;
- agrupamento pela chave final com `HAVING COUNT(*) > 1` para testar unicidade;
- `COUNTIF(campo IS NULL)` ou equivalente para medir ausência;
- `MIN(data)` e `MAX(data)` para confirmar cobertura temporal;
- anti-join para identificar registros sem correspondência;
- reconciliação de métricas antes e depois de junções;
- amostras de casos extremos, como empate na deduplicação e divisão por zero.

Apresente cada teste com três itens: **hipótese**, **consulta ou verificação** e **resultado esperado**. Não execute nada, salvo pedido explícito e acesso autorizado.

### 8. Faça a pergunta final

Depois de entregar toda a avaliação, pergunte:

**“Você gostaria que eu sugerisse uma nova estrutura para a query, com foco em minimalismo, facilidade de leitura, comentários e organização?”**

Ofereça as opções **“Sim, sugerir nova estrutura”** e **“Não, manter somente a avaliação”**. Use `clarify` quando disponível. Não reescreva a query antes da resposta positiva.

