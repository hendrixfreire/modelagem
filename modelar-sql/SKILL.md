---
name: modelar-sql
description: "Conduz a modelagem de dados em SQL (BigQuery/GoogleSQL por padrão) por entrevista, especificação e aprovação por gates F01–F05, com estudo de custo, dry run e validação, sem publicar nem materializar. Use quando o usuário pedir para modelar, criar ou editar um modelo/query canônica a partir de perguntas de negócio e análise. Não use para apenas explicar, comentar ou fichar uma query existente."
disable-model-invocation: true
version: 2.1.0
author: Hendrix Freire, Hermes Agent
platforms: [macos, linux, windows]
---

# Modelagem SQL orientada por especificações

Crie ou edite modelos SQL a partir de perguntas de análise e negócio, conduzindo o trabalho do início ao fim com aprovação explícita entre fases. BigQuery e GoogleSQL são o padrão; para outro banco, identifique o dialeto em F01, adapte os comandos e mantenha o fluxo. Não publique nem materialize.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Antes de agir, identifique o ambiente atual e use as ferramentas equivalentes disponíveis nele para ler, buscar e editar arquivos, executar scripts e fazer perguntas ao usuário. Os scripts em `scripts/` são Python puro e rodam em qualquer ambiente com shell.

## Referências

| Quando | Ler |
| --- | --- |
| Sempre, antes de agir ou retomar | [Fluxo e aprovações](references/fluxo.md) — fonte única de fases e gates |
| Em toda fase, para executar | [Checklist operacional](references/checklist.md) — copie para `CHECKLIST.md` |
| Ao entrevistar | [Entrevista](references/entrevista.md) |
| Ao criar/editar documentos e SQL | [Padrões dos artefatos](references/documentos.md) |
| Ao escrever ou revisar qualquer `.sql` | [Boas práticas na escrita](references/boas-praticas-escrita-sql.md) — estilo, estrutura, agregação e leitura |
| Em todo estudo de custo | [Custos do BigQuery](references/custos-bigquery.md) |
| Para comandos prontos de BigQuery e PTAX | [Comandos](references/comandos.md) |
| Antes de propor variante otimizada | [Otimização SQL](references/otimizacao-sql.md); para um catálogo mais amplo de técnicas BigQuery, leia também [otimizar-sql](../otimizar-sql/SKILL.md) (as invariantes desta skill prevalecem) |
| Antes de investigar, gerar SQL ou concluir | [Validação e segurança](references/validacao.md) |

Formatos ficam em `templates/`: copie o template, nunca redija o esqueleto. Os scripts em `scripts/` executam dry run, inventário, câmbio, custo e auditoria; use-os em vez de improvisar comandos. `references/comandos.md` traz os comandos manuais equivalentes.

Todo modelo segue as orientações de melhores práticas de escrita de queries registradas em `references/boas-praticas-escrita-sql.md`: estilo, estrutura, agregação, colunas e leitura. A referência vale para canônica, teste e variante; em conflito com uma invariante desta skill, vale a invariante.

## Invariantes

1. Português brasileiro no imperativo. Um termo por conceito. Preserve identificadores externos com alias em português.
2. Não assuma regras de negócio. Separe decisão do usuário, fato observado, hipótese e pendência. Dados existentes não provam intenção de negócio.
3. Nenhum `.sql` de entrega antes do G02 vigente que aprova a especificação e autoriza a canônica em foco. Não salve SQL de entrega disfarçado em outra extensão. SQL de teste fica em `qNN/testes/` durante F03 e não é entrega.
4. BigQuery somente leitura: proiba DDL, DML, tabelas temporárias explícitas, materialização, exportação remota, agendamento, procedimentos, funções remotas e mudanças de recursos/IAM. Não use tabela de destino. O script de leitura recusa `statementType` diferente de `SELECT`.
5. Não execute comandos de edição no gcloud nem escrita por outra ferramenta. Nenhum gate autoriza escrita no BigQuery.
6. Declare projeto de cobrança, região e limite de bytes antes de todo acesso; sem limite definido, não execute consulta que processe dados. Não aumente limite sem decisão do usuário.
7. Comece com uma query canônica. Query adicional ou variante só com autorização específica no gate da fase.
8. Preserve comportamento fora do escopo aprovado. Investigue toda a cadeia acessível; documente falta de acesso sem alegar cobertura completa.
9. Preserve legibilidade e minimalismo da canônica: colunas explícitas com `AS`, colunas qualificadas, `GROUP BY` explícito, CTEs necessárias, comentários de propósito e regras. Sem `GROUP BY ALL`; sem `SELECT DISTINCT` para esconder duplicação de join.
10. Mantenha `MODEL_SPECS.md`, `GLOSSARIO.md`, `CHECKLIST.md`, contextos, queries e custos sincronizados. Mudança semântica exige retorno de fase e nova aprovação antes de editar SQL.
11. Não execute Git nem publicação nesta skill. Não leia credenciais nem grave dados pessoais desnecessários.
12. Não avance de fase automaticamente. Conclusão técnica permite solicitar aprovação, não concedê-la. Pare no gate e espere.
13. Câmbio: calcule no primeiro cálculo de custo do estudo (`scripts/ptax_media.py`) e congele o resultado em `cambio_congelado` na seção 1.2 do MODEL_SPECS.md; use-o na versão semântica inteira e recalcule só em nova versão. Nunca fixe cotação na skill.

## Controle do processo

Estado e histórico de gates na seção 1 do `MODEL_SPECS.md`; checklist operacional em `CHECKLIST.md`, nota separada. Leia os dois antes de cada grupo de ações. Regras em `references/fluxo.md`.

Retomada: procure `MODEL_SPECS.md` na pasta da tarefa antes de perguntar qualquer coisa. Sem arquivo, inicie F01 e pergunte isoladamente se o modelo começa do zero ou parte de modelo existente. Com arquivo, leia estado, gates e checklist e continue do ponto registrado; não reinicie nem infira aprovação pela existência de SQL.

A invocação da skill autoriza iniciar F01, não as fases seguintes.

## Fases e gates

| Fase | Trabalho | Gate de saída |
| --- | --- | --- |
| F01 | Entrevista | G01: aprovar entendimento e autorizar investigação |
| F02 | Investigação e especificação | G02: aprovar versão semântica e autorizar primeira canônica |
| F03 | Implementação, dry run e validação de uma canônica | G03: aprovar código com evidências e autorizar próximo passo |
| F04 | Otimização opcional, um gate por variante | G04: aprovar criar e testar a variante |
| F05 | Consolidação e entrega | G05: aceitar entrega |

F03 repete por canônica; F04, por variante. Critérios de entrada, ações permitidas e critérios de saída em `references/fluxo.md`. Não pule F04 silenciosamente: registre dispensa explícita.

## Armadilhas

- Responder pergunta da entrevista não aprova gate. Silêncio, arquivos existentes e testes aprovados não são autorização.
- Dry run não valida dados nem é fatura.
- Não reduza o número de queries sacrificando granularidade, regras ou outputs aprovados.
- Não copie otimizações de outro dialeto nem altere cardinalidade para economizar bytes.
- Tarifa fotografada é por região: revalide a tarifa da região do cliente antes de calcular custo.

## Verificação

Aplique `references/validacao.md` e execute `scripts/auditoria.py` na pasta do modelo antes de solicitar G05. Confira gates, versão semântica, autorizações por query e coerência do ponto de retomada. Informe bloqueios em vez de inventar resultados.
