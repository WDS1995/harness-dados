---
name: skill-contrato
description: Elabora, valida e versiona o contrato de entrega (contrato.md) de um Glue Job antes de qualquer execução. Use quando o orquestrador receber um novo pedido, quando o contrato precisar de alteração depois de aprovado ou quando for preciso verificar se uma entrega cumpre o contrato.
---

# skill-contrato

O contrato é a fonte única de verdade da entrega. Nenhum agent executor começa a trabalhar sem um contrato com status `aprovado`.

A instância fica em `.entregas/<ID>/contrato.md` no repo consumidor. Ela é criada pelo `/iniciar-sessao` a partir do template do plugin (`../../templates/entregas/contrato.md`, relativo a esta skill).

## Passo a passo

1. **Entender o pedido.** Leia o pedido do usuário e o briefing do escriba (estado e pendências conhecidas). Identifique objetivo, entradas, saídas e regras.
2. **Levantar lacunas.** Liste tudo o que o pedido não responde: schemas, formatos, particionamento, modo de escrita, parâmetros do job, gatilho. **Não invente valores.** Faça as perguntas ao usuário de uma vez, agrupadas.
3. **Preencher o contrato.** Preencha todas as seções de `.entregas/<ID>/contrato.md`. Use apenas localizações lógicas, nunca ARNs, contas ou segredos reais.
4. **Escrever regras verificáveis.** Cada regra da seção 5 deve ser objetiva o bastante para virar um teste unitário. Ruim: "limpar os dados". Bom: "remover linhas com `id_cliente` nulo".
5. **Validar pelo checklist** abaixo. Se algum item falhar, volte ao passo 2.
6. **Apresentar para aprovação humana.** Mostre um resumo do contrato e peça aprovação explícita. Não interprete silêncio ou ambiguidade como aprovação.
7. **Registrar a aprovação.** Preencha a seção 11, mude o status para `aprovado` e atualize `.entregas/<ID>/estado.json`.

## Checklist de validação

- [ ] Objetivo e escopo (inclui e fora) preenchidos.
- [ ] Toda entrada e toda saída têm schema com tipos.
- [ ] Modo de escrita e particionamento definidos para cada saída.
- [ ] Regras de transformação numeradas e verificáveis.
- [ ] Critérios de aceite incluem testes unitários mockados e cobertura ≥ 95%.
- [ ] Seção "Dúvidas em aberto" vazia.
- [ ] Nenhum segredo, ARN ou identificador de conta real.

## Alteração de contrato aprovado

Se surgir uma mudança depois da aprovação, por exemplo um pedido de correção do agent-adversarial que altera o escopo:

1. Incremente a versão e registre a alteração na seção 12.
2. Mude o status para `em-revisao`.
3. Repita os passos 5 a 7. **Toda nova versão passa por aprovação humana.**

Correções que apenas fazem a entrega cumprir o contrato vigente **não** alteram o contrato.
