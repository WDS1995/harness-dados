"""hook-exec-test: roda a suíte inteira de testes unitários com cobertura.

Disparado no PostToolUse de Write/Edit. Só age quando o evento vem do agent-qa e o
arquivo alterado é .py. Grava o log completo em .entregas/<entrega>/qa/ e devolve ao
agent apenas um resumo curto.
"""

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

AGENT_QA = "harness-dados:agent-qa"
COBERTURA_MINIMA = 95.0
TEMPO_LIMITE_SEGUNDOS = 540
MAX_ITENS_NO_RESUMO = 5


def resolver_raiz(evento: dict, env: Mapping) -> Path:
    """Raiz do repo consumidor: CLAUDE_PROJECT_DIR; sem ela, o cwd do evento."""
    return Path(env.get("CLAUDE_PROJECT_DIR") or evento.get("cwd") or ".")


def pasta_relatorio(raiz: Path) -> Path:
    entregas = raiz / ".entregas"
    try:
        ativa = json.loads((entregas / "sessao.json").read_text(encoding="utf-8")).get("entrega_ativa")
    except (OSError, ValueError):
        ativa = None
    if ativa and (entregas / ativa).is_dir():
        return entregas / ativa / "qa"
    return entregas / "qa"


def rodar_pytest(raiz: Path, junit: Path, cobertura: Path) -> subprocess.CompletedProcess:
    comando = [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        "--cov", f"--cov-report=json:{cobertura}", f"--junitxml={junit}",
    ]
    return subprocess.run(comando, cwd=raiz, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=TEMPO_LIMITE_SEGUNDOS)


def ler_junit(junit: Path) -> dict | None:
    if not junit.exists():
        return None
    raiz = ET.parse(junit).getroot()
    suites = [raiz] if raiz.tag == "testsuite" else list(raiz.iter("testsuite"))
    totais = {"total": 0, "falhas": 0, "erros": 0, "ignorados": 0}
    for suite in suites:
        totais["total"] += int(suite.get("tests", 0))
        totais["falhas"] += int(suite.get("failures", 0))
        totais["erros"] += int(suite.get("errors", 0))
        totais["ignorados"] += int(suite.get("skipped", 0))
    detalhes = []
    for caso in raiz.iter("testcase"):
        problema = caso.find("failure")
        if problema is None:
            problema = caso.find("error")
        if problema is not None:
            mensagem = (problema.get("message") or "").strip().splitlines()
            detalhes.append({
                "teste": f"{caso.get('classname')}::{caso.get('name')}",
                "mensagem": (mensagem[0] if mensagem else problema.tag)[:200],
            })
    totais["detalhes"] = detalhes
    return totais


def ler_cobertura(cobertura: Path) -> dict | None:
    if not cobertura.exists():
        return None
    dados = json.loads(cobertura.read_text(encoding="utf-8"))
    abaixo = sorted(
        ({"arquivo": nome, "cobertura": round(info["summary"]["percent_covered"], 1)}
         for nome, info in dados.get("files", {}).items()
         if info["summary"]["percent_covered"] < COBERTURA_MINIMA),
        key=lambda item: item["cobertura"],
    )
    return {"total": round(dados["totals"]["percent_covered"], 1), "abaixo_do_minimo": abaixo}


def montar_resumo(testes: dict | None, cobertura: dict | None, aprovado: bool, saida_bruta: str) -> str:
    if testes is None:
        ultimas = "\n".join(saida_bruta.strip().splitlines()[-MAX_ITENS_NO_RESUMO:])
        return f"hook-exec-test: a suíte não executou (erro de coleta ou pytest ausente).\n{ultimas}"
    ok = testes["total"] - testes["falhas"] - testes["erros"] - testes["ignorados"]
    valor_cobertura = f"{cobertura['total']}%" if cobertura else "indisponível"
    linhas = [
        f"hook-exec-test {'✅' if aprovado else '❌'} | Testes: {ok} ok, "
        f"{testes['falhas'] + testes['erros']} com falha, {testes['ignorados']} ignorados | "
        f"Cobertura: {valor_cobertura} (mínimo {COBERTURA_MINIMA:g}%)"
    ]
    for item in testes["detalhes"][:MAX_ITENS_NO_RESUMO]:
        linhas.append(f"Falha: {item['teste']} - {item['mensagem']}")
    if cobertura:
        for item in cobertura["abaixo_do_minimo"][:MAX_ITENS_NO_RESUMO]:
            linhas.append(f"Abaixo do mínimo: {item['arquivo']} ({item['cobertura']}%)")
    return "\n".join(linhas)


def atualizar_estado(pasta_entrega: Path, aprovado: bool, cobertura: dict | None, quando: str) -> None:
    estado_path = pasta_entrega / "estado.json"
    if not estado_path.exists():
        return
    try:
        estado = json.loads(estado_path.read_text(encoding="utf-8"))
    except ValueError:
        return
    estado["qa"] = {
        "ultima_execucao": quando,
        "passou": aprovado,
        "cobertura": cobertura["total"] if cobertura else None,
    }
    estado_path.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    evento = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    if evento.get("agent_type") != AGENT_QA:
        return 0
    if not (evento.get("tool_input") or {}).get("file_path", "").endswith(".py"):
        return 0

    raiz = resolver_raiz(evento, os.environ)
    destino = pasta_relatorio(raiz)
    destino.mkdir(parents=True, exist_ok=True)
    junit, cobertura_json = destino / "junit.xml", destino / "cobertura.json"
    for antigo in (junit, cobertura_json):
        antigo.unlink(missing_ok=True)

    quando = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        processo = rodar_pytest(raiz, junit, cobertura_json)
        saida_bruta = processo.stdout + processo.stderr
    except subprocess.TimeoutExpired:
        saida_bruta = f"Tempo limite de {TEMPO_LIMITE_SEGUNDOS}s excedido."

    testes = ler_junit(junit)
    cobertura = ler_cobertura(cobertura_json)
    aprovado = (
        testes is not None
        and testes["total"] > 0
        and testes["falhas"] == 0
        and testes["erros"] == 0
        and cobertura is not None
        and cobertura["total"] >= COBERTURA_MINIMA
    )
    resumo = montar_resumo(testes, cobertura, aprovado, saida_bruta)

    relatorio = {"executado_em": quando, "aprovado": aprovado, "testes": testes,
                 "cobertura": cobertura, "resumo": resumo, "saida": saida_bruta}
    (destino / "relatorio.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    if destino.parent.name != ".entregas":
        atualizar_estado(destino.parent, aprovado, cobertura, quando)

    saida = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": resumo}}
    if not aprovado:
        saida["decision"] = "block"
        saida["reason"] = resumo
    # ensure_ascii evita depender do encoding do console (cp1252 no Windows).
    print(json.dumps(saida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
