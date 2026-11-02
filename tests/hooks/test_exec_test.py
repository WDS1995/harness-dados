"""Testes do hooks/exec_test.py (hook-exec-test).

O módulo é script, não pacote: é importado pelo caminho do arquivo.
"""

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

CAMINHO_HOOK = Path(__file__).resolve().parents[2] / "hooks" / "exec_test.py"


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("exec_test_hook", CAMINHO_HOOK)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _stdin_json(monkeypatch, evento: dict) -> None:
    dados = json.dumps(evento, ensure_ascii=False).encode("utf-8")
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(dados), encoding="utf-8"))


# ---------------------------------------------------------------- resolver_raiz

def test_resolver_raiz_prefere_claude_project_dir(hook):
    assert hook.resolver_raiz({"cwd": "/repo/.entregas/ENT-1"}, {"CLAUDE_PROJECT_DIR": "/repo"}) == Path("/repo")


def test_resolver_raiz_sem_env_usa_cwd_do_evento(hook):
    assert hook.resolver_raiz({"cwd": "/outro"}, {}) == Path("/outro")


def test_resolver_raiz_env_vazia_cai_para_cwd(hook):
    assert hook.resolver_raiz({"cwd": "/outro"}, {"CLAUDE_PROJECT_DIR": ""}) == Path("/outro")


def test_resolver_raiz_sem_env_e_sem_cwd_usa_ponto(hook):
    assert hook.resolver_raiz({}, {}) == Path(".")


# ---------------------------------------------------------------- main: filtros

def test_main_ignora_agent_que_nao_e_qa(hook, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    _stdin_json(monkeypatch, {
        "agent_type": "harness-dados:agent-escriba",
        "tool_input": {"file_path": "modulo.py"},
    })
    chamadas = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: chamadas.append((a, k)))

    assert hook.main() == 0
    assert chamadas == []
    assert list(tmp_path.iterdir()) == []


def test_main_ignora_arquivo_que_nao_e_py(hook, monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    _stdin_json(monkeypatch, {
        "agent_type": "harness-dados:agent-qa",
        "tool_input": {"file_path": "x.md"},
    })
    chamadas = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: chamadas.append((a, k)))

    assert hook.main() == 0
    assert chamadas == []
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------- H-09

def _fake_pytest(capturados: list, junit_xml: str, cobertura: dict):
    """Simula o pytest: registra cwd/args e grava junit/cobertura nos caminhos pedidos."""

    def fake_run(comando, **kwargs):
        capturados.append({"comando": comando, "cwd": kwargs.get("cwd")})
        for arg in comando:
            if arg.startswith("--junitxml="):
                Path(arg.split("=", 1)[1]).write_text(junit_xml, encoding="utf-8")
            elif arg.startswith("--cov-report=json:"):
                caminho = Path(arg[len("--cov-report=json:"):])
                caminho.write_text(json.dumps(cobertura), encoding="utf-8")
        return subprocess.CompletedProcess(comando, 0, stdout="", stderr="")

    return fake_run


JUNIT_OK = (
    '<?xml version="1.0"?>'
    '<testsuites><testsuite name="pytest" tests="3" failures="0" errors="0" skipped="0">'
    '<testcase classname="t" name="a"/><testcase classname="t" name="b"/>'
    '<testcase classname="t" name="c"/></testsuite></testsuites>'
)
COBERTURA_OK = {"totals": {"percent_covered": 97.5}, "files": {}}


def test_h09_pytest_roda_na_raiz_do_projeto_nao_no_cwd_do_evento(hook, monkeypatch, tmp_path, capsys):
    sub = tmp_path / "sub"
    sub.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    _stdin_json(monkeypatch, {
        "agent_type": "harness-dados:agent-qa",
        "cwd": str(sub),
        "tool_input": {"file_path": "modulo.py"},
    })
    capturados: list = []
    monkeypatch.setattr(subprocess, "run", _fake_pytest(capturados, JUNIT_OK, COBERTURA_OK))

    assert hook.main() == 0

    # pytest foi invocado uma vez, com cwd = raiz do projeto (CLAUDE_PROJECT_DIR), não = sub
    assert len(capturados) == 1
    assert capturados[0]["cwd"] == tmp_path
    assert capturados[0]["cwd"] != sub

    # relatório gravado sob a raiz, em .entregas/qa (sem sessao.json, sem entrega ativa)
    relatorio = tmp_path / ".entregas" / "qa" / "relatorio.json"
    assert relatorio.is_file()
    assert not (sub / ".entregas").exists()

    dados = json.loads(relatorio.read_text(encoding="utf-8"))
    assert dados["aprovado"] is True
    assert dados["testes"]["total"] == 3
    assert dados["cobertura"]["total"] == 97.5

    # os artefatos do pytest também ficaram sob a raiz, não sob sub
    assert (tmp_path / ".entregas" / "qa" / "junit.xml").is_file()
    assert (tmp_path / ".entregas" / "qa" / "cobertura.json").is_file()

    # saída do hook: JSON válido, sem decisão de bloqueio
    saida = json.loads(capsys.readouterr().out)
    assert "block" not in saida.get("decision", "")
    assert saida["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
