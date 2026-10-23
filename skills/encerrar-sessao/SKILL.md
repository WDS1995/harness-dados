---
name: encerrar-sessao
description: Encerra a sessão de trabalho do harness-dados. O orquestrador coleta o que cada agent precisa registrar, aciona o agent-escriba para documentar tudo e propõe aprendizados para a memória.
disable-model-invocation: true
---

# /encerrar-sessao

Execute os passos na ordem.

## 1. Fechar o trabalho em andamento

Não inicie nenhuma delegação nova. Para cada tarefa `em-andamento` em `estado.json`, registre o ponto exato em que parou. Ela deve continuar `em-andamento`, com uma nota clara para a próxima sessão.

## 2. Coletar registros dos agents

Para cada agent executor que trabalhou nesta sessão (veja `progresso.md`), delegue um pedido curto:

> "Encerramento da sessão da entrega <ID>. Atualize sua memória de agent com os aprendizados reutilizáveis desta sessão e devolva: (a) decisões técnicas tomadas, (b) pendências e (c) aprendizados candidatos a regra do repo."

Agents que não trabalharam na sessão não são acionados.

## 3. Documentação pelo escriba

Delegue ao **agent-escriba** em modo **encerramento**, com os retornos do passo 2. O escriba deve:

1. Acrescentar o resumo da sessão a `.entregas/<ID>/progresso.md`.
2. Conferir se `estado.json` reflete o estado real.
3. Atualizar `docs/jobs/<job>.md`, criar ADRs em `docs/decisoes/` para cada decisão técnica e atualizar `CHANGELOG.md`, quando aplicável.
4. Atualizar `backlog.md`.
5. Devolver a lista de **aprendizados candidatos** a `.claude/rules/` ou à memória, sem aplicá-los.

## 4. ✋ Promoção de aprendizados

Mostre os candidatos ao usuário. Aplique **somente** os que ele aprovar.

## 5. Fechar a sessão

Preencha `encerrada_em` em `.entregas/sessao.json` e mostre ao usuário um resumo de até 10 linhas: o que foi feito, o que ficou pendente e por onde começar na próxima sessão.
