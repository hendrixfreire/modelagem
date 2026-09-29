# Documentação de DE

## Quando carregar

Leia esta referência quando a tarefa criar ou alterar extrações, conectores, ingestão, rotinas de carga, fontes ou destinos de dados. Preencha `de.md` com a seção 2 do modelo do produto. Consulte `visao-geral.md` para contexto e `historico.md` para mudanças. Siga também o guia comum, indicado no SKILL.md.

## Fontes a consultar

Leia a documentação existente, scripts, configuração não sensível das rotinas, schemas, especificações da origem, tarefa no Runrun.it e evidências de execução. Não leia arquivos de credenciais. Consulte as entradas esperadas por AE quando a carga alimentar modelos.

## Entrevista por assunto

Pergunte apenas o que faltar nas fontes, em rodadas de até cinco perguntas.

| Assunto | Perguntas para preencher lacunas | Destino no template |
|---|---|---|
| Objetivo | Quais dados são disponibilizados e para qual uso? Qual é o limite da ingestão? | 2.1 |
| Origem | Quais sistemas e entidades são extraídos? Quem responde pela origem? Quais permissões e dependências são necessárias? | 2.2 |
| Implementação | Quais conectores e scripts executam a carga? A extração é completa ou incremental? Como tratar paginação, duplicidades, exclusões e mudanças de estrutura? | 2.3 |
| Destino | Onde os dados são gravados e quem os consome? Qual conteúdo é entregue? | 2.4 |
| Atualização | Qual frequência e condição de execução? Qual histórico é coberto? Como tratar atraso, falha e reprocessamento? | 2.4 e 2.5 |
| Validação | Como foram conferidos volume, estrutura, integridade e disponibilidade? Quais critérios, resultados, períodos e evidências? | 2.5 |
| Manutenção | Quem mantém e revisa? Onde estão código, configuração, tarefa, PR e procedimento de suporte? | 2.6 |

Registre horários operacionais em UTC. Diferencie frequência configurada de carga concluída. Descreva acesso por função e procedimento, nunca por senha ou token. Identifique restrições da origem que afetem cobertura ou disponibilidade.

## Se for atualização

Confirme origem da demanda, comportamento anterior, mudança, motivo, data e responsável. Identifique alterações de schema, frequência, cobertura histórica e destinos. Verifique impacto nos consumidores e necessidade de reprocessamento. Documente o comportamento em falha e as condições de recuperação sem executar essas operações para preencher o documento.

Atualize `de.md` para o estado vigente e `historico.md` para a mudança. Confira os links a partir da pasta do produto. Se a origem e a saída esperada por AE divergirem, registre a divergência e solicite confirmação, sem inventar uma compatibilidade.

## Arquivos complementares

Pergunte se existem diagramas de ingestão, fluxos de carga, mapas de sistemas ou relatórios de execução. Registre cada arquivo na seção 1.1 de `visao-geral.md` com finalidade, descrição textual, fonte editável, responsável, revisão e situação. Revise os arquivos afetados pela alteração e preserve evidências históricas identificadas por data e versão. Registre limitações de leitura de formatos.

## Verificação da área

- Confira se cada destino está associado a uma origem e a uma rotina identificável.
- Confira se dependências, frequência e cobertura histórica estão explícitas.
- Diferencie extração completa, incremental e reprocessamento.
- Confira o tratamento de mudanças de estrutura, atraso e falhas quando aplicáveis.
- Confira se os testes têm resultado observado e evidência, não apenas condição esperada.
- Confira a compatibilidade documentada entre saídas de DE e entradas de AE.
- Verifique que as referências não expõem credenciais.

**Conclusão:** seção de DE preenchida com fontes ou pendências explícitas, consumidores e limitações identificados e histórico e arquivos complementares coerentes. Retorne ao roteador para a revisão comum e a entrega.
