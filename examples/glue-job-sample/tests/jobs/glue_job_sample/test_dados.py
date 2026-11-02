"""Verificacoes do arquivo de amostra data/alunos.csv (contrato ENT-0001, secao 8).

Usa somente a biblioteca padrao (csv, re), sem Spark, sem AWS e sem rede.
"""
import csv
import re
from pathlib import Path

CSV = Path(__file__).resolve().parents[3] / "data" / "alunos.csv"
CABECALHO = ["id_aluno", "nome", "curso", "nota_final", "data_matricula"]


def _linhas():
    with CSV.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.reader(arquivo))


def _dados():
    return _linhas()[1:]


def test_csv_cabecalho_com_as_5_colunas_do_schema():
    assert _linhas()[0] == CABECALHO


def test_csv_tem_100_linhas_de_dados_com_5_colunas():
    dados = _dados()

    assert len(dados) == 100
    assert all(len(linha) == 5 for linha in dados)


def test_csv_datas_no_formato_yyyy_mm_dd():
    padrao = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    assert all(padrao.match(linha[4]) for linha in _dados())


def test_csv_cobre_casos_de_r1_a_r5():
    dados = _dados()
    notas = [float(linha[3]) for linha in dados if linha[3] != ""]

    # R1: id_aluno nulo
    assert any(linha[0] == "" for linha in dados)
    # R2/R3: espacos extras em nome e curso
    assert any(linha[1] != linha[1].strip() for linha in dados)
    assert any(linha[2] != linha[2].strip() for linha in dados)
    # R2: caixa variada em nome
    assert any(
        nome != nome.upper() and nome != nome.lower()
        for nome in (linha[1].strip() for linha in dados)
    )
    # R4: notas com mais de 2 casas decimais
    assert any(round(nota, 2) != nota for nota in notas)
    # R5: nota nula
    assert any(linha[3] == "" for linha in dados)
    # R5: notas abaixo e acima de 6
    assert any(nota < 6 for nota in notas)
    assert any(nota >= 6 for nota in notas)
    # R5: nota que so vira aprovada depois do arredondamento (ex.: 5.999 -> 6.00)
    assert any(nota < 6 <= round(nota, 2) for nota in notas)
