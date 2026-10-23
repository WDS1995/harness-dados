---
name: skill-escriba
description: Passo a passo do agent-escriba para o briefing de abertura e a documentação de encerramento de sessão do harness-dados (progresso.md, docs/jobs, ADRs, CHANGELOG, backlog).
user-invocable: false
---

# skill-escriba

## Modo abertura: briefing

1. Leia `.entregas/sessao.json` e `.entregas/backlog.md`.
2. Se houver `entrega_ativa`, leia da pasta dela: `estado.json`, as **3 últimas** entradas de `progresso.md` e a seção "Dúvidas em aberto" de `contrato.md`.
3. Leia sua memória de agent em busca de alertas relevantes para essa entrega.
4. Se o orquestrador avisou que a sessão anterior não foi encerrada, compare `estado.json` com `git status` e `git log` e aponte as divergências.
5. Devolva o briefing **no formato abaixo**, com até 15 linhas e sem alterar nenhum arquivo:

```
BRIEFING — <data>
Entrega ativa: <ID e título | nenhuma>
Fase: <fase do estado.json>  | Contrato: v<versão> <status>
Última atividade: <resumo da última entrada do progresso.md>
Pendentes: <tarefas pendentes/em-andamento, com agent>
Bloqueios: <tarefas bloqueadas e motivo | nenhum>
Alertas: <sessão não encerrada, divergências, dúvidas em aberto, itens da memória | nenhum>
Backlog: <nº de itens por status>
```

## Modo encerramento: documentação

O orquestrador envia os retornos dos agents: decisões, pendências e aprendizados candidatos.

1. **progresso.md:** acrescente uma entrada para a sessão:
   ```
   ## AAAA-MM-DD HH:MM — sessão — encerramento
   - Feito:
   - Arquivos:
   - Decisões:
   - Pendências:
   - Próximo passo:
   ```
2. **estado.json:** confira se `fase`, `tarefas` e `qa` batem com `plano.md`, com `progresso.md` e com o `git status`. Corrija apenas divergências evidentes e liste o que corrigiu.
3. **docs/jobs/<nome-do-job>.md:** crie ou atualize, se a sessão alterou um Glue Job (modelo abaixo).
4. **docs/decisoes/ADR-NNNN-<titulo>.md:** crie um ADR para cada decisão técnica relatada (modelo abaixo). Use o próximo número livre.
5. **CHANGELOG.md:** acrescente o que mudou na seção `## [Não lançado]`, no formato Keep a Changelog (Adicionado / Alterado / Corrigido / Removido).
6. **backlog.md:** atualize o status da entrega.
7. Devolva ao orquestrador:
   - a lista de arquivos criados ou alterados;
   - as divergências encontradas e corrigidas;
   - os **aprendizados candidatos**, cada um com destino sugerido (`.claude/rules/<arquivo>.md` ou memória de um agent) e o texto proposto.

## Modelo: docs/jobs/<nome-do-job>.md

```markdown
# <nome-do-job>

**Entrega de origem:** <ID> | **Contrato:** v<versão>

## Objetivo
## Entradas
| Fonte | Formato | Schema resumido |
## Saídas
| Destino | Formato | Particionamento | Modo de escrita |
## Regras de transformação
## Parâmetros (`--ARG`)
| Parâmetro | Obrigatório | Descrição |
## Infraestrutura (Terraform)
## Testes
Cobertura atual: <%> | Como rodar: <comando>
## Runbook
Como reprocessar, falhas conhecidas e o que verificar.
## Histórico
| Data | Entrega | Alteração |
```

## Modelo: docs/decisoes/ADR-NNNN-<titulo>.md

```markdown
# ADR-NNNN: <título>

- **Data:** AAAA-MM-DD
- **Status:** aceita
- **Entrega:** <ID>

## Contexto
## Decisão
## Alternativas consideradas
## Consequências
```
