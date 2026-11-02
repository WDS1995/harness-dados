# Plano — ENT-0001

Contrato: `contrato.md` (versão 2, aprovado em 2026-10-22)

| Tarefa | Descrição | Agent | Depende de | Status |
|---|---|---|---|---|
| T1 | `jobs/glue_job_sample/main.py` (script único, só `spark.sql`) + `data/alunos.csv` (100 linhas fictícias) | agent-glue-job | — | concluida |
| T2 | Terraform: fora de escopo nesta entrega (contrato §2, §7) | — | — | cancelada |
| T3 | Testes unitários com base no código de T1 (cobertura ≥ 95%) | agent-qa | T1 | concluida |
| T4 | Revisão adversarial (código, CSV, testes) | agent-adversarial | T3 | concluida |

<!-- Status: pendente | em-andamento | concluida | bloqueada | cancelada -->
