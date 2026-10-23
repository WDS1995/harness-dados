---
name: skill-teste-unitario
description: Passo a passo e padrões para escrever testes unitários de AWS Glue Jobs no harness-dados, com PySpark e awsglue totalmente mockados e cobertura mínima de 95%. Use ao criar ou corrigir testes.
user-invocable: false
---

# skill-teste-unitario

## Regras fixas

- Apenas testes **unitários**. Sem Spark real, sem Docker, sem AWS, sem testes de integração.
- `pyspark` e `awsglue` são **sempre mockados** via `tests/conftest.py`, mesmo que estejam instalados.
- A cobertura mínima é **95% de todo o código** em `jobs/`.
- Toda regra da seção 5 do contrato tem pelo menos um teste, e o nome do teste cita a regra: `test_regra_3_remove_id_cliente_nulo`.

## Estrutura

```
tests/
├── conftest.py
└── jobs/<nome_job>/
    ├── test_transform.py
    └── test_job.py
```

## conftest.py padrão

Se `tests/conftest.py` não existir, crie-o exatamente assim:

```python
import sys
from unittest.mock import MagicMock

import pytest

_MODULOS_MOCKADOS = [
    "pyspark", "pyspark.sql", "pyspark.sql.functions", "pyspark.sql.types",
    "pyspark.sql.window", "pyspark.context",
    "awsglue", "awsglue.context", "awsglue.job", "awsglue.utils",
    "awsglue.dynamicframe", "awsglue.transforms",
]

for _nome in _MODULOS_MOCKADOS:
    sys.modules[_nome] = MagicMock(name=_nome)

# `from pyspark.sql import functions as F` precisa devolver o mesmo mock de sys.modules.
sys.modules["pyspark.sql"].functions = sys.modules["pyspark.sql.functions"]
sys.modules["pyspark.sql"].types = sys.modules["pyspark.sql.types"]
sys.modules["pyspark.sql"].window = sys.modules["pyspark.sql.window"]


@pytest.fixture(autouse=True)
def _resetar_mocks():
    for nome in _MODULOS_MOCKADOS:
        sys.modules[nome].reset_mock()
    yield


@pytest.fixture
def F():
    return sys.modules["pyspark.sql.functions"]


@pytest.fixture
def df():
    """DataFrame mockado: cada transformação devolve o próprio mock, permitindo encadeamento."""
    mock = MagicMock(name="DataFrame")
    for metodo in ("filter", "where", "withColumn", "withColumnRenamed", "select",
                   "drop", "dropDuplicates", "join", "groupBy", "agg", "union",
                   "unionByName", "orderBy", "alias", "distinct", "repartition"):
        getattr(mock, metodo).return_value = mock
    return mock
```

## Como testar com mocks

Com mocks, `F.col("a")` e `F.col("b")` devolvem **o mesmo** objeto. Por isso, verificar só o argumento de `df.filter(...)` não prova nada. Verifique sempre:

1. **Os nomes de coluna e os literais usados:** `F.col.assert_any_call("id_cliente")`.
2. **O método chamado no DataFrame:** `df.filter.assert_called_once()`.
3. **A operação aplicada sobre a coluna:** `F.col.return_value.isNotNull.assert_called_once()`.
4. **O retorno da função:** `assert resultado is df.filter.return_value`.

No `job.py`, use `mocker.patch("jobs.<nome_job>.job.<Nome>")` para `getResolvedOptions`, `GlueContext` e `Job`. Teste:
- `main` chamando cada etapa na ordem e chamando `job.commit()`;
- `ler_entrada` e `escrever_saida` recebendo os parâmetros certos.

## Passo a passo

1. Leia a seção 5 do contrato e o código em `jobs/<nome_job>/`.
2. Crie o `conftest.py` padrão, se ele não existir.
3. Escreva `test_transform.py`: pelo menos um teste por regra, cobrindo também os ramos (`if`/`else`) de cada função.
4. Escreva `test_job.py`: `main`, `ler_entrada` e `escrever_saida`.
5. A cada arquivo `.py` que você salvar, o **hook-exec-test** roda a suíte inteira e devolve um resumo. Se o resumo indicar falha ou cobertura abaixo de 95%, corrija **seus testes** e salve de novo.
6. Se um teste falhar porque **o código de produção está errado** (diverge do contrato), não altere `jobs/`. Registre a falha e siga para o próximo item.
7. Devolva ao orquestrador:
   - resultado final (testes ok/falhos e cobertura);
   - mapa regra → teste;
   - defeitos encontrados no código de produção, cada um com a regra do contrato violada e o agent responsável (`agent-glue-job`).
