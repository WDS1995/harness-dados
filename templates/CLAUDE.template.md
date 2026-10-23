# <Nome do repositório>

Repositório de Engenharia de Dados que usa o plugin **harness-dados**. Toda sessão roda com o **orquestrador** como agent principal.

## Como trabalhar

- Comece toda sessão com `/harness-dados:iniciar-sessao` e termine com `/harness-dados:encerrar-sessao`.
- Nenhum código é escrito sem um contrato aprovado em `.entregas/<ID>/contrato.md`.
- O estado das entregas fica em `.entregas/`. A documentação durável fica em `docs/`.

## Estrutura

```
jobs/<nome_job>/       código PySpark (job.py + transform.py)
tests/                 testes unitários (PySpark e awsglue mockados, cobertura ≥ 95%)
infra/                 Terraform (modules/glue_job + jobs/<nome_job>.tf)
docs/jobs/             documentação por job
docs/decisoes/         ADRs
.entregas/             contratos, planos, estado e progresso das entregas
```

## Contexto do domínio

<!-- Preencha: áreas de negócio, fontes de dados principais, ambientes (sem segredos). -->

@docs/contexto/glossario.md
