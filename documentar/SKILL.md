---
name: documentar
description: Use ao criar ou atualizar documentação de produtos.
version: 0.2.0
author: Hendrix Freire, Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentação, entrevista, AE, DE, DV, Bitbucket]
---

# Documentar

Identifique a entrega e encaminhe a entrevista e a documentação para as referências das áreas envolvidas. Produza ou atualize um documento de produto; não implemente o produto nem publique apenas por receber um pedido de documentação.

## 1. Identifique o pedido

Declare o objetivo em uma frase. Reaproveite informações fornecidas e leia as fontes autorizadas antes de perguntar. Confirme as lacunas em rodadas de até cinco perguntas:

- Qual cliente e produto serão documentados? Onde deve ficar o documento?
- É documentação inicial ou atualização? Onde está a versão existente?
- Qual necessidade motivou a entrega, o que foi feito e quem utiliza o resultado?
- Quais fontes existem: tarefa no Runrun.it, código, decisões, testes e arquivos complementares?
- Quais áreas participaram ou foram afetadas: DE, AE e DV?

Na atualização, obtenha também o que mudou, por quê, quando, quem realizou e quais impactos foram identificados. Não deduza regras de negócio somente pelo código.

**Avance quando:** produto, tipo de documentação e áreas estiverem identificados. Se não conseguir identificar uma área, pergunte antes de escolher uma referência.

## 2. Carregue as referências necessárias

Resolva os caminhos em relação a este `SKILL.md`. Use `read_file` ou ferramenta equivalente. Se um arquivo estiver ausente, solicite sua localização; não substitua o padrão por uma estrutura inventada.

### Padrão comum: leitura obrigatória

- [Guia de preenchimento](../instrucoes-documentacao-produto-v1.md): consulte antes da entrevista; contém obrigatoriedade, tratamento de lacunas, arquivos complementares, histórico e revisão.
- [Template do produto](../modelo-documentacao-produto-v1.md): consulte antes da escrita; contém a estrutura e a seção fixa para agentes.

### Roteamento por área

| Quando o trabalho envolver | Referência obrigatória | Seção do produto |
|---|---|---|
| Fontes, extração, conectores, ingestão ou cargas | [DE](references/de.md) | 2. DE |
| Modelos, transformações, regras de negócio, indicadores ou testes dos dados | [AE](references/ae.md) | 3. AE |
| Dashboards, relatórios, interface, filtros, acessos ou publicação da visualização | [DV](references/dv.md) | 4. DV |

Carregue todas as referências aplicáveis, não apenas a área de quem solicitou. Em tarefas com várias áreas, conduza a entrevista na ordem DE → AE → DV e compartilhe as respostas comuns sem repetir perguntas. Carregue outra referência quando identificar impacto em sua área; dependência compartilhada não autoriza alterar conteúdo fora do escopo.

Para mudança somente na visão geral ou no histórico, aplique o guia comum e carregue uma área apenas se o conteúdo técnico dela for afetado. Na documentação inicial, preserve os títulos das três áreas e justifique “Não se aplica” quando não houver participação. Na atualização, preserve as áreas não afetadas.

**Avance quando:** cada área aplicável tiver sua referência lida e o escopo de preenchimento identificado.

## 3. Execute a entrevista e a escrita

Siga a entrevista e a verificação de cada referência carregada. Pergunte somente o que faltar, por assunto. Distinga fatos confirmados, comportamento implementado, suposições e pendências. Não declare resultados de testes sem evidência de execução.

Leia a documentação existente inteira antes de editar. Para criar, use `write_file`; para atualizar, use `patch` ou ferramenta equivalente. Leia as regras locais do projeto antes de qualquer escrita. Não execute SQL, cargas ou operações de nuvem apenas para documentar; solicite autorização separada quando necessário.

Preserve integralmente a seção “0. Instruções para agentes”. Na criação, copie-a do template; na atualização, compare antes e depois. Se a seção existente divergir do padrão, aponte a divergência e solicite revisão coordenada, sem substituição silenciosa.

Aplique o guia comum à visão geral, aos arquivos complementares e ao histórico. Mantenha o estado vigente nas seções técnicas e o motivo da mudança no histórico. Revise arquivos complementares afetados e registre descrição textual, fonte editável, responsável e situação. Não invente histórico anterior para um produto já existente.

Se faltar um dado que impeça uma decisão, solicite confirmação. Se a lacuna não impedir a escrita, entregue um rascunho com “Pendente”, impacto e responsável identificado ou pendente de definição. Substitua campos genéricos do template por informações ou pendências explícitas.

**Avance quando:** o arquivo existir, o conteúdo solicitado estiver preenchido e as lacunas estiverem declaradas.

## 4. Revise e entregue

Antes de entregar, aplique a lista de revisão do guia e os critérios de cada área carregada. Confira coerência entre saídas de DE, entradas e saídas de AE e consumo por DV quando essas relações existirem. Preserve a ordem DE → AE → DV e valide links, seção fixa, evidências, histórico e arquivos complementares.

Inspecione o diff quando houver Git; não execute `git init` para contornar a ausência de repositório. Obtenha datas por ferramenta e diferencie a data do registro da data do evento. Informe limites de leitura ou de execução. Não confunda revisão documental com teste técnico ou aprovação humana.

Entregue o arquivo, um resumo do escopo documentado e as pendências. Não produza apenas uma proposta de conteúdo quando o pedido for criar o documento.

## 5. Encaminhe para Git, Bitbucket e Wiki

Leia o [tutorial de Git e Bitbucket](../tutorial-git-bitbucket-documentacao.md) e indique o próximo passo conforme o estado real: preparar acesso, clonar, criar branch, revisar diff, commit, push, PR ou conferir a sincronização após o merge.

Se a pessoa quiser continuar, confirme se prefere executar manualmente ou com auxílio do agente. O pedido “documentar” não autoriza commit, push, PR ou merge. Obtenha autorização explícita para executar essas ações. Nunca solicite token ou senha no chat, leia credenciais ou descarte trabalho existente.

Diferencie arquivo local, branch enviada, PR aberto e página publicada. Verifique o destino antes de afirmar envio ou publicação. Se não houver autorização, conclua com o arquivo local e a orientação, sem executar a etapa externa.

## Uso local

Solicite: “Leia `documentar/SKILL.md` nesta pasta e me ajude a documentar a tarefa que terminei.”

Mantenha `references/` junto deste arquivo e os três documentos comuns na pasta superior. Esta skill local não está automaticamente instalada no catálogo de um agente. Não duplique o guia ou o template nas referências por área; elas orientam a entrevista e apontam para os campos do padrão comum.
