# Contrato de Entrega — {{ID}}: {{TITULO}}

| Campo | Valor |
|---|---|
| ID | {{ID}} |
| Solicitante | {{SOLICITANTE}} |
| Criado em | {{DATA}} |
| Versão | 1 |
| Status | rascunho <!-- rascunho | aprovado | em-revisao | concluido --> |

## 1. Objetivo

<!-- Qual problema de negócio esta entrega resolve. Uma ou duas frases. -->

## 2. Escopo

**Inclui:**
-

**Fora de escopo:**
-

## 3. Entradas

| Fonte | Tipo (S3, Glue Catalog, JDBC...) | Localização (lógica, sem ARN real) | Formato | Volume estimado |
|---|---|---|---|---|

**Schema de entrada:**

| Coluna | Tipo | Nulo? | Descrição |
|---|---|---|---|

## 4. Saídas

| Destino | Tipo | Localização (lógica) | Formato | Particionamento | Modo de escrita (append/overwrite/merge) |
|---|---|---|---|---|---|

**Schema de saída:**

| Coluna | Tipo | Nulo? | Origem / regra |
|---|---|---|---|

## 5. Regras de transformação

<!-- Numeradas, cada uma verificável por teste unitário. -->
1.

## 6. Glue Job

| Item | Valor |
|---|---|
| Nome do job | |
| Versão do Glue | |
| Worker type / nº de workers | |
| Parâmetros (`--ARG`) | |
| Gatilho (agendamento / evento / manual) | |

## 7. Infraestrutura (Terraform)

<!-- Recursos a criar ou alterar. Sem nomes de conta, ARNs ou segredos reais. -->
-

## 8. Critérios de aceite

<!-- Cada critério deve ser objetivo e verificável. -->
- [ ] Testes unitários passando, com PySpark e `awsglue` mockados.
- [ ] Cobertura de testes ≥ 95% de todo o código.
- [ ] Cada regra da seção 5 coberta por ao menos um teste.
- [ ]

## 9. Premissas e riscos

-

## 10. Dúvidas em aberto

<!-- O contrato só pode ser aprovado com esta seção vazia. -->
-

## 11. Aprovação

| Versão | Aprovado por | Data | Observação |
|---|---|---|---|

## 12. Histórico de alterações

| Versão | Data | Alteração | Motivo |
|---|---|---|---|
| 1 | {{DATA}} | Criação | |
