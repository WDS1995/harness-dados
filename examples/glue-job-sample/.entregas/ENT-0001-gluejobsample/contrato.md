# Contrato de Entrega — ENT-0001: GlueJobSample (alunos CSV → Parquet + Glue Catalog)

| Campo | Valor |
|---|---|
| ID | ENT-0001 |
| Solicitante | Wellington Domiciano |
| Criado em | 2026-10-22 |
| Versão | 2 |
| Status | concluido <!-- rascunho | aprovado | em-revisao | concluido --> |

## 1. Objetivo

Job de exemplo para validar o harness: ler um CSV de alunos no S3, aplicar transformações simples **exclusivamente com Spark SQL** (`spark.sql(...)`), gravar o resultado em outro path do mesmo bucket e criar ou atualizar, em tempo de execução, o database e a tabela no Glue Data Catalog.

## 2. Escopo

**Inclui:**
- Arquivo de amostra `data/alunos.csv`: 100 linhas de dados + cabeçalho, 5 colunas, dados **fictícios** e gerados de forma determinística.
- Código do job em `jobs/glue_job_sample/main.py`, um **script único** (ver premissa P1).
- Testes unitários em `tests/`, escritos pelo agent-qa **depois** do código, com base no código gerado e na skill-teste-unitario. PySpark e `awsglue` mockados, cobertura ≥ 95%.

**Fora de escopo:**
- Terraform/IaC. O job já existe e foi criado manualmente no console (seção 7). O agent-terraform não participa desta entrega.
- Upload do CSV e do `main.py` para o S3, inclusão do parâmetro `--S3_BUCKET` no console e execução do job na AWS. Ficam com o usuário.
- IAM, qualidade de dados, testes de integração.

## 3. Entradas

| Fonte | Tipo | Localização (lógica, sem ARN real) | Formato | Volume estimado |
|---|---|---|---|---|
| alunos | S3 | `s3://<S3_BUCKET>/input-alunos/alunos.csv` | CSV, cabeçalho, separador `,`, UTF-8 | 100 linhas |

`<S3_BUCKET>` é recebido em tempo de execução pelo parâmetro `--S3_BUCKET`. O valor real é informado pelo usuário no console e nunca aparece no código nem nos testes.

**Schema de entrada:**

| Coluna | Tipo | Nulo? | Descrição |
|---|---|---|---|
| id_aluno | INT | sim (linhas nulas são descartadas por R1) | Identificador do aluno |
| nome | STRING | não | Nome fictício (pode vir com espaços extras e caixa variada) |
| curso | STRING | não | Curso (pode vir com espaços extras e caixa variada) |
| nota_final | DOUBLE | sim | Nota de 0 a 10 |
| data_matricula | DATE | não | Formato `yyyy-MM-dd` |

## 4. Saídas

| Destino | Tipo | Localização (lógica) | Formato | Particionamento | Modo de escrita |
|---|---|---|---|---|---|
| alunos_tratados | S3 + Glue Catalog | `s3://<S3_BUCKET>/output-table-alunos/` e tabela `db_alunos.alunos_tratados` | Parquet | nenhum | overwrite |

**Schema de saída:**

| Coluna | Tipo | Nulo? | Origem / regra |
|---|---|---|---|
| id_aluno | INT | não | entrada, R1 |
| nome | STRING | não | R2 |
| curso | STRING | não | R3 |
| nota_final | DOUBLE | sim | R4 |
| situacao | STRING | não | R5 |
| ano_matricula | INT | não | R6 |
| data_matricula | DATE | não | entrada |

## 5. Regras de transformação

Todas implementadas com `spark.sql(...)`: leitura, transformação, escrita e catálogo. A API DataFrame não é usada.

1. **R1:** remover linhas com `id_aluno` nulo.
2. **R2:** `nome` = `INITCAP(TRIM(nome))`.
3. **R3:** `curso` = `UPPER(TRIM(curso))`.
4. **R4:** `nota_final` = `ROUND(nota_final, 2)`. Nulo continua nulo.
5. **R5:** `situacao` é calculada sobre a nota **já arredondada por R4**. Exemplo: `5.999` vira `6.00` e fica `APROVADO`. `situacao` = `'APROVADO'` se `nota_final >= 6`, `'REPROVADO'` se `nota_final < 6`, `'SEM_NOTA'` se `nota_final` for nulo.
6. **R6:** `ano_matricula` = `YEAR(data_matricula)`.
7. **R7:** leitura via `CREATE OR REPLACE TEMPORARY VIEW ... USING csv OPTIONS (path 's3://<S3_BUCKET>/input-alunos/alunos.csv', header 'true')`, com o schema da seção 3.
8. **R8:** em tempo de execução, `CREATE DATABASE IF NOT EXISTS db_alunos` e `CREATE TABLE IF NOT EXISTS db_alunos.alunos_tratados (...) USING PARQUET LOCATION 's3://<S3_BUCKET>/output-table-alunos/'`, com o schema da seção 4.
9. **R9:** a escrita é feita com `INSERT OVERWRITE TABLE db_alunos.alunos_tratados SELECT ...`, o que grava no S3 e mantém o catálogo sincronizado.

## 6. Glue Job

| Item | Valor |
|---|---|
| Nome do job | GlueJobSample |
| Script | `main.py`, script único (`jobs/glue_job_sample/main.py` no repo) |
| Versão do Glue | 5.0, Spark, Python 3 |
| Worker type / nº de workers | G.1X / 3, sem auto-scaling |
| Timeout / Max concurrency / Retries | 10 min / 1 / 0 |
| Bookmark / Job Insights | off / on |
| Metrics, Observability, Logging, Spark UI | on (Spark UI standard) |
| Glue Data Catalog como Hive metastore | on (necessário para R8 e R9) |
| Connections / Libraries / Security config | off |
| Parâmetros (`--ARG`) | `--S3_BUCKET` (obrigatório) e `--JOB_NAME` (padrão do Glue) |
| Gatilho | manual |

## 7. Infraestrutura (Terraform)

- Nenhum recurso nesta entrega. O job existe na AWS, criado manualmente, com a configuração da seção 6.
- Paths do bucket de assets (lógicos): script em `s3://<bucket-glue-assets>/scripts/`, Spark UI em `s3://<bucket-glue-assets>/sparkHistoryLogs/`, temporário em `s3://<bucket-glue-assets>/temporary/`.
- Role: `AWSGlueServiceRole` (existente). Ela precisa ter leitura e escrita no bucket de dados e permissão no Glue Catalog para criar database e tabela. Verificação a cargo do usuário.

## 8. Critérios de aceite

- [ ] Testes unitários passando, com PySpark e `awsglue` mockados.
- [ ] Cobertura de testes ≥ 95% de todo o código.
- [ ] Cada regra da seção 5 coberta por ao menos um teste, que verifica o SQL enviado ao `spark.sql`.
- [ ] O código não usa a API DataFrame para leitura, transformação ou escrita: só `spark.sql`.
- [ ] O bucket vem de `--S3_BUCKET` (`getResolvedOptions`). Nenhum bucket, conta ou ARN real no código ou nos testes.
- [ ] `data/alunos.csv` com exatamente 100 linhas de dados, 5 colunas, cabeçalho e dados fictícios. Contém casos que exercitam R1 a R5: `id_aluno` nulo, espaços e caixa variada, nota nula, notas abaixo e acima de 6.

## 9. Premissas e riscos

- **P1:** desvio aprovado do padrão `job.py + transform.py`. O job usa um arquivo único, porque Libraries está off e um módulo extra não chegaria ao Glue. A lógica fica em funções testáveis dentro de `main.py`, e o boilerplate do Glue (`GlueContext`, `Job.init`/`commit`) fica isolado em `main()`.
- **P2:** como o bookmark está off e a escrita é overwrite, cada execução reprocessa o CSV inteiro.
- **P3:** path de entrada `input-alunos/alunos.csv` confirmado pelo usuário na aprovação.
- **Risco:** se a role não tiver permissão no S3 ou no Catalog, o job falha em runtime. Os testes mockados não detectam isso.

## 10. Dúvidas em aberto

<!-- vazio -->

## 11. Aprovação

| Versão | Aprovado por | Data | Observação |
|---|---|---|---|
| 1 | Wellington Domiciano | 2026-10-22 | Aprovado na sessão; path de entrada confirmado; sem Terraform nesta entrega |
| 2 | Wellington Domiciano | 2026-10-22 | Esclarecimento de R5 (nota arredondada) aprovado na sessão |
| 2 (entrega) | Wellington Domiciano | 2026-10-22 | Entrega aprovada com ressalvas: job validado end-to-end (tabela consultada no Athena). Ressalva: o job não emite logs de progresso (ENT-0002). |

## 12. Histórico de alterações

| Versão | Data | Alteração | Motivo |
|---|---|---|---|
| 1 | 2026-10-22 | Criação | Pedido inicial do usuário |
| 2 | 2026-10-22 | R5 passa a usar a nota arredondada por R4 | Ambiguidade levantada pelo agent-glue-job; decisão do usuário |
