# Backlog de Entregas

| ID | Título | Prioridade | Status | Pasta |
|---|---|---|---|---|
| ENT-0001 | GlueJobSample — alunos CSV → Parquet + Glue Catalog (Spark SQL) | alta | concluida | ENT-0001-gluejobsample |
| ENT-0002 | GlueJobSample: logs de progresso no job (escopo a definir no contrato; a ressalva da ENT-0001 foi rodar sem visibilidade) | alta | backlog | — |
| ENT-0003 | GlueJobSample: 6 melhorias não bloqueantes da revisão adversarial da ENT-0001 + `.gitignore` (.coverage, __pycache__). Itens: (1) test_transform.py:140-143, teste de R9 tautológico; fixar o INSERT literal (agent-qa). (2) test_dados.py:54,61, emular R4 com Decimal ROUND_HALF_UP, não round() (agent-qa). (3) data/alunos.csv, trocar as linhas 1047 e 1059 (5.999) por 5.995 e 5.994, e ajustar o teste de fronteira (agent-glue-job; teste com agent-qa). (4) test_dados.py:48-52, caixa variada também em curso (agent-qa). (5) test_job.py:155 e :147, ampliar a regex anti-DataFrame e verificar mock_calls do retorno de spark.sql (agent-qa). (6) test_job.py:97-103, runpy não usa o patch; verificar o path do bucket ou documentar o escopo do teste (agent-qa). Parecer: ENT-0001-gluejobsample/revisao-adversarial.md | média | backlog | — |
| ENT-0004 | GlueJobSample: Terraform do job com os 20 itens de configuração da ENT-0001 (§6/§7), quando o repo estiver no GitHub com IaC | média | backlog | — |

<!-- Status: backlog | em-andamento | aguardando-aprovacao | concluida | cancelada -->

## Aprendizados pendentes de promoção (repo)

Propostos no encerramento da sessão de 2026-10-22 (ENT-0001). O usuário decidiu registrá-los e avaliar na próxima sessão. Nada foi aplicado em `.claude/rules/`.

| # | Destino | Aprendizado | Status |
|---|---|---|---|
| A-01 | `.claude/rules/glue-job.md` | Todo job loga o início, cada etapa e o fim, pelo logger do Glue | pendente |
| A-02 | `.claude/rules/glue-job.md` | Script único (`main.py`) é exceção prevista quando Libraries está off | pendente |
| A-03 | `.claude/rules/testes.md` | O SQL esperado é uma string literal, nunca gerada pela função testada | pendente |
| A-04 | `.claude/rules/testes.md` | Emular o `ROUND` do Spark com `Decimal` `ROUND_HALF_UP` e incluir valores de fronteira (5.995/5.994) | pendente |
| A-05 | `.claude/rules/testes.md` | Asserção própria, por coluna, para cada propriedade do contrato | pendente |
| A-06 | `.claude/rules/testes.md` | A checagem de "só `spark.sql`" cobre também `spark.sql.return_value.mock_calls` | pendente |
| A-07 | memória do agent-glue-job | CSV de amostra gerado por script determinístico. **Decidir** se o script fica versionado no repo | pendente |

Melhorias do plugin: `BACKLOG.md (raiz do plugin)`, H-09 a H-18 (H-04 e H-06 recorreram).
