# ADR-0004: Bucket de dados recebido por --S3_BUCKET

- **Data:** 2026-10-22
- **Status:** aceita
- **Entrega:** ENT-0001

## Contexto

O job lê e grava no bucket de dados. O nome real do bucket é um identificador de conta e não pode aparecer no código, nos testes nem na documentação do repo. O harness proíbe caminhos e buckets fixos no código (`.claude/rules/glue-job.md`).

## Decisão

O bucket é recebido pelo parâmetro `--S3_BUCKET`, lido com `getResolvedOptions(argv, ["JOB_NAME", "S3_BUCKET"])`. Os paths de entrada e saída são montados a partir dele. Os testes usam valores de teste (`bucket-teste`, `outro-bucket-teste`).

## Alternativas consideradas

- **Bucket fixo no código:** descartada. Exporia o identificador real e impediria o reuso do job em outra conta.
- **Variável de ambiente ou arquivo de configuração:** não foi avaliada nos registros da entrega. Fica a critério de revisão futura.

## Consequências

- Quem executa o job precisa informar `--S3_BUCKET` no console. Sem ele, `getResolvedOptions` falha.
- A ausência do parâmetro é um erro de configuração, e não uma falha silenciosa.
- O valor real fica fora do repo.
