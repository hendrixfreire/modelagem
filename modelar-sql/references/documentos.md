# Padrões dos artefatos

Formatos completos em `templates/` — copie o template, nunca redija o esqueleto. Este arquivo define regras de uso dos artefatos; a estrutura exata está nos templates.

## Diretório e nomes

Pasta padrão `tasks/<ID>/modelagem/` quando a tarefa Runrun.it estiver identificada; caso contrário, pergunte. Use exatamente `MODEL_SPECS.md`, `GLOSSARIO.md`, `CHECKLIST.md`, `CONTEXT.md`, `SKILL.md`.

```text
<modelagem>/
├── MODEL_SPECS.md
├── GLOSSARIO.md
├── CHECKLIST.md
├── q01_<nome_em_portugues>/
│   ├── q01_<nome_em_portugues>.sql
│   ├── CONTEXT.md
│   └── testes/
│       ├── q01_teste_unicidade.sql
│       └── q01_teste_reconciliacao.sql
└── q02_<nome_em_portugues>_otimizada/
    ├── q02_<nome_em_portugues>_otimizada.sql
    └── CONTEXT.md
```

- IDs estáveis `q01`, `q02` etc., sem limite de quantidade e sem reutilizar IDs removidos durante o trabalho. Snake_case em português, sem acento nos identificadores criados. Preserve identificadores externos.
- A pasta `testes/` concentra SQL de teste executado após G02; não é entrega, não precisa de gate próprio e fica na pasta da canônica que valida.
- Variante recebe ID próprio, sufixo `_otimizada` e campo `canonica_de_referencia`; nunca sobrescreva a canônica.
- A pasta `testes/` concentra SQL de teste executado após G02; não é entrega, não precisa de gate próprio e fica na pasta da canônica que valida.

## MODEL_SPECS.md

Copie `templates/MODEL_SPECS.md` e preencha. Os títulos das 14 seções são fixos e na ordem do template. Mantenha todas as seções; use `Não se aplica — <justificativa>` ou `Pendente — <motivo, impacto e responsável>`. Seção 1: subseções fixas `1.1 Identificação`, `1.2 Controle do processo` (YAML definido em `fluxo.md`) e `1.3 Histórico de gates`.

Conteúdo por seção:
1. Identificação, controle e gates — conforme `fluxo.md`.
2. Objetivo, perguntas numeradas, decisões apoiadas, consumidores e forma de uso.
3. Inclusões, exclusões, restrições e critérios de minimalismo.
4. Localização original, histórico relatado com atribuição, comportamento observado, mudança solicitada e compatibilidade preservada. Modelo novo: declare inexistência conforme relato.
5. Inventário de fontes e cadeia completa: identificador externo, tipo, papel, dependências, evidência, acesso, momento da observação, consumidores e lacunas. Vincule campos externos aos conceitos do glossário. Sem credenciais.
6. Granularidade de cada output em uma linha, chaves, cardinalidade dos joins, políticas para órfãos, duplicações e desempates.
7. Regras `RNxx`: descrição, fórmula quando aplicável, inclusões/exclusões, campos, conceitos, exemplos confirmados, aprovação e testes correspondentes.
8. Outputs: ID, propósito, consumidor, granularidade e schema (nome, tipo, nulabilidade, significado, unidade, fonte/regra, ordenação). Explique por que saída vazia é correta quando fizer parte do desenho.
9. Data de referência, fuso, períodos, filtros, frequência, atraso tolerado, correções e histórico. Descreva atualização; não a configure.
10. Custo: subseções fixas `10.1 Inventário de tamanho` a `10.6 Limitações e evidências`, no template. Siga `custos-bigquery.md` e `comandos.md`. Diferencie tamanho armazenado e bytes de leitura. Output não materializado: tamanho não medido; não materialize para medir.
11. Testes: por regra/output, consulta, resultado esperado, tolerância, evidência real, data e estado. Teste não executado não é aprovado.
12. Pendências e decisões: ID, pergunta, alternativas, impacto, responsável, bloqueio, resolução. Hipótese não é fato.
13. Mapa de queries: ID, nome, papel (canônica/otimizada), output, regras atendidas, dependências, caminho relativo do SQL e contexto, estado (`planejada`/`implementada`), autorização, canônica de referência. `planejada` não afirma existência de arquivo. Sem código integral.
14. Histórico: data, versão, mudança, motivo, impacto, aprovação, testes e custos atualizados. Variante descartada: registre apenas a tentativa genérica, sem nomes, IDs, caminhos ou resultados.

## GLOSSARIO.md

Copie `templates/GLOSSARIO.md`. Só vocabulário de negócio discutido e confirmado; fórmulas e mapeamentos ficam no MODEL_SPECS.md. Sem sinônimos confusos; nomes externos não mudam por uniformidade visual.

## CONTEXT.md

Copie `templates/CONTEXT.md`. Linguagem natural com vocabulário do glossário, sem duplicar SQL: propósito, consumidor, granularidade, entradas, regras por ID, parâmetros e modo de uso. Variante aceita: equivalência, canônica correspondente e motivo econômico. Links relativos para o SQL da pasta, `../MODEL_SPECS.md` e `../GLOSSARIO.md`.

## CHECKLIST.md

Copie `references/checklist.md`. Itens, evidências e pendências somente aqui; estado e gates somente no MODEL_SPECS.md. Regras de marcação na própria referência.

## Sincronização de mudanças

Antes de mudança semântica, inventarie impactos em documentos, SQL, testes e custos; peça confirmação. Atualize glossário e especificações, obtenha aprovação da revisão, e só então altere SQL. Reexecute testes afetados e dry runs. Correção textual sem mudança de significado: sincronize sem nova aprovação. Não altere arquivos externos ao modelo sem definir escopo com o usuário.
