# Exemplos

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

