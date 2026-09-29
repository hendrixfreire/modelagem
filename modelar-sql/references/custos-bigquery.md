# Referência de custos do BigQuery

## Regra de cálculo

Calcule o custo diretamente dos bytes e da tarifa oficial da região e modalidade. Sem margem percentual arbitrária, inclusive margens sugeridas por outra skill. Calcule com `decimal.Decimal` via `scripts/custo.py` ou código equivalente; nunca mentalmente. Precisão nas entradas, arredondamento só na apresentação. Cenários variam apenas parâmetros explícitos, como frequência ou bytes medidos.

Diferencie: tarifa oficial exata, custo aritmético calculado, consumo estimado por dry run, consumo faturado por job e valor efetivo da fatura. Cálculo exato sobre bytes estimados continua sendo estimativa.

## Fontes oficiais e revalidação

- Tarifas: https://cloud.google.com/bigquery/pricing
- SKUs e moeda: https://cloud.google.com/skus/
- Estimativa e limites: https://cloud.google.com/bigquery/docs/best-practices-costs
- Armazenamento: https://cloud.google.com/bigquery/docs/information-schema-table-storage
- Metadados de jobs: https://cloud.google.com/bigquery/docs/information-schema-jobs
- Câmbio: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/

Revalide tarifas a cada estudo. Registre URL, data/hora, região selecionada, modalidade, unidade, valor literal e SKU/compromisso. A página de preços tem seletor de região: a tarifa exibida vale só para a região exibida. Não use a tarifa de uma região para outra; verifique a região do cliente pelo seletor da página, navegador ou catálogo SKUs. Sem evidência atual da região correta, marque tarifa não verificada e não conclua o custo.

### Fotografia de referência — região US (`us`), USD, consultada em 14/09/2026

Valores exibidos na página oficial para a região multi-region US. Revalide antes de usar. Preserve a unidade horária do armazenamento; não substitua por preço mensal arredondado.

| Item | Valor oficial exibido | Unidade |
| --- | --- | --- |
| Processamento on-demand acima da franquia | US$ 6,25 | TiB |
| Capacidade Standard, sem compromisso | US$ 0,04 | slot-hora |
| Capacidade Enterprise, sem compromisso | US$ 0,06 | slot-hora |
| Capacidade Enterprise Plus, sem compromisso | US$ 0,10 | slot-hora |
| Armazenamento lógico ativo | US$ 0,000031507 | GiB-hora |
| Armazenamento lógico de longa duração | US$ 0,000021918 | GiB-hora |
| Armazenamento físico ativo | US$ 0,000054795 | GiB-hora |
| Armazenamento físico de longa duração | US$ 0,000027397 | GiB-hora |

Franquias mensais por conta: 1 TiB on-demand e 10 GiB de armazenamento, exibidas na página. Não deduza disponibilidade para o modelo nem aplique franquias cumulativas por categoria sem verificar a regra vigente. Longa duração depende de 90 dias sem modificação e pode variar por partição; use a tarifa explícita, não desconto presumido de 50%.

## Inventário de tabelas

Use `scripts/tamanhos.py` (equivalente manual em `comandos.md`). Registre por tabela: identificador, tipo, linhas, bytes lógicos/físicos, ativo/longa duração, partições, clustering, momento da medição e evidência. Campos externos com alias de negócio. Indisponível é indisponível, não zero. Views não têm armazenamento próprio; percorra fontes e deduplique tabelas-base antes de somar.

Considere a modalidade de armazenamento do dataset: não some lógico e físico como se ambos fossem cobrados. Em cobrança física, verifique time travel e fail-safe sem contar duplicado. Separe armazenamento existente do custo incremental hipotético do modelo; arquivo SELECT não cria armazenamento persistente. Não materialize para medir output futuro.

## Processamento on-demand

```text
custo_usd = Decimal(bytes_base) / Decimal(2**40) * tarifa_usd_por_tib
custo_brl = custo_usd * media_ptax_venda
custo_periodo_usd = soma(custo_por_execucao_usd * numero_execucoes)
```

`bytes_base` com origem identificada:
- `totalBytesProcessed` do dry run: base estimada.
- `totalBytesBilled` de job concluído: base faturada bruta, antes de franquias/créditos da conta.

Cobrança on-demand tem arredondamento para MB e mínimo de 10 MB por tabela referenciada e por query, conforme a página oficial. Verifique a convenção vigente antes de reproduzir. Não declare custo faturável exato multiplicando bytes processados quando mínimos forem relevantes; apresente o cálculo sobre bytes processados com a limitação declarada, ou use metadados de execução real dentro do limite autorizado. Não presuma base faturável pelo tamanho integral da tabela.

Calcule custo bruto e cenário condicionado à franquia remanescente comprovada separadamente. Sem dados de créditos, descontos, impostos e conta, não declare valor líquido de fatura. Cache pode não ser cobrado: desabilite nas comparações e registre `cacheHit` em execuções reais. `LIMIT` não controla bytes.

## Armazenamento

```text
custo_armazenamento_usd = soma(Decimal(bytes_classe) / Decimal(2**30) * horas_no_periodo * tarifa_usd_por_gib_hora_classe)
```

Fotografia multiplicada por horas futuras é projeção de tamanho constante, não consumo medido: declare a premissa. Não use 730 horas como mês universal; derive a duração do período definido ou use a unidade mensal oficial quando disponível.

## Capacidade

Bytes de dry run não determinam custo por capacidade. Identifique edição, região, compromissos, reserva, autoscaling e política de cobrança. Calcule só com capacidade faturável e duração demonstradas, aplicando mínimos e tarifas oficiais. `totalSlotMs` mede trabalho, não slots faturados. Conversão para on-demand é comparação hipotética rotulada, nunca custo efetivo da reserva. Sem dados de atribuição, declare custo por query indisponível nessa modalidade. Variante não é aceita pelo critério de 30% com base só em bytes nesse cenário.

## Câmbio congelado por versão semântica

Calcule no primeiro cálculo de custo do estudo, com `scripts/ptax_media.py` (detalhes em `comandos.md`): janela D-30 a D-1 em `America/Sao_Paulo`, PTAX de venda diária de fechamento, média aritmética com Decimal pela contagem efetiva de publicações. Feriados e fins de semana não são preenchidos; dias sem publicação não viram zero; não use 30 pregões.

Registre no `MODEL_SPECS.md`: janela, contagem, método, valores ou evidência local, URL e momento da consulta. Congele a média em `cambio_congelado` (seção 1.2) e use-a em todos os custos desta versão semântica. Recalcule só em nova versão semântica. Resposta vazia não é câmbio zero; BCB indisponível: mantenha USD e marque BRL pendente. A conversão USD × PTAX é referência analítica, não preço contratual; faturamento em outra moeda segue SKUs naquela moeda.

## Duas fases do estudo

**Antes de G02:** inventário, modalidade, tarifas da região, câmbio congelado quando houver custo calculável, e custos possíveis com evidência disponível. Bytes de SQL futuro e custos correspondentes: pendentes de dry run. Não gere SQL para preencher lacuna de aprovação.

**Durante F03, por query:** dry run com `bq_leitura.py`, registro de bytes, parâmetros, projeto, região, limite, cache, data e evidência. Custo com `custo.py`, USD e BRL, atualizando o documento. Recalcule após edição do SQL que afete leitura ou resultado.

**Modelo completo:** variantes substituem a canônica na operação normal (some ambas só no custo de validação). Separe testes, processamento recorrente e armazenamento existente. Frequência de consumo por BI entra no escopo, sem inventar volume de uso.

## Apresentação

Notação brasileira para humano; ISO/decimais de máquina nos registros. Bytes inteiros com conversão GiB/TiB explícita. Casas decimais suficientes para custo diferente de zero; não exiba US$ 0,00 como custo zero de consulta pequena. Inclua fórmula, entradas, origem e precisão; arredonde só na apresentação, nunca antes do teste de 30%.
