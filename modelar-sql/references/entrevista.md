# Entrevista e árvore de decisões

## Método

Siga os gates de `fluxo.md`: coleta em F01, investigação técnica em F02 (após G01), especificação e G02 em seguida. Menção a investigar aqui não autoriza antecipar fase. Complete o checklist da fase, não apenas as perguntas.

Faça rodadas por assunto. Pergunte apenas o que tem pré-requisitos resolvidos. Numere perguntas, ofereça recomendação quando houver decisão de desenho e espere respostas. Não recomende valores de regras de negócio sem fundamento. Aceite relato livre e não repita informação já fornecida. Cada resposta resolve uma decisão, abre investigação técnica ou cria pendência com impacto e responsável.

Se o dialeto não for BigQuery, identifique o banco em F01 e adapte os comandos de `comandos.md` mantendo o fluxo.

## Rodada inicial — ramo

Pergunte isoladamente: “A modelagem começa do zero ou parte de um modelo existente?”. Em retomada, confirme o ramo documentado e as mudanças.

## Rodada seguinte — objetivo comum

Pergunte, em um grupo:
- Qual é o objetivo da modelagem e qual decisão ela deve apoiar?
- Quais perguntas de análise e negócio ela deve responder? Peça exemplos de perguntas e resultados interpretáveis.
- Quem consumirá a saída e em qual ferramenta ou processo?
- Quais outputs finais imagina: tabela de análise, indicador, conjunto de tabelas ou outro? Prefere deixar o desenho dos outputs para uma proposta do agente?
- O que está fora do escopo?

Não imponha schema antes de compreender essas respostas.

## Ramo A — modelo do zero

### A1. Fontes

Quais bases alimentarão o modelo, onde estão, o que cada uma representa e quem pode esclarecer suas regras. Identificadores de projeto/dataset/tabela ou caminhos locais quando não estiverem no contexto. Cobertura histórica, atualização e limitações conhecidas. Investigue schemas existentes em vez de pedir campos transcritos.

### A2. Granularidade e saída

O que representa uma linha de cada saída, dimensões que precisam coexistir, período e chaves esperadas. O usuário imagina o schema final — campos, significados, tipos e ordem ao consumidor? Sem resposta, proponha o mínimo necessário após investigar fontes. Não assuma que toda métrica agrega em qualquer dimensão.

### A3. Regras

Aplique a rodada de regras comum. Só depois proponha relacionamentos e schema fechado.

## Ramo B — modelo existente

### B1. Localização e relato

Referência exata: tabela/view do BigQuery, arquivo SQL ou query customizada e ferramenta onde está salva. Relato livre do que o usuário sabe: criação, motivo, decisões, problemas, mudanças, atualizações, responsáveis, consumidores, documentação. Qual mudança deseja agora e o que precisa continuar compatível.

### B2. Cadeia completa

Investigação de F02 (após G01). Leia SQL e metadados disponíveis. Percorra recursivamente views, tabelas derivadas, rotinas somente para inspeção, scripts locais, processos de atualização e origens até as fontes-base. Procure consumidores e dependências a jusante em código/metadados/histórico acessível. Inventário por identificador externo com dependências, evidência, estado visitado e lacunas; detecte ciclos; não conte a mesma origem duas vezes. Não execute rotinas para descobrir o que fazem. Não confunda logs dos próprios jobs com inventário completo do projeto.

Informe dependências sem acesso, código não disponível, SQL dinâmico não resolvido e consumidores desconhecidos. Pergunte ao usuário somente sobre histórico, intenção ou referências que a investigação não recuperar. Cobertura parcial bloqueia alegação de revisão completa; peça decisão sobre prosseguir com limitação documentada quando ela não comprometer a correção.

### B3. Contraste

Comportamento observado versus desejado: granularidade, chaves, campos, métricas, regras e atualização. Preserve comportamento fora do escopo. Pergunte como resolver cada divergência de negócio. A implementação antiga não é especificação aprovada por padrão.

## Rodada comum — regras de negócio

Selecione as aplicáveis; marque temas não aplicáveis com justificativa, sem removê-los da especificação:
- Quais entidades, eventos e status entram ou ficam de fora?
- Como calcular cada métrica? Numerador, denominador, unidade, sinal, moeda e agregação?
- Como tratar descontos, cancelamentos, devoluções e rateios quando existirem?
- Como identificar duplicidade e escolher uma linha? Qual desempate determinístico?
- Quais chaves ligam as fontes? Cardinalidade esperada? O que fazer com chaves sem correspondência?
- Como distinguir zero, nulo, ausência de linha e dado indisponível?
- Qual data rege a análise: ocorrência, processamento ou atualização? Fuso e fronteira do período?
- Como tratar registros atrasados, correções retroativas e histórico de atributos?
- Quais casos de borda confirmam a regra? Resultados de referência e tolerâncias para validá-la?
- Há dados pessoais, restrição de acesso ou campos que não devem chegar à saída?

Registre como `RN01`, `RN02` etc., ligadas a conceitos do glossário, campos, aprovação e teste. Exemplos hipotéticos são perguntas, nunca resultados reais.

## Rodada comum — operação, custos e otimização

Pergunte antes do acesso à nuvem:
- Qual projeto de cobrança, região e limite de bytes por consulta? Limite agregado para a investigação?
- Cobrança on-demand ou por capacidade? Se desconhecida, qual escopo de leitura permite verificar?
- Frequência de execução e uso pelos consumidores? Cenários mínimo e máximo para a projeção?
- “Deseja gerar variantes otimizadas, além das queries canônicas? Só manterei variantes equivalentes que reduzam o custo de processamento em pelo menos 30%.”

Declare o método padrão de câmbio: média aritmética da PTAX de venda diária do BCB nos 30 dias corridos completos anteriores ao primeiro cálculo de custo do estudo, congelada para a versão semântica, sem preencher dias sem publicação. Ajuste explícito do usuário é registrado. Cotação atual não substitui a média.

## Fechamento da entrevista

Encerre F01 quando o entendimento, as informações disponíveis e as lacunas técnicas estiverem registrados. Solicite G01: aprovação do entendimento e autorização da investigação com projeto, região e limites. Aprovação do entendimento não é G02. Divergência de regra surgida na investigação: resolva com o usuário e siga os retornos de `fluxo.md`.
