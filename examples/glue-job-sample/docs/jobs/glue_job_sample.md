# GlueJobSample

**Entrega de origem:** ENT-0001 | **Contrato:** v2

## Objetivo

Job de exemplo do harness. Lê um CSV de alunos no S3, aplica transformações com `spark.sql` exclusivamente, grava o resultado em Parquet no S3 e cria ou atualiza o database e a tabela no Glue Data Catalog.

## Entradas

| Fonte | Formato | Schema resumido |
|---|---|---|
| `s3://<S3_BUCKET>/input-alunos/alunos.csv` | CSV, cabeçalho, separador `,`, UTF-8 | `id_aluno` INT (pode ser nulo); `nome` STRING; `curso` STRING; `nota_final` DOUBLE (pode ser nula, de 0 a 10); `data_matricula` DATE (`yyyy-MM-dd`) |

## Saídas

| Destino | Formato | Particionamento | Modo de escrita |
|---|---|---|---|
| `s3://<S3_BUCKET>/output-table-alunos/`, tabela `db_alunos.alunos_tratados` (Glue Catalog) | Parquet | nenhum | overwrite (`INSERT OVERWRITE TABLE`) |

Schema de saída: `id_aluno` INT; `nome` STRING; `curso` STRING; `nota_final` DOUBLE; `situacao` STRING (`APROVADO`, `REPROVADO` ou `SEM_NOTA`); `ano_matricula` INT; `data_matricula` DATE.

## Regras de transformação

Todas executadas com `spark.sql`. A API DataFrame não é usada.

1. **R1:** remove linhas com `id_aluno` nulo.
2. **R2:** `nome` = `INITCAP(TRIM(nome))`. Espaços internos extras são mantidos.
3. **R3:** `curso` = `UPPER(TRIM(curso))`.
4. **R4:** `nota_final` = `ROUND(nota_final, 2)`. Nulo continua nulo.
5. **R5:** `situacao` é calculada sobre a nota já arredondada por R4. `'APROVADO'` se `>= 6`, `'REPROVADO'` se `< 6`, `'SEM_NOTA'` se nula. Exemplo: 5.999 vira 6.00 e fica `APROVADO` (ver ADR-0003).
6. **R6:** `ano_matricula` = `YEAR(data_matricula)`.
7. **R7:** leitura por `CREATE OR REPLACE TEMPORARY VIEW alunos_raw (...) USING csv`, com o schema de entrada.
8. **R8:** `CREATE DATABASE IF NOT EXISTS db_alunos` e `CREATE TABLE IF NOT EXISTS db_alunos.alunos_tratados (...) USING PARQUET LOCATION ...`.
9. **R9:** escrita por `INSERT OVERWRITE TABLE db_alunos.alunos_tratados SELECT ...`, que grava no S3 e mantém o catálogo sincronizado.

Consequência esperada: o CSV de amostra tem 100 linhas de dados, das quais 5 têm `id_aluno` nulo. A saída esperada é de 95 linhas.

## Parâmetros (`--ARG`)

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `--S3_BUCKET` | sim | Bucket de dados. Usado para ler a entrada e gravar a saída. Informado no console ou na execução. Nunca fica fixo no código. |
| `--JOB_NAME` | sim (padrão do Glue) | Nome do job, passado pelo runtime do Glue. |

## Infraestrutura (Terraform)

- Não gerenciada por Terraform nesta entrega (contrato §2 e §7). O job foi criado manualmente no console.
- Configuração de referência: contrato v2, §6 (Glue 5.0, G.1X com 3 workers, timeout 10 min, bookmark off, Glue Catalog como Hive metastore on, Connections, Libraries e Security configuration off, gatilho manual).
- A role de execução precisa de leitura e escrita no bucket de dados e de permissão no Glue Catalog para criar database e tabela. Essa verificação ficou a cargo do usuário.
- Migração para Terraform: ENT-0004.

## Testes

Cobertura atual: 100% (branch on) | Como rodar: `python -m pytest --cov=jobs --cov-branch` na raiz do repo (PySpark e `awsglue` são mockados; a suíte não exige Spark nem AWS).

Última execução registrada: 32 testes, 0 falhas, cobertura 100% (ENT-0001, `qa/relatorio.json`).

## Runbook

- **Reprocessar:** o job reprocessa o CSV inteiro a cada execução (bookmark off, escrita overwrite). Basta executar de novo com o mesmo `--S3_BUCKET`.
- **Falha de permissão:** se a role não tiver acesso ao S3 ou ao Glue Catalog, o job falha em runtime. Os testes mockados não detectam isso.
- **Sem logs de progresso:** o job não emite logs de etapa. Até a ENT-0002 ser concluída, acompanhe pela Spark UI ou pelos logs do Glue, e aguarde o fim da execução.
- **O que verificar após a execução:** a tabela `db_alunos.alunos_tratados` deve existir no Glue Catalog e ter 95 linhas. A consulta pelo Athena foi o método usado na validação end-to-end.
- **Atenção:** `CREATE DATABASE IF NOT EXISTS` sem LOCATION usa o local padrão do warehouse. A tabela tem LOCATION própria, então isso é inofensivo.

## Histórico

| Data | Entrega | Alteração |
|---|---|---|
| 2026-10-22 | ENT-0001 | Criação do job (script único `main.py`, só `spark.sql`), da amostra `data/alunos.csv` e dos testes unitários. Contrato v1 aprovado. |
| 2026-10-22 | ENT-0001 | Contrato v2: R5 passa a usar a nota arredondada por R4. |
| 2026-10-22 | ENT-0001 | Aprovado com ressalvas após validação end-to-end na AWS. Ressalva: sem logs de progresso (ENT-0002). |
