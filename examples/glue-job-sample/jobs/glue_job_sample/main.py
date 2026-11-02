"""GlueJobSample: alunos CSV -> Parquet + Glue Data Catalog, somente com Spark SQL.

Script unico (contrato ENT-0001, premissa P1): o job nao usa Libraries, entao
nao ha modulo extra. A logica fica em funcoes que recebem `spark` e o bucket;
o boilerplate do Glue fica isolado em `main()`.
"""
import sys

DATABASE = "db_alunos"
TABELA = "alunos_tratados"
VIEW_ENTRADA = "alunos_raw"
PREFIXO_ENTRADA = "input-alunos/alunos.csv"
PREFIXO_SAIDA = "output-table-alunos/"


def caminho_entrada(bucket):
    """Retorna o path S3 do CSV de entrada."""
    return f"s3://{bucket}/{PREFIXO_ENTRADA}"


def caminho_saida(bucket):
    """Retorna o path S3 da tabela de saida."""
    return f"s3://{bucket}/{PREFIXO_SAIDA}"


def ler_entrada(spark, bucket):
    """Regra 7: cria a view temporaria sobre o CSV, com o schema da secao 3."""
    sql = (
        f"CREATE OR REPLACE TEMPORARY VIEW {VIEW_ENTRADA} ("
        "id_aluno INT, nome STRING, curso STRING, "
        "nota_final DOUBLE, data_matricula DATE) "
        "USING csv "
        f"OPTIONS (path '{caminho_entrada(bucket)}', header 'true')"
    )
    spark.sql(sql)
    return VIEW_ENTRADA


def criar_catalogo(spark, bucket):
    """Regra 8: cria database e tabela externa no Glue Catalog, se nao existirem."""
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    sql = (
        f"CREATE TABLE IF NOT EXISTS {DATABASE}.{TABELA} ("
        "id_aluno INT, nome STRING, curso STRING, nota_final DOUBLE, "
        "situacao STRING, ano_matricula INT, data_matricula DATE) "
        "USING PARQUET "
        f"LOCATION '{caminho_saida(bucket)}'"
    )
    spark.sql(sql)


def montar_select_transformacao(view=VIEW_ENTRADA):
    """Regras 1 a 6: SELECT de transformacao sobre a view de entrada.

    R1 filtra id_aluno nulo; R2 INITCAP(TRIM(nome)); R3 UPPER(TRIM(curso));
    R4 ROUND(nota_final, 2); R5 situacao a partir da nota ja arredondada;
    R6 YEAR(data_matricula).
    """
    return (
        "SELECT id_aluno, nome, curso, nota_final, "
        "CASE WHEN nota_final IS NULL THEN 'SEM_NOTA' "
        "WHEN nota_final >= 6 THEN 'APROVADO' "
        "ELSE 'REPROVADO' END AS situacao, "
        "YEAR(data_matricula) AS ano_matricula, "
        "data_matricula "
        "FROM ("
        "SELECT id_aluno, "
        "INITCAP(TRIM(nome)) AS nome, "
        "UPPER(TRIM(curso)) AS curso, "
        "ROUND(nota_final, 2) AS nota_final, "
        "data_matricula "
        f"FROM {view} "
        "WHERE id_aluno IS NOT NULL"
        ") t"
    )


def escrever_saida(spark, view=VIEW_ENTRADA):
    """Regra 9: INSERT OVERWRITE na tabela do catalogo (grava no S3)."""
    spark.sql(
        f"INSERT OVERWRITE TABLE {DATABASE}.{TABELA} "
        f"{montar_select_transformacao(view)}"
    )


def executar(spark, bucket):
    """Orquestra leitura, catalogo e escrita usando apenas spark.sql."""
    view = ler_entrada(spark, bucket)
    criar_catalogo(spark, bucket)
    escrever_saida(spark, view)


def main(argv):
    """Boilerplate do Glue: argumentos, contexto, Job.init/commit."""
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from awsglue.utils import getResolvedOptions
    from pyspark.context import SparkContext

    args = getResolvedOptions(argv, ["JOB_NAME", "S3_BUCKET"])
    glue_context = GlueContext(SparkContext.getOrCreate())
    spark = glue_context.spark_session
    job = Job(glue_context)
    job.init(args["JOB_NAME"], args)
    logger = glue_context.get_logger()

    logger.info("Inicio do job")
    executar(spark, args["S3_BUCKET"])
    logger.info("Fim do job")
    job.commit()


if __name__ == "__main__":
    main(sys.argv)
