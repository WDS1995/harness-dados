# ADR-0003: R5 classifica a nota já arredondada por R4

- **Data:** 2026-10-22
- **Status:** aceita
- **Entrega:** ENT-0001

## Contexto

O contrato v1 não dizia se a classificação de `situacao` (R5) usava a nota original ou a nota arredondada por R4 (`ROUND(nota_final, 2)`). Com a nota original, uma nota como 5.999 ficaria `REPROVADO` mesmo sendo exibida como 6.00 na saída. O agent-glue-job levantou a dúvida durante a implementação.

## Decisão

`situacao` é calculada sobre a nota já arredondada por R4. Exemplo: 5.999 vira 6.00 e fica `APROVADO`. Essa decisão foi tomada pelo usuário e registrada no contrato v2.

## Alternativas consideradas

- **Classificar pela nota original:** a saída mostraria 6.00 com `REPROVADO`, o que é incoerente para o consumidor da tabela.

## Consequências

- No SQL, o CASE de R5 fica na consulta externa, e o arredondamento fica na subconsulta. No mesmo SELECT, o `nota_final` do CASE resolveria para a coluna da view, não para o alias.
- O arredondamento do Spark (HALF_UP sobre a representação decimal) define a fronteira. 5.995 e 5.999 viram 6.0 e são `APROVADO`; 5.994 vira 5.99 e é `REPROVADO`. As linhas de fronteira 5.995 e 5.994 ainda não estão no CSV (ENT-0003, apontamento 3).
