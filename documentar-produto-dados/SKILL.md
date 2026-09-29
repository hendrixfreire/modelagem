---
name: documentar-produto-dados
description: "Cria ou atualiza a documentação de um produto de dados em clientes/<cliente>/<produto>/ (visão geral, DE, AE, DV e histórico) por entrevista por área, a partir dos modelos do repositório de documentação. Use quando o usuário pedir para documentar um produto de dados, atualizar páginas DE/AE/DV ou registrar mudança e histórico. Exige o repositório de documentação com os modelos e o tutorial de Git/Bitbucket; não use fora dele."
disable-model-invocation: true
argument-hint: "[cliente/produto] [caminho do repositório]"
version: 0.5.0
author: Hendrix Freire, Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentação, entrevista, AE, DE, DV, Bitbucket]
---

# Documentar produto de dados

Objetivo: criar ou atualizar as páginas vigentes de um produto de dados, com entrevista por área e revisão das dependências.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Antes de agir, identifique o ambiente atual e use as ferramentas equivalentes disponíveis nele para ler, buscar e editar arquivos, executar scripts e fazer perguntas ao usuário. Os scripts em `scripts/` são Python puro e rodam em qualquer ambiente com shell.

A solicitação de documentar autoriza a escrita local. Commit, push, PR, merge e publicação exigem autorização específica.

## 1. Localize o padrão e o produto

Identifique o repositório de documentação, o cliente, o produto, a tarefa, as fontes e as áreas afetadas. Localize nele `instrucoes-documentacao-produto-v1.md`, `modelo-documentacao-produto-v1.md` e `modelos-documentacao-produto-v1/`. Esta skill pode estar instalada fora do repositório: **não resolva esses caminhos em relação à pasta da skill**. Se o repositório ou os modelos não estiverem disponíveis, peça o caminho antes de criar páginas.

Leia o guia e o índice dos modelos. Confira regras locais, estado do Git e páginas existentes em `clientes/<cliente>/<produto>/`. Leia integralmente as páginas existentes do escopo antes de editar. Não migre um produto antigo nem substitua uma página única por arquivos separados sem mapear seu conteúdo e obter escopo para essa migração; preserve a página antiga até conferir o resultado.

Confirme em até cinco perguntas por rodada o que faltar: objetivo e consumidor, documentação inicial ou atualização, mudança e motivo, fontes e evidências, áreas afetadas. Registre data do evento e autoria quando houver mudança. Distingua `vigente` (comportamento atual), `histórico` (mudança e motivo), `pendência` (lacuna, impacto e responsável) e `evidência` (resultado observado, período e local).

**Avance quando:** produto, pasta, tipo de trabalho, áreas afetadas e fontes estiverem identificados.

## 2. Carregue as referências por área

Leia `references/de.md` para fontes e ingestão, `references/ae.md` para modelos e regras, `references/dv.md` para interface e acesso. Carregue todas as referências afetadas; use a ordem DE → AE → DV quando houver mais de uma. Para mudança somente na visão geral ou no histórico, carregue referência técnica apenas se houver impacto técnico.

A pasta `clientes/<cliente>/<produto>/` tem `visao-geral.md`, `de.md`, `ae.md`, `dv.md` e `historico.md`. Copie os cinco arquivos dos modelos para um produto novo. Preserve os nomes de arquivo e a seção 0 da visão geral, inclusive os links. Em produto existente, compare a seção 0 com o modelo antes e depois de editar; encaminhe divergência para revisão do padrão sem substituição silenciosa. Time não participante mantém a página com título, “Não se aplica” e motivo. Não crie pasta por time acima do produto.

**Avance quando:** referências das áreas afetadas lidas e páginas a editar identificadas.

## 3. Entreviste e escreva

Consulte código, tarefa, decisões e evidências antes de perguntar. Escreva apenas fatos sustentados; rotule comportamento implementado, regra confirmada, suposição e pendência. Uma regra lida no código não equivale a validação de negócio. Registre testes com critério, resultado, período e referência; não declare execução a partir da existência de código de teste.

Na criação, preencha a visão geral antes das páginas técnicas. Nas atualizações, edite a página do time responsável e as outras páginas cujo contrato mudou: saída de DE, entrada e saída de AE, consumo por DV. Atualize `historico.md` para alterações de significado ou comportamento. Mantenha a regra vigente na página técnica, não apenas no histórico. Atualize a síntese e as restrições da visão geral se forem afetadas. Registre arquivos complementares na visão geral; revise a fonte editável, a exportação e a descrição quando a mudança afetar o arquivo.

Para informação necessária não confirmada, escreva “Pendente”, impacto e responsável ou “responsável pendente de definição”. Execute SQL, cargas e operações de nuvem só com autorização separada. Grave arquivos locais; não finalize com apenas uma proposta de conteúdo.

**Avance quando:** páginas do escopo gravadas e lacunas identificadas por impacto e responsável.

## 4. Revise e entregue

Compare a seção 0 da visão geral com o modelo. Confira todos os links relativos e âncoras a partir de cada arquivo, inclusive links entre páginas; separe essa verificação da renderização na Wiki. Confira compatibilidade entre DE, AE e DV, histórico, evidências e arquivos complementares. Confira o diff sem incluir alterações alheias; preserve trabalho já existente no Git. Use data obtida por ferramenta e horários em UTC.

Entregue caminhos das páginas gravadas, resumo das mudanças, verificações e pendências. Informe quando não houve teste técnico, renderização ou publicação.

## 5. Encaminhe Git, Bitbucket e Wiki

Leia `tutorial-git-bitbucket-documentacao.md` no repositório e indique o próximo passo a partir do estado real. Arquivo local, branch enviada, PR e página publicada são estados distintos. Não peça credenciais no chat nem leia arquivos de credenciais. Não faça commit, push, PR, merge ou publicação sem autorização explícita.

## Uso

Solicite: “Use `/documentar-produto-dados` para documentar clientes/[cliente]/[produto] no repositório [caminho].” Esta skill depende dos modelos presentes no repositório de documentação; não presume que estejam ao lado de `SKILL.md`.
