---
name: iniciar-sessao
description: Abre uma sessão de trabalho do harness-dados. Prepara o repo na primeira execução, aciona o agent-escriba para o briefing de abertura e define a entrega da sessão.
disable-model-invocation: true
---

# /iniciar-sessao

Execute os passos na ordem. Os templates ficam em `../../templates/`, relativo ao diretório desta skill.

## 1. Bootstrap (só na primeira execução)

Se `.entregas/` não existir no repo, crie os itens abaixo a partir de `templates/`. **Nunca sobrescreva** um arquivo que já exista.

| Origem (`templates/`) | Destino no repo |
|---|---|
| `CLAUDE.template.md` | `CLAUDE.md` |
| `rules/*.md` | `.claude/rules/` |
| `pyproject.toml` | `pyproject.toml` |
| `requirements-dev.txt` | `requirements-dev.txt` |
| `docs/contexto/glossario.md` | `docs/contexto/glossario.md` |
| `entregas/backlog.md`, `entregas/sessao.json` | `.entregas/` |

Quando o destino já existir:
- **`CLAUDE.md`:** mostre ao usuário as seções do template que faltam e pergunte se pode acrescentá-las.
- **`pyproject.toml`:** verifique se as seções `[tool.pytest.ini_options]` e `[tool.coverage.*]` existem; se faltarem, mostre ao usuário o trecho a incluir.

Ao final, liste para o usuário o que foi criado e lembre que as dependências de teste estão em `requirements-dev.txt`.

## 2. Registrar a sessão

Atualize `.entregas/sessao.json`: preencha `iniciada_em` com a data e hora atuais e `encerrada_em` com `null`.

Se, antes dessa atualização, `iniciada_em` estiver preenchido e `encerrada_em` estiver `null`, a sessão anterior não foi encerrada com `/encerrar-sessao`. Avise o usuário e peça ao escriba que trate isso no briefing.

## 3. Briefing do escriba

Delegue ao **agent-escriba** em modo **abertura**. Inclua no pedido:
- o caminho de `.entregas/sessao.json` e de `.entregas/backlog.md`;
- a entrega ativa, se houver (`entrega_ativa` em `sessao.json`).

Espere de volta um briefing de até 15 linhas com:
- onde paramos (fase e última entrada de `progresso.md`);
- tarefas pendentes ou bloqueadas;
- alertas da memória e dúvidas em aberto.

## 4. Definir o foco da sessão

Mostre o briefing ao usuário e pergunte se ele quer **continuar a entrega ativa** ou **iniciar um novo pedido** do backlog ou fora dele.

- **Continuar:** retome a partir da fase registrada em `estado.json`.
- **Novo pedido:**
  1. Gere o próximo ID no formato `ENT-NNNN`, olhando o backlog.
  2. Crie `.entregas/<ID>-<nome-curto>/` com cópias de `contrato.md`, `plano.md`, `estado.json` e `progresso.md` de `templates/entregas/`.
  3. Registre a entrega no `backlog.md` e grave o **nome da pasta** (`<ID>-<nome-curto>`) em `entrega_ativa` do `sessao.json`.
  4. Siga a `skill-contrato`.
