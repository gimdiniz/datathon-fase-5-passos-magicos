# Obtenção autorizada dos dados

## Natureza da base

A base do PEDE contém dados educacionais sensíveis, inclusive informações que podem identificar ou tornar identificáveis crianças e jovens quando combinadas. Mesmo campos pseudonimizados, como RA e nome anonimizado, exigem acesso controlado.

Por essa razão, a base não é distribuída, versionada ou baixada automaticamente por este projeto.

## Autorização

Solicite acesso diretamente à organização responsável. A autorização deve indicar a finalidade de uso, o período permitido, as pessoas autorizadas e os controles de armazenamento e descarte.

O repositório não publica URL da base e não oferece mecanismo para contornar autenticação ou permissões.

## Instalação local

Após receber uma cópia legítima, mantenha o nome exato:

```text
BASE DE DADOS PEDE 2024 - DATATHON.xlsx
```

Copie o arquivo manualmente para:

```text
data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx
```

O caminho é relativo à raiz do repositório. Não adapte notebooks para diretórios pessoais.

## Estrutura esperada

O arquivo deve conter as abas:

- `PEDE2022`;
- `PEDE2023`;
- `PEDE2024`.

O validador também confere as colunas essenciais usadas pelo fluxo analítico aprovado.

## Validação

Na raiz do repositório, com o ambiente virtual ativado:

```bash
python scripts/validar_base_local.py
```

Uma validação aprovada apresenta somente dimensões agregadas e o SHA-256 da versão local. O hash permite registrar qual versão foi usada sem publicar o conteúdo.

## Erros comuns

### Arquivo não encontrado

Confirme o nome completo, inclusive espaços e extensão, e verifique se o arquivo está dentro de `data/raw/`.

### Extensão diferente

Não renomeie artificialmente um arquivo CSV ou XLS para XLSX. Solicite ou exporte corretamente a versão XLSX autorizada.

### Arquivo ilegível ou corrompido

Confirme se a cópia abre em um leitor compatível, copie-a novamente da origem autorizada e reinstale as dependências com `pip install -r requirements.txt`.

### Abas ausentes

Confirme que recebeu a versão esperada. Não renomeie abas silenciosamente, pois isso pode mascarar incompatibilidade de versão.

### Colunas essenciais ausentes

Não crie colunas fictícias. Compare a versão recebida com o dicionário oficial e solicite esclarecimento à organização.

### Permissão negada

Feche aplicativos que estejam bloqueando o arquivo e verifique as permissões locais. Não altere controles de acesso da organização nem mova a base para armazenamento público.
