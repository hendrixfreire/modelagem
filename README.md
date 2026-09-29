# modelagem

Skills para o ciclo completo de dados em SQL e BigQuery: **modelar, entender, documentar e otimizar**. Cada skill é uma pasta com um `SKILL.md`, escrita para funcionar em **Claude Code**, **Hermes** e **Codex**.

## Visão geral

| Skill | O que faz | Quando usar |
| --- | --- | --- |
| [`modelar-sql`](modelar-sql/SKILL.md) | Conduz a modelagem por entrevista, especificação e aprovação em gates (F01 a F05), com estudo de custo, dry run e validação. Somente leitura: não publica nem materializa. | Criar ou editar um modelo SQL a partir de uma pergunta de negócio |
| [`explicar-query`](explicar-query/SKILL.md) | Explica e avalia uma query: contrato da saída, cada CTE, cardinalidade dos joins, riscos semânticos e plano de validação. | Entender ou revisar uma query existente |
| [`fichar-query`](fichar-query/SKILL.md) | Extrai fontes, CTEs, filtros, campos e saída final para uma ficha em tabelas, sem análise. Inclui script e comparador de versões. | Mapear a estrutura de uma query ou de um model `.sqlx` |
| [`comentar-query`](comentar-query/SKILL.md) | Comenta etapas, relações e regras dentro do código, sem mudar o comportamento. | Deixar SQL ou outro código legível para manutenção |
| [`otimizar-sql`](otimizar-sql/SKILL.md) | Reduz bytes lidos, custo e tempo de queries BigQuery, preservando o resultado. | Query cara ou lenta no BigQuery |
| [`documentar-produto-dados`](documentar-produto-dados/SKILL.md) | Cria ou atualiza a documentação de um produto de dados (visão geral, DE, AE, DV e histórico). | Documentar um produto no repositório de documentação |
| [`dataform-bigquery`](dataform-bigquery/SKILL.md) | Gera pipelines Dataform para BigQuery (publicada pelo Google, com notas de ambiente). | Criar ou alterar ações e fontes Dataform |

## Como as skills se conectam

```text
pergunta de negócio
      |
      v
 modelar-sql  ----->  otimizar-sql        (variante otimizada, sob gate)
      |
      v
  query pronta
      |
      +--> explicar-query    (entender e avaliar)
      +--> fichar-query      (extrair estrutura em tabelas)
      +--> comentar-query    (documentar dentro do código)
      +--> documentar-produto-dados  (páginas DE, AE e DV)
```

`dataform-bigquery` atua ao lado, quando o destino é um pipeline Dataform.

## Invocação

Todas as skills são **manuais**: usam `disable-model-invocation: true` e só rodam quando você as chama, por exemplo `/modelar-sql` ou `/explicar-query caminho/da/query.sql`. Isso evita que o agente inicie fluxos longos, edite código ou grave arquivos sem pedido.

Essa flag vale no Claude Code. No Hermes e no Codex, o que decide é a `description` de cada skill, que diz o que fazer e quando não usar.

## Instalação

Clone o repositório e crie um link simbólico por skill na pasta de skills do seu agente. Exemplo para o Claude Code:

```bash
git clone https://github.com/hendrixfreire/modelagem.git ~/.agents/skills/modelagem

for skill in modelar-sql explicar-query fichar-query comentar-query otimizar-sql documentar-produto-dados dataform-bigquery; do
  ln -sfn ../../.agents/skills/modelagem/$skill ~/.claude/skills/$skill
done
```

O agente só descobre skills em `<pasta-de-skills>/<nome>/SKILL.md`, um nível abaixo. Por isso a pasta `modelagem/` sozinha não basta: cada skill precisa do próprio link. Reinicie a sessão para a lista atualizar.

## Estrutura

```text
modelagem/
  modelar-sql/               SKILL.md, references/, scripts/, templates/
  explicar-query/            SKILL.md, references/
  fichar-query/              SKILL.md, references/, scripts/
  comentar-query/            SKILL.md, references/
  otimizar-sql/              SKILL.md, references/
  documentar-produto-dados/  SKILL.md, references/
  dataform-bigquery/         SKILL.md
```

Cada `SKILL.md` é enxuto e aponta para `references/` numa tabela "quando ler". O agente carrega só o que a tarefa exige, o que poupa contexto.

## Princípios

- **Português brasileiro**, com um termo por conceito.
- **Ferramentas por ambiente:** os nomes de ferramentas citados seguem o Hermes; o agente usa o equivalente do ambiente em que estiver (Claude Code, Hermes ou Codex).
- **Somente leitura no BigQuery** na `modelar-sql`: sem DDL, DML, tabela temporária ou materialização.
- **Custo explícito:** todo acesso declara projeto de cobrança, região e limite de bytes antes de rodar.
- **Nada de regra de negócio presumida:** o agente separa decisão, fato observado, hipótese e pendência.
- **Aprovação entre fases:** nenhum gate é concedido sozinho.

## Verificação

```bash
python3 modelar-sql/scripts/verificacao_skill.py
```

Confere estrutura, gates e templates da `modelar-sql`. O `fichar-query` tem o próprio gate, que reprova e não grava uma ficha malformada.

## Licença

[MIT](LICENSE). A `dataform-bigquery` é publicada pelo Google sob Apache-2.0.
