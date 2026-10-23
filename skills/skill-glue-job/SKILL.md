---
name: skill-glue-job
description: Passo a passo e padrões para escrever o código PySpark de um AWS Glue Job no harness-dados, separando a lógica de transformação (testável com mocks) do ponto de entrada do Glue. Use ao criar ou alterar um Glue Job.
user-invocable: false
---

# skill-glue-job

## Padrão de código

```
jobs/<nome_job>/
├── __init__.py
├── job.py         # ponto de entrada: argumentos, GlueContext, leitura, escrita, commit
└── transform.py   # regras de transformação: funções puras DataFrame → DataFrame
```

- **Glue 5.0** (Spark 3.5, Python 3.11), salvo se o contrato disser outra versão.
- Nome do job em `snake_case`, igual ao nome da pasta.
- Dependências: somente o que o runtime do Glue já oferece. Biblioteca extra exige registro no contrato.

### transform.py

- Uma função por regra da seção 5 do contrato, com o número da regra na docstring: `"""Regra 3: remove linhas com id_cliente nulo."""`.
- Funções recebem e devolvem `DataFrame`. Elas **não** leem nem escrevem dados, **não** usam `GlueContext` e **não** criam `SparkSession`.
- Uma função `aplicar_regras(df)` encadeia as regras na ordem do contrato.
- Importe assim, para que os mocks funcionem: `from pyspark.sql import DataFrame, functions as F`.

### job.py

- Uma função `main(argv)` com a sequência: `getResolvedOptions` → `GlueContext` → `Job.init` → `ler_entrada` → `aplicar_regras` → `escrever_saida` → `job.commit()`.
- `ler_entrada` e `escrever_saida` são funções separadas, que recebem o contexto e os parâmetros como argumentos. Assim elas podem ser testadas com mocks.
- O bloco `if __name__ == "__main__": main(sys.argv)` fica no final, sem lógica.
- Parâmetros apenas via `--ARG` do Glue, com os nomes da seção 6 do contrato. Nada de caminho, bucket ou conta fixos no código.
- Logs via `glue_context.get_logger()`, com mensagens no início e no fim de cada etapa.

## Passo a passo

1. Leia o contrato (seções 3 a 6) e as tarefas atribuídas a você em `plano.md`.
2. Crie ou altere `transform.py`: uma função por regra, depois `aplicar_regras`.
3. Crie ou altere `job.py` seguindo o padrão acima.
4. Confira que cada regra da seção 5 tem uma função correspondente e que os schemas de saída batem com a seção 4.
5. Rode `python -m py_compile jobs/<nome_job>/*.py` para garantir que o código compila.
6. Devolva ao orquestrador:
   - arquivos criados ou alterados;
   - o mapa regra → função;
   - decisões técnicas tomadas;
   - pontos em que o contrato foi ambíguo.

## O que não fazer

- Não escreva testes. Isso é do agent-qa.
- Não altere Terraform nem o contrato.
- Não use `collect()`, `toPandas()` nem `count()` fora de logs de diagnóstico.
