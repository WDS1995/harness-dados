# ADR-0002: Uso exclusivo de spark.sql com catálogo criado em runtime

- **Data:** 2026-10-22
- **Status:** aceita
- **Entrega:** ENT-0001

## Contexto

O job lê um CSV do S3, transforma os dados e grava uma tabela no Glue Data Catalog. Ele também precisa criar o database e a tabela se não existirem, sem uma etapa de provisionamento separada. Terraform ficou fora de escopo nesta entrega (contrato §2).

## Decisão

Toda leitura, transformação, escrita e DDL usam `spark.sql(...)`:

- leitura por `CREATE OR REPLACE TEMPORARY VIEW ... USING csv` (R7);
- database e tabela por `CREATE DATABASE IF NOT EXISTS` e `CREATE TABLE IF NOT EXISTS ... USING PARQUET LOCATION` (R8);
- escrita por `INSERT OVERWRITE TABLE ... SELECT` (R9).

A API DataFrame (`.read`, `.write`, `createDataFrame` e métodos de DataFrame) não é usada. Os testes verificam o SQL enviado ao `spark.sql`.

## Alternativas consideradas

- **API DataFrame com `saveAsTable`:** descartada pelo requisito do contrato (§1 e §5: "exclusivamente com Spark SQL"; a API DataFrame não é usada).
- **Tabela criada previamente por Terraform:** fora de escopo; fica para a ENT-0004.

## Consequências

- O catálogo é criado na primeira execução e atualizado pelas seguintes.
- Os testes conseguem provar a regra, mas só pelo texto do SQL. Um SQL correto no texto ainda pode falhar em runtime por permissão (ver risco do contrato §9).
- Uma chamada de DataFrame sobre o retorno de `spark.sql` não é detectada pela regex atual. O apontamento 5 da ENT-0003 trata disso.
