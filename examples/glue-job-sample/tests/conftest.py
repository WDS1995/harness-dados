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


@pytest.fixture
def spark():
    """SparkSession mockada. O job só deve usar `spark.sql`."""
    return MagicMock(name="SparkSession")
