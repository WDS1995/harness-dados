---
name: skill-terraform
description: Passo a passo e padrões para escrever o Terraform de um AWS Glue Job no harness-dados (job, script no S3, gatilho, parâmetros). Use ao criar ou alterar a infraestrutura de um Glue Job.
user-invocable: false
---

# skill-terraform

## Padrão de código

```
infra/
├── modules/glue_job/        # módulo reutilizável: aws_glue_job, aws_s3_object do script, gatilho opcional
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── versions.tf
└── jobs/<nome_job>.tf       # uma chamada ao módulo por job; `infra/jobs/` é a raiz do Terraform (`path.root`)
```

- Todo job usa o módulo `modules/glue_job`. Se o módulo não existir, crie-o primeiro.
- Valores de ambiente (conta, região, buckets, role) chegam **sempre** por variáveis. Nunca fixe valores reais no código.
- Os arquivos locais ficam em `jobs/` na raiz do repo. Como a raiz do Terraform é `infra/jobs/`, o caminho é `${path.root}/../../jobs/<nome_job>/...` (dois níveis acima; `../jobs` aponta para o lugar errado).
- O módulo envia **dois** arquivos ao S3 por `aws_s3_object`, cada um com `etag = filemd5(...)`: `job.py` (`source = "${path.root}/../../jobs/<nome_job>/job.py"`) e `transform.py` (`source = "${path.root}/../../jobs/<nome_job>/transform.py"`).
- A raiz (`infra/jobs/`) declara o `terraform { required_providers { aws } }` e o `provider "aws"` com `region = var.aws_region`. A região é uma variável com `description` e `type`, sem valor real no código; conta, perfil e credenciais ficam fora do código.
- `default_arguments` contém os parâmetros `--ARG` da seção 6 do contrato, mais `--job-language = python` e `--enable-continuous-cloudwatch-log = true`.
- `glue_version`, `worker_type` e `number_of_workers` vêm da seção 6 do contrato.
- Toda variável tem `description` e `type`. Os outputs expõem o nome e o ARN do job.
- Tags padrão: `entrega = <ID>`, `job = <nome_job>`.

## Passo a passo

1. Leia o contrato (seções 6 e 7) e as tarefas atribuídas a você em `plano.md`.
2. Garanta que o módulo `modules/glue_job` existe e atende ao contrato.
3. Crie ou altere `infra/jobs/<nome_job>.tf`.
4. Se o `terraform` estiver instalado, rode `terraform fmt -recursive infra/` e, em `infra/jobs/`, `terraform init -backend=false` e depois `terraform validate`. Se não estiver, registre isso como pendência.
5. Devolva ao orquestrador:
   - arquivos criados ou alterados;
   - recursos que serão criados ou alterados;
   - variáveis que precisam de valor por ambiente;
   - decisões técnicas e dúvidas.

## O que não fazer

- **Nunca** execute `terraform plan`, `apply`, `destroy`, `import` nem comandos `state`. Eles exigem credenciais e afetam ambientes.
- Não altere o código do job, os testes nem o contrato.
