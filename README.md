# harness-dados

Plugin do Claude Code para Engenharia de Dados. Organiza a criação de **AWS Glue Jobs (PySpark) com Terraform** em um fluxo com contrato de entrega, agents especializados, testes unitários obrigatórios, revisão adversarial e documentação automática.

## Como funciona

Toda sessão roda com o **orquestrador** (Opus) como agent principal. Ele não escreve código: planeja, escreve o contrato, delega aos agents e consolida os resultados.

```
/iniciar-sessao → escriba (briefing) → contrato → ✋ aprovação
  → agent-glue-job ∥ agent-terraform → agent-qa (+ hook de testes)
  → agent-adversarial → REPROVADO? 1 ciclo de correção → ainda REPROVADO? ✋ você decide
  → ✋ aprovação final
/encerrar-sessao → agents registram aprendizados → escriba documenta → ✋ promoção para a memória
```

| Componente | Modelo | Papel |
|---|---|---|
| orquestrador | Opus 5.5 | Sessão principal: planeja, contrata, delega |
| agent-glue-job | Sonnet 5.5 | Código PySpark (`jobs/`) |
| agent-terraform | Sonnet 5.5 | Infraestrutura (`infra/`) |
| agent-qa | Haiku 5.5 | Testes unitários (`tests/`) |
| agent-adversarial | Opus 5.5 | Revisão independente de código, Terraform e testes |
| agent-escriba | Haiku 5.5 | Briefing de abertura e documentação de encerramento |
| hook-exec-test | — | Roda a suíte inteira com cobertura a cada arquivo `.py` salvo pelo agent-qa |

### Regras do fluxo

- Nenhum código é escrito sem um contrato **aprovado por você**.
- Testes **apenas unitários**, com PySpark e `awsglue` mockados e cobertura mínima de **95%**.
- Glue Job e Terraform são feitos em paralelo; QA e revisão adversarial, em sequência.
- Os agents **nunca** executam `terraform plan/apply/destroy` nem comandos na AWS.

## Pré-requisitos

- Claude Code com **auto memory ligada** (necessária para a memória dos agents).
- `python` (3.11+) no PATH, com as dependências de teste instaladas: `pip install -r requirements-dev.txt`.
- `terraform` é opcional: sem ele, a validação do Terraform fica registrada como pendência.

## Instalação

Enquanto o marketplace remoto não está publicado, use o plugin a partir de uma cópia local:

```
/plugin marketplace add C:\caminho\para\harness
/plugin install harness-dados@harness-dados-marketplace
```

Para um teste rápido, sem instalar: `claude --plugin-dir C:\caminho\para\harness`.

## Uso

1. No repo de dados, abra o Claude Code e rode `/harness-dados:iniciar-sessao`.
   - Na primeira vez, ele cria `CLAUDE.md`, `.claude/rules/`, `pyproject.toml`, `requirements-dev.txt`, `docs/` e `.entregas/`, sem sobrescrever nada que já exista.
2. Descreva o pedido. O orquestrador faz as perguntas que faltarem e apresenta o contrato para sua aprovação.
3. Acompanhe a execução e aprove a entrega no final.
4. Encerre com `/harness-dados:encerrar-sessao`.

Os comandos que ainda não têm permissão vão pedir sua aprovação durante a sessão.

## Estrutura gerada no repo de dados

```
CLAUDE.md
.claude/rules/          regras por tipo de arquivo (glue-job, terraform, testes)
.claude/agent-memory/   memória de cada agent
jobs/<nome_job>/        job.py (ponto de entrada) + transform.py (regras)
tests/                  testes unitários + conftest.py com os mocks
infra/                  modules/glue_job + jobs/<nome_job>.tf
docs/jobs/              documentação por job
docs/decisoes/          ADRs
.entregas/              backlog, sessão e uma pasta por entrega:
  <ID>-<nome>/          contrato.md, plano.md, estado.json, progresso.md, qa/
CHANGELOG.md
```

## Estrutura deste repositório

```
.claude-plugin/   manifesto do plugin e marketplace
settings.json     define o orquestrador como agent principal
agents/           orquestrador e subagents
skills/           skills de domínio e de sessão
hooks/            hooks.json + exec_test.py
templates/        arquivos criados no repo de dados pelo /iniciar-sessao
```

As decisões de arquitetura estão registradas em [CLAUDE.md](CLAUDE.md).
