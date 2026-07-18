# Documentação dos dados

## Objetivo

Este documento registra a estrutura esperada das bases do Datathon Passos Mágicos e as condições mínimas para seu uso analítico. Ele não substitui o dicionário oficial da instituição. A presença de arquivos locais varia por usuário e depende de autorização.

## Origem e arquivos locais

A fonte local auditada é `data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx`, com três planilhas:

| Planilha | Linhas | Colunas | Período |
|---|---:|---:|---:|
| PEDE2022 | 860 | 42 | 2022 |
| PEDE2023 | 1.014 | 48 | 2023 |
| PEDE2024 | 1.156 | 50 | 2024 |

Arquivos em `data/processed/` são derivados locais sensíveis. Eles não são distribuídos nem versionados. O notebook `01_visao_geral_base.ipynb` gera localmente `passos_magicos_clean_eda.csv` para consumo das etapas seguintes.

Consulte `docs/obtencao_dados.md` e `docs/reprodutibilidade.md` antes de executar o fluxo.

## Unidade de observação

Cada linha parece representar um aluno em um ano de referência. O campo RA funciona como identificador persistente e permite análises longitudinais. Essa interpretação deve ser confirmada no dicionário oficial antes da modelagem.

## Indicadores principais

As bases apresentam os indicadores IAN, IDA, IEG, IAA, IPS, IPV e INDE. O IPP aparece a partir de 2023. As definições usadas nos notebooks devem ser validadas com a documentação oficial.

| Indicador | Interpretação preliminar | Atenção metodológica |
|---|---|---|
| IAN | Adequação de nível/defasagem | Pode estar diretamente relacionado ao target. |
| IDA | Desempenho acadêmico | Verificar momento de medição e composição. |
| IEG | Engajamento | Verificar disponibilidade antes do desfecho. |
| IAA | Autoavaliação | Indicador psicossocial sensível. |
| IPS | Indicador psicossocial | Uso requer cuidado ético e análise de viés. |
| IPP | Indicador psicopedagógico | Ausente em 2022; não imputar retroativamente sem fundamento. |
| IPV | Ponto de virada | Confirmar se é avaliação ou desfecho. |
| INDE | Índice composto | Alto risco de leakage se seus componentes ou derivados forem target. |

## Perfil da base processada local

Na auditoria de `base_2024_clean.csv`:

- 1.156 linhas e 58 colunas;
- nenhuma duplicidade integral;
- 1.156 RAs distintos;
- 102 nulos em INDE, IAA, IPS, IPP e IPV;
- 101 nulos em IDA;
- 682 nulos em Inglês;
- 38 ocorrências textuais `INCLUIR` no INDE original foram convertidas em nulo;
- 122 registros possuem IAA igual a 10,002;
- `pedra` contém `Agata` e `INCLUIR`;
- há colunas totalmente nulas e duas colunas constantes de situação do aluno.

Esses valores são achados de qualidade, não autorização para correção automática.

## Identificação e dados sensíveis

Mesmo com nomes pseudonimizados, RA, data de nascimento, idade, gênero, turma, escola, instituição, fase e trajetória anual formam um conjunto de quase-identificadores. Indicadores psicossociais e educacionais de menores exigem proteção reforçada.

As bases linha a linha não devem ser publicadas. Produtos públicos devem utilizar agregação, supressão de grupos pequenos e ausência de busca individual.

## Limitações conhecidas

- O código-fonte que gerou `base_2024_clean.csv` não está disponível no estado auditado.
- A base histórica consolidada usada pela EDA não está disponível localmente.
- As colunas mudam entre os anos.
- Há ausências estruturais, como IPP em 2022.
- O significado e o sinal de `Defasagem` ainda precisam de validação oficial.
- A data de disponibilidade de cada indicador precisa ser registrada antes da modelagem.

## Rastreabilidade mínima recomendada

Para cada base derivada, registrar:

1. arquivo e planilha de origem;
2. data da geração;
3. versão do código;
4. contagem de linhas antes e depois;
5. colunas removidas, criadas e renomeadas;
6. regras de conversão, exclusão e imputação;
7. testes de qualidade executados;
8. responsável pela decisão.
