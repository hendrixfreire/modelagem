# Validação e segurança

## Controle de fase antes de agir

- Leia `fluxo.md`, seção 1 do MODEL_SPECS.md e CHECKLIST.md; confira fase, situação, versão semântica, query em foco, gate anterior e ação autorizada.
- Não execute a próxima fase com gate pendente. Aprovação precisa corresponder à versão atual e ao objeto em foco.
- Atualize CHECKLIST.md com evidências. Item de aprovação não é marcado por teste aprovado.
- Investigação exige G01; criação/edição de SQL de entrega exige G02 vigente e autorização da query; apresentação do código exige dry run e testes prévios; variante exige G04; encerramento exige G05.
- Retomada: leia o estado persistido. Ausência de prova da aprovação exige confirmação; não deduza pelo arquivo existente.

## Antes de investigar

- Não sobrescreva um modelo sem confirmar escopo.
- Declare projeto de cobrança, região e limite de bytes antes de todo grupo de leituras; metadados sem processamento devem ser identificados como tal.
- Carregue `gcp-resource-guardrails` para limites de ação e `references/comandos.md` para comandos. Antes de usar gcloud, carregue a skill `gcloud` e confira a ajuda do comando de leitura. Não execute nenhum exemplo de escrita.
- Revise a consulta inteira e funções chamadas; começar com SELECT não prova ausência de efeitos. Recuse SQL dinâmico não resolvido, funções remotas e procedimentos. Sem DDL, DML, exportações, `CALL`, scripts de múltiplas instruções ou destino persistente.
- Use projeto, localização, GoogleSQL, limite de bytes e cache explícitos. Dry run não lê resultados; execução normal de SELECT pode gerar cobrança e resultados temporários geridos pelo serviço.

## Antes de criar ou editar SQL de entrega

- G02 vigente para a versão semântica e autorização específica da query. SQL de teste em `qNN/testes/` é permitido durante F03 e não é entrega.
- Schema, granularidade, regras e dependências suficientes para implementar sem suposição bloqueante.

## Validação por query

1. CTEs: propósito, necessidade, entradas, transformações, aliases, comentários e granularidade por etapa.
2. Interação: chaves, cardinalidade, duplicações, órfãos, filtros, agregações e risco de multiplicação de métricas.
3. Negócio: cada pergunta e regra aprovada tem resposta e teste? Casos de borda preservam significado?
4. Dry run via `scripts/bq_leitura.py`: recusa automática de `statementType` não SELECT; registre bytes reais. Erro de acesso/sintaxe/região é falha, não validação.
5. Testes de leitura aplicáveis: unicidade da chave, nulos, quantidade de linhas, cardinalidade, reconciliação de métricas e períodos. Modelo existente: compare antes/depois para provar preservação. Zero, nulo e ausência, separadamente.
6. Parâmetros representativos aprovados. Não reduza período ou conjunto silenciosamente para caber no teto; bloqueio no limite: explique e peça decisão.
7. Custos via `scripts/custo.py` com tarifa da região e câmbio congelado; valide fórmulas e unidades.
8. Registre comandos sem segredos, IDs de jobs, data, saída real reduzida e limitações. Evidência em JSON só quando necessária à reprodução.

## Auditoria final dos artefatos

Execute `scripts/auditoria.py` na pasta do modelo; confira manualmente o que ele não cobre:

- Títulos e ordem das seções fixas de MODEL_SPECS.md, GLOSSARIO.md e CONTEXT.md contra os templates.
- Correspondência entre `.sql` existentes e entradas `implementada` do mapa; link planejado não é arquivo entregue.
- ID único, pasta por query, mesmo nome de pasta e SQL, contexto presente, links relativos válidos.
- Glossário imediatamente anterior às queries; vocabulário dos artefatos coincidente com ele.
- Rastreabilidade output → regra → query → teste → evidência; autorização de cada query adicional.
- Ausência de regras não aprovadas, campos inventados, SELECT DISTINCT corretivo, GROUP BY ALL, escrita e materialização.
- Cadeia completa: fontes visitadas, deduplicação no armazenamento, ciclos e lacunas documentadas. Sem completude com acesso parcial.
- Tarifas por região/unidade, bytes rotulados medidos/estimados, fórmulas com Decimal, câmbio congelado da versão e ausência de margem arbitrária.
- Otimizações: mesmas condições, equivalência, redução mínima de 30% sem arredondar; nenhuma referência a variante descartada.
- Mudanças semânticas com aprovação, SQL, contextos, testes e custos atualizados.
- Gates e checklist coerentes com os arquivos; checklist preenchido com evidência, itens de aprovação lastreados em resposta do usuário.

Declare pendência quando faltar prova exigida; explique o que falta, não chame a entrega de validada. Entrega parcial aceita termina como `encerrado_com_pendencias`, não `concluido`.

## Cenários de revisão da própria skill

- Modelo novo: primeira pergunta só o ramo; nenhum `.sql` de entrega antes de G02.
- Modelo existente: investigação percorre toda a cadeia e preserva comportamento fora do escopo.
- Fase tecnicamente concluída: solicita gate e para; não executa a próxima fase.
- Resposta factual do usuário: não é gate aprovado.
- Retomada com arquivos mas sem aprovação: pede confirmação.
- Otimização dispensada: registra dispensa antes de F05.
- Economia de 29,99%: descarta. De 30%: só aceita com equivalência e comparação válidas.
- Custo canônico zero: não divide por zero.
- Capacidade/clustering com custo inconclusivo: bytes não são prova financeira.
- Falta de tarifa ou câmbio: informa indisponível; não inventa preço nem usa cotação atual no lugar da média congelada.
- Variante descartada: remove só arquivos locais próprios e limpa referências.

Testes estáticos não comprovam execução no BigQuery nem comportamento futuro de um LLM. Não execute modelo real só para testar a instalação desta skill sem entrevista e limites do usuário.
