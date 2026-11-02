# Changelog

Todas as mudanças notáveis deste repo são registradas aqui.

O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [Não lançado]

### Adicionado

- Job `GlueJobSample` (`jobs/glue_job_sample/main.py`): lê o CSV de alunos no S3, aplica as regras R1 a R6 com `spark.sql`, grava Parquet e cria ou atualiza `db_alunos.alunos_tratados` no Glue Catalog (ENT-0001).
- Amostra `data/alunos.csv`, com 100 linhas fictícias geradas de forma determinística (ENT-0001).
- Testes unitários em `tests/`, com PySpark e `awsglue` mockados: 32 testes, cobertura de 100% (ENT-0001).
- Documentação do job em `docs/jobs/glue_job_sample.md` e ADRs 0001 a 0004 em `docs/decisoes/` (ENT-0001).

### Removido

- Quatro arquivos `.py` vazios na raiz do repo, a pedido do usuário.
