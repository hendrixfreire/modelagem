# Fluxo de modelagem e gates de aprovação

## Regra central

Trate o processo como fases com transições controladas. Um gate é uma aprovação explícita do usuário sobre uma entrega identificada e a próxima ação. O agente verifica critérios e solicita; somente o usuário aprova. Não execute trabalho da fase seguinte antes da resposta.

Este arquivo é a fonte única das transições. As outras referências detalham o trabalho, mas não autorizam pular gates. A criação ou revisão desta skill não aprova gates de modelos futuros.

## Retomada e pasta padrão

Ao invocar a skill, procure `MODEL_SPECS.md` na pasta da tarefa atual antes de perguntar. Encontrado: leia seção 1, `CHECKLIST.md` e os artefatos citados; retome do estado registrado; se a aprovação registrada não tiver prova clara, peça confirmação antes de agir. Não encontrado: inicie F01.

Pasta padrão: `tasks/<ID>/modelagem/` quando a tarefa Runrun.it estiver identificada; caso contrário, pergunte o destino. Não misture modelos independentes no mesmo glossário sem acordo.

## Estado persistido no MODEL_SPECS.md

Seção 1 com subseções fixas `### 1.1. Identificação`, `### 1.2. Controle do processo` e `### 1.3. Histórico de gates`. Em 1.2, mantenha o YAML:

```yaml
fase_atual: F01
situacao: em_execucao
query_em_foco: null
versao_semantica_aprovada: null
gate_pendente: null
bloqueios: []
proxima_acao: concluir_entrevista
estado_validacao: nao_iniciada
cambio_congelado: null
```

- `fase_atual`: F01 a F05; ao encerrar, mantenha F05.
- `situacao`: `em_execucao`, `aguardando_aprovacao`, `bloqueado`, `concluido`, `encerrado_com_pendencias`.
- `estado_validacao`: `nao_iniciada`, `pendente`, `reprovado`, `validado`.
- `cambio_congelado`: média PTAX calculada no primeiro cálculo de custo desta versão semântica; recalcule só em nova versão.

Incremente revisão documental para evidências/estado; versão semântica para mudança de objetivo, regra, schema, granularidade ou arquitetura. Atualizar custo ou caminho sem mudar contrato não exige novo G02.

Em 1.3, registre por solicitação: ID do gate (`G03-q01-01` para tentativas), fase de origem e destino, objeto e revisão, versão semântica, escopo autorizado, evidências, decisão (`pendente`, `aprovado`, `reprovado`, `invalidado`, `dispensado`), autor, data e trecho da confirmação. Gere datas com ferramenta; não invente IDs de mensagens.

Crie `CHECKLIST.md` a partir de `templates/CHECKLIST.md` e referencie em 1.2. Itens, evidências e pendências somente na nota; estado e gates somente no MODEL_SPECS.md. Leia os dois antes de cada grupo de ações. Item concluído não aprova gate.

## Protocolo em todo gate

1. Confira critérios de saída e checklist da fase. Requisito bloqueante faltando: permaneça `bloqueado`, explique o que falta.
2. Atualize documentos e informe versão e objeto em avaliação.
3. Apresente o resumo e peça aprovação explícita. Não antecipe a fase seguinte.
4. Aguarde. “Sim”/“aprovo” só valem com uma única solicitação de gate inequívoca em aberto. Resposta factual não é aprovação.
5. Ajustes: aplique só o que a fase permite; mudança semântica segue regra de retorno.
6. Aprovado: registre antes de avançar. “Pode fazer tudo” não antecipa gates futuros.

Formato:

```text
Fase: <ID e nome> — aguardando aprovação
Entregue: <artefatos/resultado e versão>
Verificado: <critérios e evidências reais>
Pendências: <nenhuma ou lista com impacto>
Próxima ação: <fase, query, leituras e limites aplicáveis>
Aprova <entrega> e autoriza <próxima ação>?
```

## F01 — Entrevista

**Entrada:** invocação para modelo novo, ou retorno aprovado à entrevista.

**Faça:** siga `entrevista.md`, começando pelo ramo isolado. Colete objetivo, perguntas de negócio, outputs, fontes/localização, histórico, regras conhecidas, restrições, escolha de otimização, limites de leitura e diretório. Leia contexto local para formular perguntas; não execute investigação BigQuery nem gere SQL. Classifique lacunas técnicas para a investigação de F02. Crie rascunhos a partir dos templates.

**Saída verificável:** entendimento registrado, fontes localizáveis, lacunas listadas, escopo de investigação proposto com limites.

**G01:** peça aprovação do entendimento e autorização da investigação de F02, incluindo projeto, região e limite de bytes. Não aprova especificações.

## F02 — Investigação e especificação

**Entrada:** G01 aprovado com limites definidos.

**Investigue:** fontes, schemas, tamanhos, cardinalidades, cadeia do modelo existente, metadados e diagnósticos em memória. Use `scripts/tamanhos.py` para inventário e `scripts/ptax_media.py` para câmbio quando for calcular custos. Revalide tarifas da região do cliente. Não crie `.sql`. Registre evidências e divergências de negócio, resolvendo-as com o usuário.

**Especifique:** feche regras, glossário, granularidades, schemas, critérios de aceite e arquitetura mínima. Preencha todas as seções a partir de `templates/MODEL_SPECS.md`. Mapa de queries com IDs e caminhos `planejada`. Bytes de SQL futuro ficam pendentes de dry run. Para mais de uma query, justifique cada necessidade.

**Saída verificável:** inventário e cadeia documentados com lacunas explícitas; versão semântica identificada; sem decisão de negócio bloqueante; primeira canônica identificada; câmbio calculado e congelado em 1.2 quando houver custo calculável.

**G02:** peça aprovação da versão do MODEL_SPECS.md e autorização apenas da primeira canônica. Nenhum `.sql` de entrega sem esse gate vigente.

## F03 — Implementação, dry run e validação de uma canônica

**Entrada:** G02 ou G03 autorizando esta query. Versão semântica vigente.

**Faça, nesta ordem, para a canônica em foco:**
1. Crie a query e o `CONTEXT.md` a partir dos templates; atualize o mapa para `implementada`.
2. Revise localmente regras, legibilidade, aliases, schema e granularidade.
3. Execute dry run com `scripts/bq_leitura.py` (recusa `statementType` diferente de `SELECT`); registre bytes reais retornados.
4. Crie SQL de teste em `qNN/testes/` (unicidade, nulos, cardinalidade, reconciliação) e execute com o mesmo script dentro do limite. SQL de teste não é entrega nem precisa de gate próprio.
5. Calcule custo com `scripts/custo.py` usando a tarifa da região e o câmbio congelado.
6. Atualize evidências, custos e checklist. Se um teste falhar, corrija dentro de F03 e reexecute dry run e testes antes de apresentar.

**Saída verificável:** SQL, contexto, dry run, testes e custos com evidência; aderência ao contrato demonstrada.

**G03:** apresente código e evidências juntas. Peça aprovação dos resultados e autorização de exatamente um próximo passo: próxima canônica (ID e justificativa), F04 (otimização), F05 (com dispensa explícita de F04) ou retorno para correção.

## F04 — Otimização opcional

**Entrada:** canônicas validadas e escolha do usuário por variantes. Não invente otimização para preencher a fase.

**Gate único por variante (`G04-v<tentativa>`):** apresente canônica de referência, técnica, ID próprio, plano de comparação e limites. Aprovação autoriza criar, executar dry runs, testar equivalência e comparar custos desta variante.

**Faça após o gate:** crie candidata e contexto; dry runs comparáveis com `bq_leitura.py`; testes de equivalência incluindo multiplicidade; economia com `custo.py --comparar`. Reter somente com equivalência validada e redução mínima de 30% sem arredondamento prévio. Inferior a 30%, equivalência falha ou comparação inconclusiva: descarte dentro do escopo local autorizado e limpe todas as referências, preservando registro genérico da tentativa.

**Saída verificável:** cada experimento decidido; retidas equivalentes com economia demonstrada; descartes sem referências residuais; custos e mapa sincronizados.

## F05 — Consolidação e entrega

**Entrada:** última canônica aprovada em G03 e F04 concluído ou dispensado explicitamente.

**Faça:** consolide documentos, caminhos, custos por query e do modelo, evidências, recomendações e pendências. Execute `scripts/auditoria.py` e corrija o que for erro local. Não crie queries nem altere semântica nesta fase. Apresente os artefatos para aceite.

**G05:** peça aceite. Após aceite: `concluido` se todos os critérios validados; `encerrado_com_pendencias` se o usuário aceitou entrega parcial. Não altere `estado_validacao` por causa do aceite.

## Retornos, rejeição e interrupção

- Rejeição mantém a fase de origem; corrija e solicite novamente.
- Correção técnica de SQL: permaneça em F03, corrija, reexecute dry run e testes, reapresente G03. Não precisa novo G02 se o contrato não mudou.
- Mudança de objetivo/regra/schema/granularidade/arquitetura: apresente impacto, peça retorno a F01/F02, invalide aprovação semântica e gates dependentes, obtenha novo G02 antes de editar SQL. Não repita fases independentes.
- Nova evidência factual sem mudança de contrato: atualize revisão e evidências; não fabrique nova aprovação.
- Avanço indevido detectado: pare, registre a ocorrência e peça decisão; não autorize retroativamente.
- Antes de pausar, registre fase, gate e bloqueio. Ao retomar, leia estado e gates; divergência exige confirmação, não dedução pela existência de arquivo.
- Documentos antigos sem controle de processo: migre metadados, identifique aprovações comprovadas e solicite as faltantes; não aprove automaticamente.
