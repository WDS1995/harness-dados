---
paths:
  - "infra/**/*.tf"
---

# Terraform

- Todo Glue Job usa o módulo `infra/modules/glue_job`.
- Arquivos locais do job: `${path.root}/../../jobs/<nome_job>/...` (a raiz do Terraform é `infra/jobs/`); envie `job.py` e `transform.py`.
- Provider e região (`var.aws_region`) são declarados na raiz.
- Valores de ambiente chegam sempre por variáveis com `type` e `description`.
- Nunca execute `terraform plan`, `apply`, `destroy`, `import` ou comandos `state`.
