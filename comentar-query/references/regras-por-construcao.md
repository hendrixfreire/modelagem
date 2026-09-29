# Regras por construção (SQL e outras linguagens)


Além do comentário de abertura, comente expressões internas quando a regra não for evidente ou exigir ressalva. Posicione a explicação imediatamente antes da condição ou do conjunto de condições correspondente.

Em SQL, verifique:

- `WHERE`, `HAVING` e `QUALIFY`: população mantida ou excluída, inclusive efeitos de NULL.
- `JOIN` e `ON`: chaves, preservação de linhas sem correspondência e risco de multiplicação. Diferencie unicidade esperada de unicidade comprovada.
- Datas: data de referência, janela, limites inclusivos ou exclusivos e timezone, se definido.
- `CASE`, `IF` e `COALESCE`: prioridade das alternativas, significado do ELSE e diferença entre zero, NULL e ausência de linha.
- Agregações: mudança de granularidade, numerador, denominador, unidade e média ponderada ou não, conforme a expressão.
- Janelas: grupo de `PARTITION BY`, ordenação, frame quando relevante, desempate e uso do resultado.
- Deduplicação: chave, registro mantido e limites em caso de empate. Não descreva uma escolha arbitrária como “primeiro” ou “mais recente”.
- `UNION` e `UNION ALL`: como as populações se combinam e se duplicidades são removidas ou preservadas.

Em outras linguagens, aplique o mesmo raciocínio a validações, desvios condicionais, loops, tentativas, exceções, retorno antecipado e efeitos externos. Explique limites, ordem das decisões e comportamento quando a entrada está ausente ou inválida.

Não traduza sintaxe sem explicar o efeito. Prefira “Exclui pedidos cancelados da receita” a “Filtra status”. Não invente o motivo de negócio: quando ele não estiver documentado, descreva apenas o comportamento observado. Marque uma premissa como “esperada” ou “não verificada” e uma dúvida de negócio como pendente. Não altere a implementação para resolver a dúvida.

**Critério:** cada filtro ou condição relevante tem explicação no bloco ou junto à expressão, sem duplicação desnecessária.
