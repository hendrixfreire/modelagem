# Documentação de DV

## Quando carregar

Leia esta referência quando a tarefa criar ou alterar dashboards, relatórios, interface, filtros, cálculos na ferramenta de visualização, acessos ou publicação. Preencha `dv.md` com a seção 4 do modelo do produto. Consulte `visao-geral.md` para contexto e `historico.md` para mudanças. Siga também o guia comum, indicado no SKILL.md.

## Fontes a consultar

Leia a documentação existente, definições do relatório, configuração não sensível das fontes, páginas do produto, tarefa no Runrun.it e evidências de validação. Consulte as saídas e regras de AE. Uma captura de tela não comprova sozinha filtros, cálculos, permissões ou atualização.

## Entrevista por assunto

Pergunte apenas o que faltar nas fontes, em rodadas de até cinco perguntas.

| Assunto | Perguntas para preencher lacunas | Destino no template |
|---|---|---|
| Objetivo | Quem utiliza a interface? Que decisão ela apoia? O que está incluído e excluído? | 4.1 |
| Entradas | Quais tabelas, views ou outras fontes são consumidas? Quais dependências existem? | 4.2 |
| Interface | Quais páginas e visões existem? Quais indicadores apresentam? Como funcionam filtros, seleções padrão e interações? | 4.3 |
| Cálculos | Quais cálculos ocorrem na ferramenta? Como se relacionam com as definições de AE? Existem exceções de exibição? | 4.3 |
| Acesso | Quais perfis acessam o produto? Há restrições por usuário ou grupo? Como solicitar acesso? | 4.3 e 4.4 |
| Publicação | Qual é o link e o ambiente? Quando a interface e os dados exibidos são atualizados? | 4.4 |
| Validação | Os números foram comparados com AE? Filtros, interações e acessos foram testados? Quais critérios, resultados e evidências? | 4.5 |
| Manutenção | Quem mantém e revisa? Onde estão arquivos do relatório, configuração, tarefa, PR e suporte? | 4.6 |

Diferencie regra calculada em AE de cálculo adicional em DV. Referencie definições compartilhadas em vez de manter fórmulas divergentes. Separe atualização da interface de atualização dos dados e preserve o significado do período e dos filtros exibidos.

## Se for atualização

Confirme o comportamento anterior, o que mudou, motivo, data e responsável. Identifique páginas, indicadores, filtros, grupos de acesso e consumidores afetados. Verifique se a alteração exige rever documentação de AE; não altere a definição de negócio por conta própria.

Atualize `dv.md` para o estado vigente e `historico.md` para a mudança. Diferencie publicação em teste de publicação em produção. Não afirme disponibilidade para usuários apenas porque o arquivo do relatório foi salvo.

## Arquivos complementares

Pergunte se existem capturas de tela, mapas de navegação, fluxos de uso ou arquivos de design. Registre-os na seção 1.1 de `visao-geral.md` com finalidade, descrição textual, fonte editável, responsável, revisão e situação. Atualize imagens e descrições afetadas por mudanças na interface. Identifique capturas históricas por data e versão e remova dados pessoais ou restritos desnecessários. Se não houver ferramenta para conferir imagens, declare que a revisão visual não ocorreu.

## Verificação da área

- Confira se páginas, indicadores e filtros estão identificados e explicados.
- Confira se cálculos adicionais e referências a AE estão explícitos.
- Diferencie valores padrão dos filtros de restrições de acesso.
- Confira se links e ambientes de publicação foram verificados ou têm limitação declarada.
- Registre os resultados dos testes de números, interações e acessos separadamente.
- Diferencie inspeção textual, inspeção visual e teste funcional efetivamente realizados.
- Confira se arquivos complementares representam a interface vigente ou estão identificados como históricos ou pendentes.

**Conclusão:** seção de DV preenchida com fontes ou pendências explícitas, acesso e atualização descritos e histórico e arquivos complementares coerentes. Retorne ao roteador para a revisão comum e a entrega.
