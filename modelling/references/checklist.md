# Checklist operacional da modelagem

## Uso

Copie o template abaixo para `CHECKLIST.md`, na mesma pasta do MODEL_SPECS.md, assim que definir o diretório. Não incorpore a lista ao MODEL_SPECS.md. `fluxo.md` define as transições; este checklist acompanha a execução, sem conceder autorização nem substituir critérios de aceite. Leia CHECKLIST.md antes de cada grupo de ações, ao retomar e antes de solicitar um gate; atualize após executar. Fase e autorizações ficam na seção 1 do MODEL_SPECS.md, sem duplicação.

- `[ ]` item não concluído, bloqueado ou aprovação não recebida; `[x]` somente com evidência: seção, arquivo relativo, resultado de teste ou gate aprovado.
- Após cada item executado, registre `— Evidência: <referência>`; pendência: `— Pendente: <motivo e próximo passo>`; não aplicável: `— Não se aplica: <justificativa>`.
- Marque aprovação somente após a resposta explícita. Ações anteriores não provam aprovação.
- Replique F03 por canônica autorizada e o bloco de tentativa F04 por variante autorizada, sem preencher IDs por suposição.
- Antes de solicitar um gate, confira todos os itens da fase e os critérios de `fluxo.md`. Pendência bloqueante impede avanço normal.
- Ao alterar um artefato, reabra os itens afetados e invalide os gates dependentes. Evidência anterior não vale para a nova versão.
- Após descartar variante, retire IDs, caminhos e valores específicos; mantenha a tentativa genérica, os gates e a evidência da limpeza.

## Template de CHECKLIST.md

```markdown
# Checklist da modelagem

[Especificações e controle do processo](MODEL_SPECS.md)

## F01 — Entrevista
- [ ] F01.01 — Confirmar ramo: modelo novo ou existente, na primeira pergunta isolada.
- [ ] F01.02 — Registrar objetivo, perguntas de negócio, consumidores, outputs desejados ou abertos e exclusões.
- [ ] F01.03 — Registrar fontes ou localização do modelo, histórico relatado e comportamento a preservar.
- [ ] F01.04 — Discutir granularidades, schemas imaginados, regras, casos de borda e vocabulário inicial.
- [ ] F01.05 — Registrar preferência por otimização, frequência de uso e parâmetros de custo conhecidos.
- [ ] F01.06 — Definir diretório; criar MODEL_SPECS.md, GLOSSARIO.md e CHECKLIST.md a partir dos templates, com links entre as notas.
- [ ] F01.07 — Listar lacunas técnicas e propor investigação com projeto, região e limites.
- [ ] F01.G01 — Receber e registrar aprovação do entendimento e autorização da investigação.

## F02 — Investigação e especificação
- [ ] F02.01 — Conferir G01, escopo, acesso e limites antes das leituras.
- [ ] F02.02 — Inspecionar fontes, schemas, chaves, granularidades e cardinalidades sem criar/editar SQL.
- [ ] F02.03 — Percorrer a cadeia acessível, deduplicar fontes, identificar ciclos, atualização e consumidores; registrar lacunas.
- [ ] F02.04 — Levantar tamanhos reais por tabela com scripts/tamanhos.py; registrar data da medição.
- [ ] F02.05 — Contrastar comportamento observado com objetivo; resolver divergências de negócio com o usuário.
- [ ] F02.06 — Verificar modalidade e tarifas oficiais da região; calcular e congelar câmbio com scripts/ptax_media.py quando houver custo calculável.
- [ ] F02.07 — Registrar evidências, custos preliminares, limitações e pendências sem inventar bytes.
- [ ] F02.08 — Especificar regras RNxx, outputs, schemas, arquitetura mínima e testes previstos no MODEL_SPECS.md preenchido do template.
- [ ] F02.09 — Registrar mapa de queries planejadas; justificar cada query além da primeira.
- [ ] F02.G02 — Receber e registrar aprovação da versão semântica e autorização da primeira canônica.

## F03 — Implementação e validação da canônica <ID autorizado>
- [ ] F03.01 — Conferir versão semântica aprovada e autorização específica da query em foco.
- [ ] F03.02 — Criar a query e o CONTEXT.md a partir dos templates, em pasta própria, com ID correspondente ao mapa.
- [ ] F03.03 — Aplicar estrutura mínima, comentários, aliases explícitos e regras SQL locais; preservar comportamento fora do escopo.
- [ ] F03.04 — Revisar localmente CTEs, joins, granularidade, schema e regras; atualizar mapa para implementada.
- [ ] F03.05 — Executar dry run com scripts/bq_leitura.py; registrar bytes e recusa de statementType não SELECT.
- [ ] F03.06 — Criar e executar testes em qNN/testes/ com o mesmo script dentro do limite; registrar resultados.
- [ ] F03.07 — Calcular custo com scripts/custo.py usando tarifa da região e câmbio congelado.
- [ ] F03.08 — Atualizar evidências, custos e checklist; em caso de falha, corrigir em F03 e revalidar antes de apresentar.
- [ ] F03.G03 — Receber e registrar aprovação dos resultados e autorização do próximo passo.

## F04 — Otimização opcional
- [ ] F04.01 — Confirmar canônicas validadas e escolha do usuário; registrar dispensa explícita se não houver otimização.

### Tentativa <sequência>
- [ ] F04.T01 — Identificar oportunidade, canônica de referência, técnica e ID próprio planejado.
- [ ] F04.G04 — Receber e registrar autorização única para criar, testar e comparar esta variante.
- [ ] F04.T02 — Criar candidata e contexto; preservar canônica e semântica aprovada.
- [ ] F04.T03 — Dry runs comparáveis e testes de equivalência, incluindo multiplicidade, schema, nulos e métricas.
- [ ] F04.T04 — Calcular economia com custo.py --comparar; verificar mínimo de 30% sem arredondamento prévio.
- [ ] F04.T05 — Reter somente variante elegível; descartar as demais no escopo local autorizado e limpar referências.
- [ ] F04.T06 — Sincronizar mapa, contextos, custos, evidências e checklist; preservar registro genérico da tentativa descartada.

### Fechamento
- [ ] F04.02 — Confirmar decisão final da otimização antes de F05.

## F05 — Consolidação e entrega
- [ ] F05.01 — Conferir autorização de entrada, canônicas/variantes retidas e eventual escopo parcial aceito.
- [ ] F05.02 — Consolidar custos por query e do modelo sem somar canônica e variante substituta na operação normal.
- [ ] F05.03 — Executar scripts/auditoria.py; corrigir erros locais e registrar pendências legítimas.
- [ ] F05.04 — Conferir rastreabilidade de perguntas, outputs, regras, queries, testes e evidências.
- [ ] F05.05 — Checar a entrega contra a requisição em silêncio e apresentar os arquivos com o estado técnico correto.
- [ ] F05.G05 — Receber e registrar aceite final do usuário.
- [ ] F05.06 — Encerrar como concluido ou encerrado_com_pendencias, preservando a situação real da validação.
```
