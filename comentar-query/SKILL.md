---
name: comentar-query
description: "Adiciona comentários de propósito, etapas, relações e regras de negócio dentro de SQL (CTEs e SELECT final) ou de qualquer código, sem alterar o comportamento. Use quando o usuário pedir para comentar, documentar no código ou facilitar a leitura. Não use para refatorar, corrigir regras, executar consultas ou explicar fora do arquivo (para isso, use explicar-query)."
disable-model-invocation: true
version: 0.3.0
author: Hendrix Freire, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [comentarios, documentacao, sql, codigo, regras-de-negocio]
    related_skills: [explicar-query, fichar-query]
---

# Comentários de etapas e regras no código

Documente o propósito, as relações e as regras de cada etapa dentro do próprio código, para quem precisa ler, manter ou validar o trabalho. Apesar do nome `comentar-query`, aplique este padrão a qualquer domínio: consultas, scripts, funções, pipelines, automações, integrações e testes. Não limite o uso a modelos de dados ou a um cliente.

> **Ferramentas por ambiente.** Esta skill roda em Claude Code, Hermes e Codex. Os nomes de ferramentas citados (`read_file`, `search_files`, `patch`, `write_file`, `clarify`) seguem o Hermes. Antes de agir, identifique o ambiente atual e use a ferramenta equivalente disponível nele para ler, buscar, editar, criar arquivos e fazer perguntas ao usuário.

## Quando usar

- Ao criar ou alterar código que tenha etapas, transformações, filtros ou decisões que precisem de explicação.
- Ao receber pedidos como “comente as CTEs”, “explique as regras no código” ou “facilite a leitura”.
- Ao documentar código existente sem alterar seu comportamento.
- Não use como autorização para refatorar, corrigir regras, executar consultas ou publicar arquivos.

## Referências (carregue sob demanda)

| Quando | Ler |
| --- | --- |
| Ao comentar filtros, joins, datas, CASE, agregações, janelas, deduplicação, UNION | [regras-por-construcao.md](references/regras-por-construcao.md) |
| Ao escrever o bloco antes do SELECT final (contagem de colunas, contrato) | [saida-final.md](references/saida-final.md) |
| Para ver o formato esperado em SQL e Python | [exemplos.md](references/exemplos.md) |

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

Comente expressões internas quando a regra não for evidente, imediatamente antes da condição. Leia [regras-por-construcao.md](references/regras-por-construcao.md) e aplique os itens pertinentes. Não invente o motivo de negócio: sem documentação, descreva só o comportamento observado e marque premissas como “esperada” ou “não verificada”.

### 5. Documente o contrato da saída final

Insira um bloco numerado como a próxima etapa (`N. saída_final`) imediatamente antes do SELECT final. Leia [saida-final.md](references/saida-final.md) e siga o inventário de colunas e os pontos de comportamento. Conte colunas com ferramentas, nunca por vírgulas.

### 6. Verifique antes de entregar

Compare o antes e o depois com ferramentas. Use `patch` para alterações em arquivos existentes e `write_file` para arquivos novos. Em tarefas de comentários, confirme que o conteúdo executável não mudou com tokens ou árvore sintática que desconsidere apenas comentários comuns e espaços irrelevantes.

Não remova comentários com regex genérica para provar equivalência: marcadores podem aparecer dentro de strings. Não trate hints SQL, diretivas, pragmas, comentários de tipagem ou docstrings como texto sem efeito. Respeite indentação significativa e posições especiais da linguagem.

Execute análise sintática ou testes locais pertinentes quando disponíveis. Não execute consultas faturáveis nem ações externas apenas para validar comentários. Se faltar analisador, revise o diff e informe esse limite; não declare equivalência comprovada por execução.

**Critério:** cobertura dos comentários e preservação da lógica verificadas; limites da verificação registrados.

Veja o formato esperado em [exemplos.md](references/exemplos.md).

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
