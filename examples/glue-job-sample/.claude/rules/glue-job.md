---
paths:
  - "jobs/**/*.py"
---

# Glue Jobs

- `transform.py` contém só funções puras DataFrame → DataFrame, uma por regra do contrato, com o número da regra na docstring.
- `job.py` contém o ponto de entrada (`main`), a leitura, a escrita e o `job.commit()`. Nada de lógica de negócio.
- Parâmetros apenas via `--ARG`. Nenhum caminho, bucket ou conta fixos no código.
- Importe funções do Spark como `from pyspark.sql import functions as F`.
