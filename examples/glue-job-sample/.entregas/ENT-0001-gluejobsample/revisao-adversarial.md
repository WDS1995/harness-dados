# Revisão adversarial — ENT-0001 (T4)

- Contrato: `contrato.md` v2 (aprovado)
- Revisor: agent-adversarial
- Data: 2026-10-22
- Escopo revisado: `jobs/glue_job_sample/main.py`, `data/alunos.csv`, `tests/` (conftest, test_transform, test_job, test_dados), `qa/relatorio.json`, `pyproject.toml`. Terraform fora de escopo (§2, §7).

VEREDITO: APROVADO

Nenhum apontamento bloqueante. QA: 32 testes, 0 falhas, 0 ignorados, cobertura 100% (`source = ["jobs"]`, branch on), sem `skip`, `xfail` ou `pragma: no cover`.

## Verificações feitas

| Item | Resultado |
|---|---|
| R1 a R6 (SELECT) | `WHERE id_aluno IS NOT NULL`, `INITCAP(TRIM(nome))`, `UPPER(TRIM(curso))` e `ROUND(nota_final, 2)` ficam na subconsulta. O CASE de R5 e o `YEAR` de R6 ficam na consulta externa. A subconsulta é necessária: no mesmo SELECT, o `nota_final` do CASE resolveria para a coluna da view, não para o alias. Com isso a v2 de R5 está correta. |
| R5, fronteira | Spark `ROUND` usa HALF_UP sobre a representação decimal do double (`BigDecimal(Double.toString)`): 5.999 e 5.995 viram 6.0 (APROVADO), 5.994 vira 5.99 (REPROVADO). Nulo fica nulo e cai em `SEM_NOTA`, que é o primeiro ramo. `>= 6` compara DOUBLE com INT promovido. |
| R7 | `CREATE OR REPLACE TEMPORARY VIEW v (colTypeList) USING csv OPTIONS (...)` é sintaxe válida do Spark 3.5 (`createTempViewUsing`). Com schema explícito, `header 'true'` só descarta a 1ª linha. O `dateFormat` padrão `yyyy-MM-dd` lê o DATE. Campo vazio vira null em INT e DOUBLE. Espaços à esquerda são preservados na leitura (`ignoreLeadingWhiteSpace` é false), então o TRIM tem efeito. |
| R8 | DDL idêntica à §4 em nomes, ordem e tipos, com `USING PARQUET LOCATION` derivado do bucket. |
| R9 | `INSERT OVERWRITE TABLE` por posição: INT, STRING, STRING, DOUBLE (`ROUND` de DOUBLE), STRING, INT (`YEAR`), DATE. Ordem e tipos batem com a DDL, sem cast implícito sob `storeAssignmentPolicy=ANSI`. |
| Só `spark.sql` | Não há `.read`, `.write`, `createDataFrame` nem métodos de DataFrame. Os imports de awsglue e pyspark estão isolados em `main()` (P1). |
| Parâmetros | `getResolvedOptions(argv, ["JOB_NAME", "S3_BUCKET"])`. Nenhum bucket fixo. |
| Segurança | Os testes usam `bucket-teste` e `outro-bucket-teste`. A busca por `arn:`, `amazonaws` e números de 12 dígitos em jobs/, tests/ e data/ não encontrou nada. |
| CSV (§8) | ASCII/LF, sem BOM, cabeçalho + 100 linhas, 5 colunas. Tem 5 `id_aluno` nulos (1017, 1034, 1051, 1068, 1085), 10 notas nulas, espaços extras e caixa variada em nome e curso, notas < 6 e ≥ 6, e o caso 5.999 → 6.00. |
| Testes por regra | Há `test_regra_1` a `test_regra_9`, todos sobre o SQL enviado ao `spark.sql`. R7 e R8 usam igualdade exata. R1 a R6 usam fragmentos ancorados na subconsulta e na consulta externa (ordem das colunas, CASE fora da subconsulta, WHERE no fim da subconsulta). |

## Apontamentos

| # | Severidade | Arquivo:linha | Problema | Correção esperada | Agent responsável |
|---|---|---|---|---|---|
| 1 | não bloqueante | tests/jobs/glue_job_sample/test_transform.py:140-143 | O teste de R9 compara o SQL com `montar_select_transformacao(VIEW)`, ou seja, com a própria saída do código, o que é tautológico. Nenhum teste fixa o SELECT inteiro, então uma coluna extra na subconsulta passaria (por exemplo, `nota_final AS nota_raw` antes do ROUND). | Adicionar uma asserção de igualdade com a string literal completa do INSERT/SELECT esperado. | agent-qa |
| 2 | não bloqueante | tests/jobs/glue_job_sample/test_dados.py:54,61 | O teste emula R4 com o `round()` do Python (binário e half-even), que diverge do `ROUND` do Spark (HALF_UP decimal). Exemplo: `round(6.005, 2)` dá 6.0 no Python e 6.01 no Spark. Hoje só afeta as checagens de existência, mas é um modelo errado da regra. | Usar `decimal.Decimal(str(nota)).quantize(Decimal("0.01"), ROUND_HALF_UP)` para emular o Spark. | agent-qa |
| 3 | não bloqueante | data/alunos.csv | Não há linhas na fronteira exata de R5: 5.995 (vira 6.00, APROVADO) e 5.994 (vira 5.99, REPROVADO). O §8 não exige essas linhas, mas elas são o caso que mais distingue a v2 da v1 em execução real. | Trocar duas linhas repetidas (por exemplo, 1047 e 1059, hoje 5.999) por 5.995 e 5.994, mantendo 100 linhas. | agent-glue-job (o teste correspondente em test_dados.py fica com o agent-qa) |
| 4 | não bloqueante | tests/jobs/glue_job_sample/test_dados.py:48-52 | A caixa variada é verificada só em `nome`. Para R3, nada garante que `curso` tenha caixa variada (hoje tem: `quimica`, `FISICA`). | Adicionar a mesma asserção para `linha[2]`. | agent-qa |
| 5 | não bloqueante | tests/jobs/glue_job_sample/test_job.py:155 | A regex anti-DataFrame não pega `.saveAsTable(`, `.insertInto(`, `.createOrReplaceTempView(`, `.filter(`, `.withColumn(` nem `.select(`. O teste da linha 147 também não pega chamadas sobre o retorno de `spark.sql(...)`, porque `method_calls` não registra chamadas em valores de retorno. | Ampliar a regex com esses métodos e/ou verificar `spark.sql.return_value.mock_calls == []`. | agent-qa |
| 6 | não bloqueante | tests/jobs/glue_job_sample/test_job.py:97-103 | `runpy.run_path` cria um namespace novo, então o patch de `executar` na fixture não vale ali. O teste roda o `executar` real sobre um spark mockado e não verifica se o bucket chegou a ele. Passa, mas prova menos do que o nome sugere. | Verificar `glue["ctx"].spark_session.sql` com o path `s3://bucket-teste/...`, ou documentar no teste que só valida o bloco `__main__`. | agent-qa |

## Observações (não bloqueiam)

- `INITCAP(TRIM(nome))` mantém espaços duplos internos: `Diego  ramos ` vira `Diego  Ramos`. Está conforme R2. Se o desejado for normalizar os espaços internos, isso exige **mudar o contrato** (por exemplo, `INITCAP(REGEXP_REPLACE(TRIM(nome), '\\s+', ' '))`). Responsável: orquestrador (contrato).
- `CREATE DATABASE IF NOT EXISTS db_alunos` sem LOCATION registra no Glue a localização padrão do warehouse. É inofensivo porque a tabela tem LOCATION própria, e segue exatamente o texto de R8.
- A coluna "Nulo? não" da §4 não é imposta na DDL (a v1 de Parquet no Spark não aplica NOT NULL). Ela é garantida por R1 e pelos dados, não pelo catálogo. Está conforme o contrato.
- A mudança de layout (P1, script único) diverge de `.claude/rules/glue-job.md` e do `CLAUDE.md` do consumidor (`job.py + transform.py`). É um desvio aprovado e vale registrar em `docs/jobs/` no encerramento (escriba).
- Há artefatos de execução na raiz e em `jobs/` (`.coverage`, `__pycache__/`) e nenhum `.gitignore`. Não fazem parte da entrega, mas não devem ser versionados.

## Mudança de contrato

Nenhum apontamento exige mudança de contrato. Só a observação sobre espaços internos em `nome` exigiria, e apenas se o usuário quiser outro comportamento.
