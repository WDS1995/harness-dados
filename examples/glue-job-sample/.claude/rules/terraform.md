---
paths:
  - "infra/**/*.tf"
---

# Terraform

- Todo Glue Job usa o módulo `infra/modules/glue_job`.
- Valores de ambiente chegam sempre por variáveis com `type` e `description`.
- Nunca execute `terraform plan`, `apply`, `destroy`, `import` ou comandos `state`.
