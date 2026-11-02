# ADR-0001: Script único quando Libraries está off

- **Data:** 2026-10-22
- **Status:** aceita
- **Entrega:** ENT-0001

## Contexto

O padrão do harness para Glue Jobs é `jobs/<nome_job>/job.py` + `transform.py`. Esse padrão pressupõe que o job envie o módulo extra ao Glue por Libraries. No GlueJobSample, Libraries está off (contrato §6). Um módulo extra não chegaria ao runtime do Glue.

## Decisão

O job usa um único arquivo, `jobs/glue_job_sample/main.py`. A lógica fica em funções testáveis dentro do próprio arquivo, que recebem `spark` e o bucket. O boilerplate do Glue (`GlueContext`, `Job.init`/`commit`, `getResolvedOptions`) fica isolado em `main()`, e os imports de `awsglue` e `pyspark` ficam dentro dele.

## Alternativas consideradas

- **Dois arquivos (`job.py` + `transform.py`) com Libraries ligado:** exigiria mudar a configuração do job no console e subir o módulo para o S3. Fora do escopo da entrega.
- **Lógica no nível do módulo, sem funções:** não foi registrada como alternativa na entrega. A escolha de funções que recebem `spark` e o bucket é o que permite os testes mockados (contrato §2 e §9, P1).

## Consequências

- O padrão `job.py + transform.py` em `.claude/rules/glue-job.md` e no `CLAUDE.md` do consumidor não vale para este job. O desvio foi aprovado (premissa P1 do contrato). A regra precisa ser revisada pelo orquestrador (ver progresso da ENT-0001).
- Os testes importam `main.py` diretamente, com `awsglue` e `pyspark` mockados.
- Se o job passar a usar Libraries, este ADR deve ser revisto.
