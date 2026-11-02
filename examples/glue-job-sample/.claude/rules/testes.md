---
paths:
  - "tests/**/*.py"
---

# Testes unitários

- Apenas testes unitários. `pyspark` e `awsglue` são sempre mockados pelo `tests/conftest.py`.
- Cobertura mínima de 95% de todo o código em `jobs/`.
- Toda regra do contrato tem um teste cujo nome cita a regra (`test_regra_<n>_...`).
- Nunca enfraqueça um teste para fazê-lo passar (`skip`, `xfail`, remoção de asserções, exclusão de cobertura).
