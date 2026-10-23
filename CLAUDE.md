# Harness de Engenharia de Dados

Este repositório constrói um **harness reutilizável do Claude Code** para os times de Engenharia de Dados. O que sai daqui (instruções, agents, skills, hooks, commands, settings) deve ser distribuído e usado em **outros repositórios** de dados. Este repo não guarda pipelines nem código de produção.

## Contexto

- Plataforma: nuvem nativa **AWS e/ou Azure**. Primeiro caso de uso: **AWS Glue Jobs (PySpark) provisionados com Terraform**.
- Não suponha outras ferramentas (dbt, Airflow etc.) até que estejam registradas aqui.

## Como trabalhar neste repo

- **Decisões estruturais exigem validação prévia.** Antes de criar diretórios, escolher o formato de distribuição, definir taxonomia de componentes ou adicionar hooks, proponha as opções e espere a aprovação. Depois de aprovada, registre a decisão em "Decisões".
- Idioma: **português (PT-BR)** em instruções, documentação e descrições de componentes. Termos técnicos, nomes de arquivos, identificadores e frontmatter continuam em inglês.
- Este `CLAUDE.md` orienta quem **desenvolve o harness**. Ele é diferente do(s) `CLAUDE.md` que o harness vai entregar aos repos consumidores.
- Cada componente deve ter um propósito único e uma descrição precisa: `description` de skills e agents decide quando eles são acionados.
- Prefira mecanismos determinísticos (hooks, permissions) para regras que **precisam** ser cumpridas, e instruções (CLAUDE.md, skills) para orientação e conhecimento.
- Não coloque segredos, credenciais, nomes de contas ou ARNs reais em nenhum artefato.

## Arquitetura aprovada

```
/iniciar-sessao → [orquestrador] → [escriba] briefing de início
  → [orquestrador] contrato (skill-contrato) → ✋ aprovação humana
  → [glue-job] / [terraform] → [qa] + hook-exec-test (PostToolUse)
  → [adversarial] → REPROVADO? → orquestrador → agent responsável → qa → adversarial (1 ciclo)
  → REPROVADO de novo? → ✋ usuário decide
  → ✋ aprovação humana
/encerrar-sessao → [orquestrador] → [escriba] e demais agents documentam
```

| Componente | Tipo | Modelo | Papel |
|---|---|---|---|
| orquestrador | agent da **sessão principal** via `settings.json` do plugin (nunca subagent) | Opus 5.5 | Planeja, escreve o contrato, delega, recebe resultados |
| agent-glue-job | subagent + skill-glue-job | Sonnet 5.5 | Executor criativo: código do Glue Job |
| agent-terraform | subagent + skill-terraform | Sonnet 5.5 | Executor criativo: infraestrutura |
| agent-qa | subagent + skill-teste-unitario | Haiku 5.5 | Executor reativo: escreve e corrige testes unitários |
| agent-adversarial | subagent, revisor | Opus 5.5 | Revisa a entrega contra o contrato; pede correções ao orquestrador |
| agent-escriba | subagent + skill-escriba | Haiku 5.5 | Executor reativo: chamado no **início e no fim** de toda sessão |
| skill-contrato | skill | — | Template e checklist do contrato de entrega |
| hook-exec-test | hook global `PostToolUse` (Python), filtrado por `agent_type` = agent-qa | — | Roda a **suíte inteira** com cobertura após edições de `.py` pelo agent-qa; devolve só o resumo |

## Decisões

| # | Data | Decisão | Motivo |
|---|------|---------|--------|
| 1 | 2026-10-22 | Repo é um harness reutilizável, em PT-BR | Servir vários repos de dados |
| 2 | 2026-10-22 | Orquestrador é o agent da sessão principal, ativado por `/iniciar-sessao` | Subagents não podem chamar outros subagents |
| 3 | 2026-10-22 | `/encerrar-sessao` aciona o orquestrador, que chama os subagents para documentar | Fechamento padronizado |
| 4 | 2026-10-22 | Escriba é chamado no início e no fim de toda sessão | Continuidade entre sessões |
| 5 | 2026-10-22 | Apenas testes unitários, cobertura mínima de **95% de todo o código** | Qualidade sem custo de ambiente |
| 6 | 2026-10-22 | PySpark e `awsglue` sempre mockados; sem Spark, sem Docker, sem testes de integração | Testes rápidos e locais |
| 7 | 2026-10-22 | Testes disparados por hook `PostToolUse` | Execução determinística |
| 8 | 2026-10-22 | agent-qa usa Haiku 5.5 (revisar depois) | Custo; tarefa reativa |
| 9 | 2026-10-22 | Gate de aprovação humana sempre presente no fluxo | Controle humano |
| 10 | 2026-10-22 | agent-adversarial pede correções ao orquestrador, que delega ao agent responsável | Orquestrador é o único que delega |
| 11 | 2026-10-22 | IAM de menor privilégio e qualidade de dados ficam fora do escopo inicial | Priorização |
| 12 | 2026-10-22 | Memória: `CLAUDE.md` curto com `@imports`, `.claude/rules/` com `paths:`, `.claude/agent-memory/<agent>/` (escopo `project`) | Contexto carregado só quando relevante |
| 13 | 2026-10-22 | Memória separada do controle de sessão (`.entregas/`); escriba propõe promoções de aprendizado, com aprovação humana | Evitar ruído e contexto inchado |
| 14 | 2026-10-22 | Commands sem acento: `/iniciar-sessao`, `/encerrar-sessao` | Compatibilidade com nomes de arquivo, Windows e git |
| 15 | 2026-10-22 | Scripts de hook em Python | Portabilidade Windows/Linux |
| 16 | 2026-10-22 | agent-adversarial usa Opus 5.5 | Revisor pelo menos do nível dos executores |
| 17 | 2026-10-22 | hook-exec-test roda a suíte inteira a cada execução e retorna ao agent apenas o resumo; log completo fica em arquivo | Garantia total sem poluir o contexto |
| 18 | 2026-10-22 | Distribuição como plugin `harness-dados`, com marketplace no próprio repo | Versionamento único de agents, skills e hooks |
| 19 | 2026-10-22 | Orquestrador ativado pelo `settings.json` do plugin (`"agent": "orquestrador"`); `/iniciar-sessao` executa o ritual de abertura | Skills não conseguem trocar o agent da sessão principal |
| 20 | 2026-10-22 | hook-exec-test é global e filtra por `agent_type` do agent-qa | Plugin agents ignoram `hooks` no frontmatter |
| 21 | 2026-10-22 | `/iniciar-sessao` e `/encerrar-sessao` são skills (`disable-model-invocation: true`); sem pasta `commands/` | Skills substituem commands |
| 22 | 2026-10-22 | CLAUDE.md e rules do consumidor são criados por bootstrap a partir de `templates/` | Plugins não distribuem CLAUDE.md nem rules |
| 23 | 2026-10-22 | Apenas 1 ciclo de correção: se o adversarial reprovar de novo, o usuário decide como seguir | Evitar loops; decisão humana |
| 24 | 2026-10-22 | Paralelizar delegações independentes sempre que possível; agent-glue-job e agent-terraform rodam em paralelo | Velocidade nas entregas |
| 25 | 2026-10-22 | agent-qa e agent-adversarial rodam em sequência; o adversarial revisa também os testes unitários | Testes mockados podem passar sem provar a regra |
| 26 | 2026-10-22 | Sem hooks adicionais por enquanto; a proibição de comandos destrutivos fica nas instruções dos agents | Priorização |
| 27 | 2026-10-22 | Padrões aprovados: `jobs/<nome_job>/job.py + transform.py`, Glue 5.0 como padrão, `infra/modules/glue_job` + `infra/jobs/<nome_job>.tf`, `tests/conftest.py` com mocks | Validados pelo usuário |
| 28 | 2026-10-22 | Sem allowlist de permissões no repo consumidor: todo comando sem permissão é aprovado pelo usuário na hora | Controle humano |
| 29 | 2026-10-22 | Sem versionamento formal do plugin por enquanto | Priorização |

## Fatos verificados (2026-10-22, teste headless com `--plugin-dir`)

- `settings.json` do plugin com `"agent": "orquestrador"` (nome simples) faz a sessão principal rodar como orquestrador.
- Hooks recebem `agent_type` com o nome do plugin como prefixo: `harness-dados:agent-escriba`, `harness-dados:orquestrador` (sessão principal). O filtro do hook-exec-test deve comparar com `harness-dados:agent-qa`.

## Layout

```
.claude-plugin/   plugin.json, marketplace.json
settings.json     agent padrão da sessão (orquestrador)
agents/           orquestrador e subagents
skills/           skills de domínio e de sessão (iniciar-sessao, encerrar-sessao)
hooks/            hooks.json + scripts Python
templates/        bootstrap do repo consumidor (CLAUDE.md, rules/, entregas/)
```

## Pendências

- Marketplace remoto (próxima etapa): publicar o repo em um remoto git e documentar a instalação para o time.
- Teste de ponta a ponta de uma entrega completa.
