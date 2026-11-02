"""Testes unitarios das regras R1 a R9 (contrato ENT-0001, secao 5).

Cada regra e verificada pelo SQL enviado ao `spark.sql`, com a SparkSession mockada.
"""
from jobs.glue_job_sample import main as job

BUCKET = "bucket-teste"
VIEW = "alunos_raw"


def normalizar(sql):
    """Colapsa espacos e quebras de linha, para comparar SQL de forma robusta."""
    return " ".join(sql.split())


def sql_da_escrita(spark):
    """Executa escrever_saida com spark mockado e devolve o SQL normalizado enviado."""
    job.escrever_saida(spark, VIEW)
    spark.sql.assert_called_once()
    return normalizar(spark.sql.call_args.args[0])


def subconsulta(sql):
    """Texto entre `FROM (` e `) t`: a camada que faz as transformacoes por coluna."""
    inicio = sql.index("FROM (") + len("FROM (")
    fim = sql.rindex(") t")
    return sql[inicio:fim]


def test_regra_1_remove_linhas_com_id_aluno_nulo(spark):
    sql = sql_da_escrita(spark)

    assert f"FROM {VIEW} WHERE id_aluno IS NOT NULL" in sql
    assert subconsulta(sql).endswith("WHERE id_aluno IS NOT NULL")


def test_regra_2_nome_initcap_de_trim(spark):
    sql = sql_da_escrita(spark)

    assert "INITCAP(TRIM(nome)) AS nome" in subconsulta(sql)


def test_regra_3_curso_upper_de_trim(spark):
    sql = sql_da_escrita(spark)

    assert "UPPER(TRIM(curso)) AS curso" in subconsulta(sql)


def test_regra_4_nota_final_arredondada_com_2_casas(spark):
    sql = sql_da_escrita(spark)

    assert "ROUND(nota_final, 2) AS nota_final" in subconsulta(sql)


def test_regra_4_nota_nula_continua_nula_sem_substituicao(spark):
    sql = sql_da_escrita(spark)

    for funcao in ("COALESCE", "IFNULL", "NVL"):
        assert funcao not in sql


def test_regra_5_situacao_sem_nota_quando_nota_nula(spark):
    sql = sql_da_escrita(spark)

    assert "WHEN nota_final IS NULL THEN 'SEM_NOTA'" in sql


def test_regra_5_situacao_aprovado_quando_nota_maior_ou_igual_a_6(spark):
    sql = sql_da_escrita(spark)

    assert "WHEN nota_final >= 6 THEN 'APROVADO'" in sql


def test_regra_5_situacao_reprovado_quando_nota_menor_que_6(spark):
    sql = sql_da_escrita(spark)

    assert "ELSE 'REPROVADO' END AS situacao" in sql


def test_regra_5_nulo_tratado_antes_dos_demais_ramos(spark):
    sql = sql_da_escrita(spark)

    assert sql.index("WHEN nota_final IS NULL") < sql.index("WHEN nota_final >= 6")
    assert sql.index("WHEN nota_final >= 6") < sql.index("ELSE 'REPROVADO'")


def test_regra_5_situacao_calculada_sobre_nota_ja_arredondada(spark):
    sql = sql_da_escrita(spark)

    # O CASE fica na consulta externa e usa o nota_final da subconsulta (ja arredondado).
    assert "SELECT id_aluno, nome, curso, nota_final, CASE WHEN nota_final IS NULL" in sql
    assert "CASE" not in subconsulta(sql)
    assert "ROUND(nota_final, 2) AS nota_final" in subconsulta(sql)


def test_regra_6_ano_matricula_e_year_de_data_matricula(spark):
    sql = sql_da_escrita(spark)

    assert "YEAR(data_matricula) AS ano_matricula, data_matricula FROM (" in sql
    assert "data_matricula FROM " + VIEW in subconsulta(sql)


def test_regra_7_view_temporaria_csv_com_header_e_path_no_bucket(spark):
    retorno = job.ler_entrada(spark, BUCKET)

    spark.sql.assert_called_once()
    sql = normalizar(spark.sql.call_args.args[0])
    assert retorno == VIEW
    assert sql == (
        "CREATE OR REPLACE TEMPORARY VIEW alunos_raw "
        "(id_aluno INT, nome STRING, curso STRING, nota_final DOUBLE, data_matricula DATE) "
        "USING csv "
        "OPTIONS (path 's3://bucket-teste/input-alunos/alunos.csv', header 'true')"
    )


def test_regra_8_cria_database_e_tabela_if_not_exists_com_location(spark):
    job.criar_catalogo(spark, BUCKET)

    assert spark.sql.call_count == 2
    database, tabela = [normalizar(c.args[0]) for c in spark.sql.call_args_list]
    assert database == "CREATE DATABASE IF NOT EXISTS db_alunos"
    assert tabela == (
        "CREATE TABLE IF NOT EXISTS db_alunos.alunos_tratados "
        "(id_aluno INT, nome STRING, curso STRING, nota_final DOUBLE, "
        "situacao STRING, ano_matricula INT, data_matricula DATE) "
        "USING PARQUET "
        "LOCATION 's3://bucket-teste/output-table-alunos/'"
    )


def test_regra_9_insert_overwrite_na_tabela_do_catalogo(spark):
    job.escrever_saida(spark, VIEW)

    spark.sql.assert_called_once()
    sql = normalizar(spark.sql.call_args.args[0])
    assert sql.startswith(
        "INSERT OVERWRITE TABLE db_alunos.alunos_tratados SELECT id_aluno, nome, curso, nota_final, CASE"
    )
    assert sql == (
        "INSERT OVERWRITE TABLE db_alunos.alunos_tratados "
        + normalizar(job.montar_select_transformacao(VIEW))
    )
