# Documentação de AE

## Quando carregar

Leia esta referência quando a tarefa criar ou alterar modelos, tabelas, views, transformações, regras de negócio, indicadores ou testes dos dados. Preencha `ae.md` com a seção 3 do modelo do produto. Consulte `visao-geral.md` para contexto e `historico.md` para mudanças. Siga também o guia comum, indicado no SKILL.md.

## Fontes a consultar

Leia a documentação existente, o SQL ou projeto de transformação, os schemas disponíveis, a tarefa no Runrun.it, as decisões e as evidências de validação. Consulte entradas de DE e consumo por DV quando houver dependência. Código implementado não equivale a regra de negócio confirmada.

## Entrevista por assunto

Pergunte apenas o que faltar nas fontes, em rodadas de até cinco perguntas. Primeiro confirme o objetivo de negócio; depois detalhe a implementação.

| Assunto | Perguntas para preencher lacunas | Destino no template |
|---|---|---|
| Objetivo | Que necessidade a modelagem atende? Quem consome a saída? O que ficou fora do escopo? | 3.1 |
| Entradas | Quais tabelas e campos são utilizados? Quais cargas, períodos e condições precisam estar disponíveis? | 3.2 |
| Modelagem | O que uma linha representa? Qual é a chave? Como as junções e agregações alteram a quantidade e o significado das linhas? | 3.3, modelagem |
| Regras | Como cada indicador é calculado? Quais filtros e exceções se aplicam? Qual unidade, forma de agregação, data de referência e fuso? Quem validou a regra? | 3.3, regras |
| Tratamentos | Como tratar duplicidades, nulos, zeros, ausência de linhas, exclusões e alterações históricas? | 3.3, tratamentos |
| Saídas | Quais tabelas ou views são entregues? O que significam seus campos? Quem as utiliza? | 3.4 |
| Atualização | Qual rotina atualiza os dados? Como tratar atraso e reprocessamento? Qual histórico está disponível? | 3.4 |
| Validação | Quais critérios e testes foram usados? Qual resultado e período avaliado? Onde estão as evidências? | 3.5 |
| Manutenção | Quem mantém, revisa e valida o negócio? Onde estão código, configuração, tarefa, PR e suporte? | 3.6 |

Para taxas e médias, obtenha numerador, denominador e tratamento de denominador zero. Para junções, obtenha chaves, tipo, cardinalidade esperada e tratamento de ausência de correspondência. Identifique regras confirmadas, suposições e pendências separadamente.

## Se for atualização

Confirme o comportamento anterior, a mudança, o motivo, a data e o responsável. Identifique indicadores e consumidores afetados, mudanças de granularidade ou schema e necessidade de reprocessar períodos anteriores. Atualize `ae.md` para o estado vigente e acrescente o registro em `historico.md`;  não registre a mudança apenas no histórico.

Se uma decisão de negócio estiver pendente, não a resolva por inferência do SQL. Registre o comportamento implementado e encaminhe a confirmação ao responsável.

## Arquivos complementares

Pergunte se existem diagramas de modelos, relações entre bases, fluxos de transformação ou arquivos de validação. Registre-os na seção 1.1 de `visao-geral.md` com finalidade, descrição textual, fonte editável, responsável, revisão e situação. Atualize os arquivos afetados junto com o texto. Preserve evidências históricas com sua data e versão. Se não puder ler um formato, declare a limitação.

## Verificação da área

- Confira se granularidade e chave descrevem a mesma saída.
- Confira se junções e agregações explicam mudanças na quantidade de linhas.
- Confira se regras têm fórmula, filtros, exceções e situação de validação.
- Diferencie nulo, zero, ausência de linha e dado indisponível.
- Confira se os campos finais possuem definição ou dicionário referenciado.
- Separe frequência da rotina de disponibilidade efetiva para consumo.
- Registre critérios, resultados, períodos e evidências; não declare testes executados apenas porque existe código de teste.
- Identifique impactos para DE ou DV. Encaminhe a questão à área correspondente; não decida por ela.

**Conclusão:** seção de AE preenchida com fontes ou pendências explícitas, dependências conferidas e histórico e arquivos complementares coerentes. Retorne ao roteador para a revisão comum e a entrega.
