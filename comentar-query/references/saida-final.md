# Bloco de saída final


Insira um bloco de comentários imediatamente antes do SELECT final. Numere-o como a próxima etapa do fluxo: `N. saída_final`. Explique a estrutura e o comportamento efetivos da query, incluindo regras herdadas das CTEs. Mantenha os detalhes de cada cálculo junto à expressão correspondente; não repita toda a análise das etapas.

#### Inventário e contagem de colunas

- Conte as colunas finais com ferramentas, preferencialmente a partir da árvore sintática e dos metadados disponíveis. Não conte vírgulas: funções e estruturas também contêm vírgulas.
- Informe `Colunas: T no total = D dimensões + M métricas + A campos técnicos/auditoria`. Omita a categoria técnica quando ela não existir. Conte cada coluna uma única vez e confirme a soma com código.
- **Dimensões:** identificadores, datas de análise, categorias e atributos usados para identificar, filtrar ou segmentar o resultado. Um identificador numérico não é uma métrica.
- **Métricas:** quantidades, valores, contagens, taxas, médias e estimativas usados para medir o fenômeno. Uma métrica pode ser não aditiva; não a classifique como dimensão só porque não pode ser somada.
- **Campos técnicos/auditoria:** origem de processamento, instante de captura, indicadores de qualidade e rastreamento cujo propósito principal não seja segmentar o negócio nem medir o fenômeno. Use esta categoria somente quando necessária, sem forçar todo campo a ser dimensão ou métrica.
- Classifique pela função no resultado, não apenas pelo nome ou tipo. Um status de negócio pode ser dimensão; um indicador de falha de captura pode ser auditoria. Quando houver mais de um uso, declare o papel principal adotado sem contar duas vezes. Se faltar contexto, marque a classificação como provisória.
- Liste os nomes finais de cada categoria em comentários, com quebras por grupo quando necessário. Preserve os aliases e a ordem relativa de projeção dentro de cada grupo. Não acrescente um dicionário extenso de campos diretos.
- Resolva `*`, `alias.*`, `EXCEPT` e `REPLACE` antes de declarar um total. Se o schema não puder ser recuperado, informe `Total de colunas: não determinado; depende de ...` e apresente apenas o inventário conhecido. Não invente a contagem.
- Conte STRUCT e ARRAY como uma coluna de primeiro nível cada; descreva campos internos e a unidade dos elementos separadamente quando isso afetar o uso. Em UNION, conte o schema resultante, não a soma das projeções dos ramos. Para projeção dinâmica, condicione o inventário aos parâmetros ou schema conhecidos.

#### Comportamento que o consumidor precisa conhecer

Cubra os pontos abaixo quando aplicáveis; omita itens sem efeito no resultado:

1. **Propósito e consumidor:** o que a saída permite analisar e quem ou qual processo a utiliza. Não invente um consumidor ausente do contexto.
2. **Granularidade e chave:** o que uma linha representa e quais campos a identificam. Diferencie chave esperada de unicidade garantida pela construção SQL ou verificada nos dados. Explique como duplicidades de origem ou joins podem afetar o resultado.
3. **População e cobertura:** quem entra, quem fica fora, se entidades sem atividade aparecem e se existe grade completa ou apenas registros observados. Inclua filtros herdados, não apenas o WHERE final.
4. **Tempo:** período de saída, campo de referência, limites, timezone conhecido e janelas de cálculo. Diferencie data exibida de período usado para estimar uma métrica; registre parâmetros e dependência de CURRENT_DATE ou CURRENT_TIMESTAMP. Não prometa reprodutibilidade se as fontes puderem mudar.
5. **Métricas e unidades:** fórmula ou origem, unidade monetária ou física conhecida, taxa em escala de 0 a 1 ou de 0 a 100 quando demonstrável, e arredondamento relevante. Não deduza moeda apenas pelo nome de uma coluna.
6. **Agregação segura:** quais métricas podem ser somadas e em quais dimensões. Destaque saldos que não devem ser somados entre datas, métricas de produto repetidas por SKU, contagens distintas não aditivas e taxas que exigem recomputar numerador/denominador. Explique rateios e reconciliações sustentados pela implementação. Se a aditividade não estiver demonstrada, registre o limite.
7. **NULL, zero e ausência de linha:** diferencie desconhecido, não aplicável, denominador zero, falta de correspondência e resultado zero. Informe quando a saída inteira pode ficar vazia; em agregações sem GROUP BY, verifique se ainda há uma linha mesmo sem entrada.
8. **Ordenação e volume:** informe ORDER BY final, direção, desempates e LIMIT, TOP ou paginação. Sem ORDER BY final, declare que a ordem não é garantida quando isso importar ao consumo. Não prometa número exato de linhas sem prova; se usar uma fórmula de grade, registre suas condições. LIMIT limita linhas retornadas, não comprova redução de bytes lidos.
9. **Tipos e compatibilidade:** destaque apenas aspectos que mudam o consumo, como IDs em texto, datas versus timestamps, precisão numérica, ARRAY/STRUCT e aliases duplicados. Não invente tipos sem schema ou inferência demonstrável.
10. **Limites e evidência:** identifique estimativas, alternativas de cálculo, fontes incompletas e premissas não verificadas. Diferencie inspeção do SQL, análise sintática e teste com dados. Não converta sucesso de parsing em validação das métricas.

Em código não tabular, adapte o bloco final para tipo e estrutura do retorno, estados, condições de erro, efeitos externos e consumidor. Não imponha contagem de dimensões e métricas a um retorno booleano ou objeto sem semântica analítica.

**Critério:** o consumidor entende quantas colunas recebe, como elas se dividem, o que cada linha representa, como agregar as métricas e quais limites impedem uma interpretação correta.

