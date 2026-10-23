# Backlog do harness-dados

Correções e melhorias do próprio plugin. Origem de cada item indicada na coluna "Origem".

| # | Item | Tipo | Origem | Status |
|---|---|---|---|---|
| H-01 | `skill-terraform`: corrigir o caminho dos arquivos locais a partir da raiz `infra/jobs/` (`${path.root}/../../jobs/...`, não `../jobs`); incluir o upload do `transform.py`; declarar provider e região na raiz | correção | Teste E2E 2026-10-22 (bloqueante do adversarial) | aberto |
| H-02 | Import do `transform.py` difere entre Glue (`import transform`) e testes (`jobs.<job>.transform`). Proposta: Terraform empacota `jobs/` em `.zip` (`archive_file`) e envia via `--extra-py-files`, mantendo o mesmo import nos dois ambientes. **Decisão estrutural: validar antes de aplicar** | correção | Teste E2E 2026-10-22 | aberto |
| H-03 | agent-adversarial deve tratar qualquer exclusão de cobertura (`# pragma: no cover`, `omit`) como **bloqueante**; agent-glue-job proibido de usar `pragma: no cover` | correção | Teste E2E 2026-10-22 | aberto |
| H-04 | Horários em `progresso.md` são estimados pelos agents. Fazer os agents obterem data e hora com `date` (vai gerar pedido de permissão na primeira vez) | correção | Teste E2E 2026-10-22 | aberto |
| H-05 | `/encerrar-sessao` deve limpar `entrega_ativa` em `sessao.json` quando a entrega for concluída | correção | Teste E2E 2026-10-22 | aberto |
| H-06 | Bootstrap do `/iniciar-sessao` deve criar um `.gitignore` padrão (`.coverage`, `__pycache__/`, `.terraform/`, `CLAUDE.local.md` etc.) | correção | Teste E2E 2026-10-22 | aberto |
| H-07 | `--enable-continuous-cloudwatch-log`: a skill-terraform manda incluir, mas o contrato não prevê. Proposta: manter e listar no template do contrato como argumento padrão do harness. **Decisão do usuário** | decisão | Teste E2E 2026-10-22 | aberto |
| H-08 | Marketplace remoto: publicar o repo em um remoto git e documentar a instalação para o time | evolução | Decisão do usuário (próxima etapa) | aberto |
