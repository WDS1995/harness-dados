"""Testes unitarios do ponto de entrada e da orquestracao (contrato ENT-0001, secoes 5 e 8).

awsglue e pyspark sao mockados pelo tests/conftest.py. Os imports de awsglue/pyspark
dentro de main() sao atendidos pelos mocks de sys.modules.
"""
import re
import runpy
import sys
from pathlib import Path

import pytest

from jobs.glue_job_sample import main as job

BUCKET = "bucket-teste"
ARQUIVO_JOB = Path(__file__).resolve().parents[3] / "jobs" / "glue_job_sample" / "main.py"


@pytest.fixture
def glue(mocker):
    """Substitui GlueContext, Job, SparkContext, getResolvedOptions e executar."""
    args = {"JOB_NAME": "GlueJobSample", "S3_BUCKET": BUCKET}
    resolve = mocker.patch.object(
        sys.modules["awsglue.utils"], "getResolvedOptions", return_value=args
    )
    glue_context_cls = mocker.patch.object(sys.modules["awsglue.context"], "GlueContext")
    job_cls = mocker.patch.object(sys.modules["awsglue.job"], "Job")
    spark_context_cls = mocker.patch.object(sys.modules["pyspark.context"], "SparkContext")
    executar = mocker.patch.object(job, "executar")
    return {
        "resolve": resolve,
        "args": args,
        "GlueContext": glue_context_cls,
        "Job": job_cls,
        "job": job_cls.return_value,
        "ctx": glue_context_cls.return_value,
        "SparkContext": spark_context_cls,
        "executar": executar,
    }


def test_main_resolve_JOB_NAME_e_S3_BUCKET_via_getResolvedOptions(glue):
    argv = ["main.py", "--JOB_NAME", "GlueJobSample", "--S3_BUCKET", BUCKET]

    job.main(argv)

    glue["resolve"].assert_called_once_with(argv, ["JOB_NAME", "S3_BUCKET"])


def test_main_cria_glue_context_a_partir_do_spark_context(glue):
    job.main(["main.py"])

    glue["SparkContext"].getOrCreate.assert_called_once_with()
    glue["GlueContext"].assert_called_once_with(glue["SparkContext"].getOrCreate.return_value)
    glue["Job"].assert_called_once_with(glue["ctx"])


def test_main_inicializa_job_com_JOB_NAME_e_argumentos(glue):
    job.main(["main.py"])

    glue["job"].init.assert_called_once_with("GlueJobSample", glue["args"])


def test_main_executa_com_spark_da_sessao_e_bucket_resolvido(glue):
    job.main(["main.py"])

    glue["executar"].assert_called_once_with(glue["ctx"].spark_session, BUCKET)


def test_main_usa_bucket_do_parametro_e_nao_valor_fixo(glue):
    glue["resolve"].return_value = {"JOB_NAME": "GlueJobSample", "S3_BUCKET": "outro-bucket-teste"}

    job.main(["main.py"])

    glue["executar"].assert_called_once_with(glue["ctx"].spark_session, "outro-bucket-teste")


def test_main_chama_etapas_na_ordem_e_commit_no_fim(glue):
    chamadas = []
    glue["job"].init.side_effect = lambda *a, **k: chamadas.append("init")
    glue["executar"].side_effect = lambda *a, **k: chamadas.append("executar")
    glue["job"].commit.side_effect = lambda *a, **k: chamadas.append("commit")

    job.main(["main.py"])

    assert chamadas == ["init", "executar", "commit"]
    glue["job"].commit.assert_called_once_with()


def test_main_registra_inicio_e_fim_no_logger(glue):
    job.main(["main.py"])

    logger = glue["ctx"].get_logger.return_value
    assert [c.args[0] for c in logger.info.call_args_list] == ["Inicio do job", "Fim do job"]


def test_bloco_main_do_script_executa_main_com_glue(glue, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--JOB_NAME", "GlueJobSample", "--S3_BUCKET", BUCKET])

    runpy.run_path(str(ARQUIVO_JOB), run_name="__main__")

    glue["resolve"].assert_called_once()
    glue["job"].commit.assert_called_once_with()


def test_executar_chama_leitura_catalogo_e_escrita_nessa_ordem(mocker, spark):
    chamadas = []

    def ler(_spark, bucket):
        chamadas.append(("ler_entrada", bucket))
        return "view_x"

    def catalogo(_spark, bucket):
        chamadas.append(("criar_catalogo", bucket))

    def escrita(_spark, view):
        chamadas.append(("escrever_saida", view))

    mocker.patch.object(job, "ler_entrada", side_effect=ler)
    mocker.patch.object(job, "criar_catalogo", side_effect=catalogo)
    mocker.patch.object(job, "escrever_saida", side_effect=escrita)

    job.executar(spark, BUCKET)

    assert chamadas == [
        ("ler_entrada", BUCKET),
        ("criar_catalogo", BUCKET),
        ("escrever_saida", "view_x"),
    ]


def test_executar_envia_sql_na_ordem_view_database_tabela_insert(spark):
    job.executar(spark, BUCKET)

    comandos = [" ".join(c.args[0].split()) for c in spark.sql.call_args_list]
    assert len(comandos) == 4
    assert comandos[0].startswith("CREATE OR REPLACE TEMPORARY VIEW alunos_raw")
    assert comandos[1] == "CREATE DATABASE IF NOT EXISTS db_alunos"
    assert comandos[2].startswith("CREATE TABLE IF NOT EXISTS db_alunos.alunos_tratados")
    assert comandos[3].startswith("INSERT OVERWRITE TABLE db_alunos.alunos_tratados SELECT")
    assert "FROM alunos_raw" in comandos[3]


def test_nao_usa_api_dataframe_somente_spark_sql(spark):
    job.executar(spark, BUCKET)

    assert {chamada[0] for chamada in spark.method_calls} == {"sql"}
    spark.read.assert_not_called()
    spark.createDataFrame.assert_not_called()


def test_codigo_do_job_nao_contem_chamadas_da_api_dataframe():
    codigo = ARQUIVO_JOB.read_text(encoding="utf-8")

    assert re.search(r"createDataFrame|\.read\b|\.write\b|\.table\(|\.toDF\(", codigo) is None


def test_caminhos_de_entrada_e_saida_derivados_do_bucket():
    assert job.caminho_entrada(BUCKET) == "s3://bucket-teste/input-alunos/alunos.csv"
    assert job.caminho_saida(BUCKET) == "s3://bucket-teste/output-table-alunos/"


def test_escrever_saida_e_montar_select_usam_view_padrao(spark):
    job.escrever_saida(spark)

    sql = " ".join(spark.sql.call_args.args[0].split())
    assert "FROM alunos_raw WHERE id_aluno IS NOT NULL" in sql
    assert "FROM alunos_raw WHERE id_aluno IS NOT NULL" in " ".join(
        job.montar_select_transformacao().split()
    )
