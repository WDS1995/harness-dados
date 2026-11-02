# glue-job-sample

Entrega real feita com o harness (plugin `harness-dados`) durante a aula: um Glue Job que lê um CSV de alunos, trata os dados só com Spark SQL e grava em Parquet com tabela no Glue Data Catalog. Serve de **referência/gabarito do desafio**: compare o resultado da sua sessão com os artefatos daqui (contrato, plano, progresso, revisão adversarial, QA).

## Estrutura

```
.claude/rules/        regras do projeto (glue-job, terraform, testes)
.entregas/            artefatos do harness: contrato, plano, progresso, estado, revisão adversarial, qa/
docs/                 contexto (glossário), decisões (ADRs) e documentação do job
jobs/glue_job_sample/ main.py (script único do Glue Job)
tests/                testes unitários (PySpark e awsglue mockados)
data/alunos.csv       amostra de 100 linhas
CLAUDE.md, CHANGELOG.md, pyproject.toml, requirements-dev.txt
```

## Rodar os testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Resultado esperado: 32 testes passando, cobertura ≥ 95%.

## Como foi executado na AWS

- Job criado manualmente no console do Glue (sem Terraform nesta entrega).
- Script único `jobs/glue_job_sample/main.py` (ver `docs/decisoes/ADR-0001-script-unico-sem-libraries.md`).
- Parâmetro `--S3_BUCKET` informa o bucket; o nome real nunca aparece no código.
- Entrada: `s3://<S3_BUCKET>/input-alunos/alunos.csv`.
- Saída: `s3://<S3_BUCKET>/output-table-alunos/`, tabela `db_alunos.alunos_tratados`, consultada no Athena.

Detalhes e regras de transformação (R1 a R9): `.entregas/ENT-0001-gluejobsample/contrato.md`.
