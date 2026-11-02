# Guia de instalação do harness-dados

Instale e teste o plugin **harness-dados** no Claude Code em poucos minutos. Para entender o porquê do harness, da arquitetura e do fluxo, leia o [README](../README.md).

## Pré-requisitos

Confira cada item no terminal:

- [ ] **Claude Code** atualizado: `claude --version`
- [ ] **git** (o Claude Code usa o git para baixar o marketplace): `git --version`
- [ ] **Python 3.11+** no PATH: `python --version`

Só para o [desafio](../README.md) (Glue Job na AWS):

- [ ] **Conta AWS** e **AWS CLI** configurado: `aws sts get-caller-identity`
- [ ] **Terraform** (opcional): `terraform version`

## Preciso baixar ou clonar o repositório?

> **Não.** O `marketplace add` clona o repositório sozinho em `~/.claude/plugins/marketplaces/` e o `install` copia o plugin para `~/.claude/plugins/cache/harness-dados-marketplace/harness-dados/<versão>/`.
>
> Clone o repositório só se quiser testar localmente (`claude --plugin-dir <caminho>`) ou contribuir.

## Passo 1: adicionar o marketplace

Dentro do Claude Code:

```
/plugin marketplace add WDS1995/harness-dados
```

Ou pelo terminal:

```bash
claude plugin marketplace add WDS1995/harness-dados
```

## Passo 2: instalar o plugin

Dentro do Claude Code:

```
/plugin install harness-dados@harness-dados-marketplace
```

Ou pelo terminal:

```bash
claude plugin install harness-dados@harness-dados-marketplace
```

## Passo 3: conferir

Dentro do Claude Code, abra o gerenciador:

```
/plugin
```

Pelo terminal:

```bash
claude plugin list
```

Deve aparecer `harness-dados@harness-dados-marketplace`, **Version 0.1.0**, **Status enabled**. Opcionalmente:

```bash
claude plugin details harness-dados
```

Deve mostrar **7 skills, 6 agents e 1 hook**. Se estiver com o Claude Code aberto, reinicie-o para carregar o plugin.

## Passo 4: teste rápido

1. Crie uma pasta nova e inicialize o git:

   ```bash
   mkdir meu-repo-de-dados && cd meu-repo-de-dados
   git init
   ```
2. Abra o Claude Code: `claude`
3. Inicie a sessão:

   ```
   /harness-dados:iniciar-sessao
   ```
4. Na primeira vez, o bootstrap cria (sem sobrescrever nada existente):

   ```
   CLAUDE.md
   .gitignore
   .claude/rules/
   tests/__init__.py
   pyproject.toml
   requirements-dev.txt
   docs/contexto/glossario.md
   .entregas/
   ```

   Depois o escriba faz o briefing e o orquestrador pergunta se você quer continuar uma entrega ou iniciar um novo pedido.
5. Instale as dependências de teste (em outro terminal, na mesma pasta):

   ```bash
   pip install -r requirements-dev.txt
   ```
6. Para terminar o teste:

   ```
   /harness-dados:encerrar-sessao
   ```

## Problemas comuns

| Sintoma                                                 | Solução                                                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `Filename too long` no `marketplace add` (Windows)  | `git config --global core.longpaths true` e repita o comando                            |
| Os comandos `/harness-dados:...` não aparecem        | Reinicie o Claude Code e confira com `claude plugin list` se o plugin está `enabled` |
| O hook não roda os testes / `pytest` não encontrado | Rode `pip install -r requirements-dev.txt` com o Python que está no PATH               |
| Plugin desatualizado                                    | Veja a seção abaixo e rode o update                                                     |

## Atualizar e desinstalar

Dentro do Claude Code:

```
/plugin marketplace update harness-dados-marketplace
```

Pelo terminal:

```bash
claude plugin marketplace update harness-dados-marketplace   # baixa a versão mais nova do repo
claude plugin update harness-dados                           # atualiza o plugin instalado
claude plugin uninstall harness-dados                        # remove o plugin
claude plugin marketplace remove harness-dados-marketplace   # remove o marketplace 
```

## Próximo passo

Faça o **Desafio** do [README](../README.md#-desafio): criar um Glue Job com o harness e executá-lo na AWS.
