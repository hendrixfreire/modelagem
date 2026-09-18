# Otimização SQL no BigQuery

Pergunte na entrevista se o usuário deseja variantes otimizadas. Para outro dialeto, leia também a skill `sql-optimization` e adapte: esta referência cobre BigQuery.

## Canônica

Implemente primeiro a canônica aprovada. Priorize leitura, estrutura mínima e comentários de propósito, granularidade e regras. Não crie canônica artificialmente ineficiente para atingir o limiar; use colunas necessárias e filtros de negócio corretos também nela.

## Técnicas válidas no BigQuery

Só proponha variante com mecanismo verificável:

- **Poda de partições:** filtro direto na coluna de partição, sem função envolvendo a coluna (`WHERE data_evento >= ...`, nunca `WHERE DATE(ts) >= ...` se `ts` é a coluna particionada). Verifique com dry run: bytes caem quando a poda funciona.
- **Poda de clustering:** filtro nas colunas de clustering na ordem definida na tabela.
- **Redução de colunas lidas:** BigQuery cobra colunas selecionadas, não linhas. Eliminar coluna grande da leitura reduz custo de forma previsível; confirme no dry run.
- **Pré-filtro equivalente:** aplicar filtro de negócio antes do join/agregação, sem mudar o resultado.
- **Reescrita de agregação:** trocar subconsulta correlacionada por window function ou agregação única, preservando granularidade e multiplicidade.

## Transformações proibidas sem prova de equivalência

`LEFT JOIN` → `INNER JOIN`, `IN` → join, `OR` → `UNION ALL`, comparação sem diferenciação de maiúsculas → sensível: qualquer uma pode remover ou duplicar linhas. Use só com testes de equivalência aprovando. Índices relacionais e tabelas temporárias não são ações permitidas nesta skill.

## Gate único por variante

`G04-v<tentativa>`: apresente canônica, técnica, ID próprio (sufixo `_otimizada`), plano de comparação e limites. Aprovação autoriza criar, testar e comparar esta variante. Edição após teste: reexecute dry run e equivalência antes da decisão.

## Comparação

1. Preserve campos, tipos, nomes, granularidade, multiplicidade, métricas, nulos, fuso e período. Sem aproximação, amostragem ou período menor para atingir economia.
2. Dry runs das duas versões sob a mesma região, parâmetros, período e fontes, via `scripts/bq_leitura.py`. Não compare dry run de uma com bytes faturados da outra.
3. Equivalência por testes de leitura dentro do teto: schema, chaves, contagens, multiplicidade, diferenças de linhas e métricas. `EXCEPT DISTINCT` isolado não detecta diferença de multiplicidade. Amostra parcial: declare o limite. Funções voláteis/dados mutáveis: fixe parâmetros comparáveis ou declare inconclusivo.
4. Economia com `scripts/custo.py --comparar`, sem arredondamento prévio:

```text
reducao = (custo_canonica - custo_otimizada) / custo_canonica
aceitar = equivalencia_validada and custo_comparavel and custo_canonica > 0 and reducao >= Decimal('0.30')
```

On-demand: bytes estimados comparáveis fundamentam economia estimada, se mínimos/arredondamentos não invalidarem a conclusão. Poda de clustering pode tornar o dry run um limite superior sem precisão: use jobs de leitura medidos dentro do teto, cache desligado, ou declare inconclusivo. Capacidade: bytes não provam economia financeira.

## Decisão

- Redução ≥ 30% e equivalência validada: retenha, atualize mapa e recomende a variante quando as condições medidas se aplicarem. Preserve a canônica.
- Redução < 30%: informe e descarte.
- Custo canônico zero: percentual indefinido; não retenha variante por esse critério.
- Equivalência falha: corrija dentro do escopo autorizado ou descarte.
- Inconclusivo: não aceite nem recomende; explique o bloqueio.

## Descarte local e sincronização

Autorizado a excluir somente a variante local criada nesta execução e arquivos exclusivos dela. Antes de remover: confira caminho dentro da pasta do modelo, ausência de symlinks e de conteúdo do usuário. Não use remoção recursiva ampla.

Remova `.sql`, `CONTEXT.md` exclusivo e pasta vazia. Remova IDs, nomes, links, comparações e referências à variante de todos os artefatos. Preserve registro genérico: `tentativa 1 — descartada`. Preserve seção fixa: `Nenhuma variante otimizada retida`. O relato econômico fica na conversa. Pesquise ID e caminho removidos em toda a pasta; confirme ausência de referências e links quebrados. Nunca apague canônica nem objeto remoto. Arquivos preexistentes dependendo da variante: pare e defina escopo com o usuário.
