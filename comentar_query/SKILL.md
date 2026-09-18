---
name: comentar_query
description: Use ao comentar etapas e regras em SQL ou código.
version: 0.2.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [comentarios, documentacao, sql, codigo, regras-de-negocio]
---

# Comentários de etapas e regras no código

Documente o propósito, as relações e as regras de cada etapa dentro do próprio código, para quem precisa ler, manter ou validar o trabalho. Apesar do nome `comentar_query`, aplique este padrão a qualquer domínio: consultas, scripts, funções, pipelines, automações, integrações e testes. Não limite o uso a modelos de dados ou a um cliente.

## Quando usar

- Ao criar ou alterar código que tenha etapas, transformações, filtros ou decisões que precisem de explicação.
- Ao receber pedidos como “comente as CTEs”, “explique as regras no código” ou “facilite a leitura”.
- Ao documentar código existente sem alterar seu comportamento.
- Não use como autorização para refatorar, corrigir regras, executar consultas ou publicar arquivos.

## Pré-requisitos

Leia o arquivo completo, as instruções do projeto e as decisões disponíveis. Use `read_file` e `search_files` para recuperar o contexto. Não exija banco de dados ou acesso de produção para uma tarefa de comentários.

## Procedimento

### 1. Confirme o escopo

Identifique o arquivo e a versão solicitada. Preserve o original quando o usuário pedir uma cópia. Se o pedido for apenas comentar, altere somente comentários e espaçamento seguro para a linguagem.

Declare o propósito e o consumidor no início do arquivo, respeitando posições obrigatórias de shebang, declaração de codificação ou diretivas. Declare também a granularidade da saída quando houver dados tabulares.

**Critério:** arquivo, consumidor e limite de alteração identificados; nenhuma regra nova assumida.

### 2. Mapeie as etapas

Leia entradas, transformações, condições e consumidores antes de escrever. Em SQL, cubra todas as CTEs na ordem declarada e o SELECT final. Sem CTEs, identifique os blocos lógicos. Em outras linguagens, use funções ou blocos com responsabilidade própria.

Numere as etapas sequencialmente dentro de cada fluxo: `1. nome_da_etapa`, `2. nome_da_etapa`. Não sugira que a ordem textual das CTEs garante a ordem física de execução. Em fluxos independentes, reinicie a numeração por fluxo e identifique seu escopo.

**Critério:** toda etapa está identificada, inclusive ramificações e junções.

### 3. Comente cada etapa no ponto de uso

Insira um comentário imediatamente antes da CTE, função ou bloco. Cubra, em geral em 3 a 6 linhas:

- **Função:** o que produz e por que a etapa existe.
- **Unidade:** o que cada linha de dados representa; por exemplo, pedido, item ou cliente + mês. Isso não significa explicar cada linha de sintaxe.
- **Relações:** de onde recebe dados, quais chaves usa e para qual etapa fornece a saída.
- **Regras:** quais registros ou casos inclui, exclui, transforma ou mantém sem informação.

Em código não tabular, substitua a granularidade pela unidade processada: evento, requisição, arquivo, objeto ou tarefa. Explique o estado recebido e o estado produzido quando aplicável. Não invente uma granularidade tabular para uma função sem linhas de dados.

Use frases diretas como “Seleciona”, “Calcula”, “Mantém” e “Alimenta”. Não imponha rótulos repetidos quando frases curtas já cobrirem os pontos. Divida CTEs visualmente com uma linha em branco; não crie banners decorativos.

**Critério:** o leitor entende a responsabilidade e o contrato da etapa antes de ler suas expressões.

### 4. Explique regras junto aos filtros e condições

Além do comentário de abertura, comente expressões internas quando a regra não for evidente ou exigir ressalva. Posicione a explicação imediatamente antes da condição ou do conjunto de condições correspondente.

Em SQL, verifique:

- `WHERE`, `HAVING` e `QUALIFY`: população mantida ou excluída, inclusive efeitos de NULL.
- `JOIN` e `ON`: chaves, preservação de linhas sem correspondência e risco de multiplicação. Diferencie unicidade esperada de unicidade comprovada.
- Datas: data de referência, janela, limites inclusivos ou exclusivos e timezone, se definido.
- `CASE`, `IF` e `COALESCE`: prioridade das alternativas, significado do ELSE e diferença entre zero, NULL e ausência de linha.
- Agregações: mudança de granularidade, numerador, denominador, unidade e média ponderada ou não, conforme a expressão.
- Janelas: grupo de `PARTITION BY`, ordenação, frame quando relevante, desempate e uso do resultado.
- Deduplicação: chave, registro mantido e limites em caso de empate. Não descreva uma escolha arbitrária como “primeiro” ou “mais recente”.
- `UNION` e `UNION ALL`: como as populações se combinam e se duplicidades são removidas ou preservadas.

Em outras linguagens, aplique o mesmo raciocínio a validações, desvios condicionais, loops, tentativas, exceções, retorno antecipado e efeitos externos. Explique limites, ordem das decisões e comportamento quando a entrada está ausente ou inválida.

Não traduza sintaxe sem explicar o efeito. Prefira “Exclui pedidos cancelados da receita” a “Filtra status”. Não invente o motivo de negócio: quando ele não estiver documentado, descreva apenas o comportamento observado. Marque uma premissa como “esperada” ou “não verificada” e uma dúvida de negócio como pendente. Não altere a implementação para resolver a dúvida.

**Critério:** cada filtro ou condição relevante tem explicação no bloco ou junto à expressão, sem duplicação desnecessária.

### 5. Documente o contrato da saída final

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

### 6. Verifique antes de entregar

Compare o antes e o depois com ferramentas. Use `patch` para alterações em arquivos existentes e `write_file` para arquivos novos. Em tarefas de comentários, confirme que o conteúdo executável não mudou com tokens ou árvore sintática que desconsidere apenas comentários comuns e espaços irrelevantes.

Não remova comentários com regex genérica para provar equivalência: marcadores podem aparecer dentro de strings. Não trate hints SQL, diretivas, pragmas, comentários de tipagem ou docstrings como texto sem efeito. Respeite indentação significativa e posições especiais da linguagem.

Execute análise sintática ou testes locais pertinentes quando disponíveis. Não execute consultas faturáveis nem ações externas apenas para validar comentários. Se faltar analisador, revise o diff e informe esse limite; não declare equivalência comprovada por execução.

**Critério:** cobertura dos comentários e preservação da lógica verificadas; limites da verificação registrados.

## Exemplos de aplicação

### SQL: CTEs numeradas e regra próxima ao filtro

Exemplo didático; não reutilize a regra de receita sem confirmar o contrato do trabalho.

```sql
-- Propósito: fornecer receita por cliente para o relatório comercial.
-- Granularidade da saída: uma linha por cliente com pedido elegível.
WITH
-- 1. pedidos_elegiveis
-- Seleciona pedidos faturados da tabela pedidos para o cálculo da receita.
-- Uma linha por pedido, conforme a chave esperada da fonte; não deduplica registros.
-- Alimenta receita_cliente com o cliente e o valor do pedido.
pedidos_elegiveis AS (
    SELECT
        id_cliente,
        valor_pedido
    FROM pedidos
    -- Inclui somente pedidos faturados; outros status e status NULL ficam fora.
    WHERE status = 'faturado'
),

-- 2. receita_cliente
-- Soma os valores de pedidos_elegiveis por cliente.
-- Uma linha por cliente; clientes sem pedido elegível não são criados nesta etapa.
-- SUM ignora valores NULL e retorna NULL se todos os valores do grupo forem NULL.
receita_cliente AS (
    SELECT
        id_cliente,
        SUM(valor_pedido) AS receita
    FROM pedidos_elegiveis
    GROUP BY id_cliente
)
-- 3. saída_final
-- Entrega receita por cliente para o relatório comercial.
-- Colunas: 2 no total = 1 dimensão + 1 métrica.
-- Dimensão: id_cliente. Métrica: receita.
-- Granularidade: uma linha por id_cliente, garantida pelo GROUP BY anterior.
-- População: clientes com pedidos faturados; clientes sem pedido elegível não aparecem.
-- Tempo: sem filtro de data; considera todo o histórico disponível na fonte.
-- Receita: soma de valor_pedido; moeda não informada neste exemplo.
-- Agregação: pode somar entre clientes se cada pedido ocorrer uma vez na fonte
-- e os valores estiverem na mesma moeda; a query não verifica essas premissas.
-- NULL: receita é NULL se todos os valores do cliente forem NULL, não zero.
-- Identificadores de cliente NULL, se existirem, formam um único grupo.
-- Sem pedidos elegíveis, a saída fica vazia. Não há limite fixo de linhas.
-- Ordenação: id_cliente crescente. Regras inferidas do SQL, sem teste nos dados.
SELECT id_cliente, receita
FROM receita_cliente
ORDER BY id_cliente;
```

### Python: etapas não tabulares

```python
# Propósito: validar o lote recebido antes do envio pelo processo de integração.
def validar_lote(registros, limite):
    # 1. validar_limite
    # Recebe a quantidade máxima permitida por lote e verifica a configuração.
    # Interrompe a validação com erro se o limite não for positivo.
    if limite <= 0:
        raise ValueError("O limite deve ser positivo.")

    # 2. validar_quantidade
    # Processa um lote e verifica sua quantidade antes de liberar o envio.
    # A fronteira é inclusiva: quantidade igual ao limite é aceita.
    if len(registros) > limite:
        raise ValueError("O lote excede o limite.")

    # Saída: True libera o lote, inclusive vazio; esta função não envia registros.
    return True
```

## Cuidados

- Não comente cada atribuição ou coluna direta quando o bloco já explica sua função.
- Não esconda regras em um cabeçalho distante; mantenha detalhes junto à condição.
- Não afirme unicidade, desempenho, intenção ou aprovação sem evidência.
- Não copie contagens, datas históricas ou regras de um cliente para outro trabalho.
- Atualize os comentários e a numeração quando alterar o código; remova explicações que deixaram de corresponder à implementação.
- Use português, preserve identificadores externos e adote uma palavra por conceito. Evite metáforas, adjetivos de avaliação e sinônimos decorativos.
- Em formatos sem comentários, como JSON estrito, use documentação auxiliar; não introduza sintaxe inválida nem campos não previstos.

## Checklist final

- [ ] Todas as CTEs ou etapas do fluxo estão numeradas na ordem declarada.
- [ ] Função, unidade processada, entradas, relações e saída estão explicadas.
- [ ] Filtros, condições e regras de negócio estão documentados no ponto de uso.
- [ ] NULL, zero, ausência, erros, datas e empates estão explicados onde se aplicam.
- [ ] O bloco de saída final está numerado e informa propósito, granularidade, chave e cobertura.
- [ ] As colunas foram contadas com ferramentas e classificadas sem sobreposição; a soma das categorias reconcilia com o total.
- [ ] Os nomes finais estão listados por categoria; projeções não resolvidas e classificações provisórias estão sinalizadas.
- [ ] Tempo, unidades, agregação segura, NULL, zero e saída vazia estão explicados onde se aplicam.
- [ ] Ordenação, limites de linhas, tipos relevantes e nível de evidência não excedem o que foi verificado.
- [ ] Os comentários descrevem o código real, sem aprovar regras não verificadas.
- [ ] A lógica e os arquivos protegidos foram preservados e verificados.
- [ ] A resposta final informa o arquivo alterado e a verificação realizada, sem repetir todos os comentários.
