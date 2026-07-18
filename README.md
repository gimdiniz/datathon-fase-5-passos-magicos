# Datathon PósTech — Passos Mágicos

Projeto de análise de dados educacionais desenvolvido para o Datathon da PósTech. O repositório reúne entendimento da base, análise exploratória, perguntas complementares, documentação metodológica e uma modelagem preliminar de risco de defasagem.

## Dashboard executivo

O dashboard apresenta somente figuras e tabelas agregadas de `reports/`. Ele não carrega dados de `data/`, não oferece busca individual e não gera previsões por estudante.

## Como reproduzir o projeto

### 1. Pré-requisitos

- Git;
- Python 3.11 ou 3.12 recomendado;
- autorização da organização responsável para acessar a base educacional;
- espaço local protegido para armazenar a cópia autorizada.

### 2. Clone do repositório

```bash
git clone https://github.com/gimdiniz/datathon-fase-5-passos-magicos.git
cd datathon-fase-5-passos-magicos
```

### 3. Ambiente virtual

No Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Dependências

```bash
pip install -r requirements.txt
```

### 5. Obtenção autorizada da base

A base contém dados educacionais sensíveis e não é distribuída pelo repositório. Solicite acesso à organização responsável, respeitando a finalidade autorizada e os controles de segurança aplicáveis.

Não existe download automático, URL pública ou mecanismo para contornar permissões.

### 6. Nome e caminho esperados

Copie manualmente o arquivo, sem renomeá-lo, para:

```text
data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx
```

As abas esperadas são `PEDE2022`, `PEDE2023` e `PEDE2024`. Consulte [docs/obtencao_dados.md](docs/obtencao_dados.md) para orientações detalhadas.

### 7. Validação local

```bash
python scripts/validar_base_local.py
```

O validador confirma estrutura e legibilidade, apresenta somente dimensões agregadas e calcula o SHA-256 da cópia local. Ele não imprime linhas, não modifica o arquivo e não baixa dados.

### 8. Ordem dos notebooks

Execute os notebooks a partir da raiz do repositório, nesta ordem:

1. `notebooks/01_visao_geral_base.ipynb` — validação analítica, harmonização e geração local da base processada;
2. `notebooks/02_EDA.ipynb` — análise exploratória e artefatos agregados;
3. `notebooks/03_preparacao_modelagem.ipynb` — preparação e classificação das features;
4. `notebooks/04_modelagem_risco_defasagem.ipynb` — modelagem temporal e métricas.

O primeiro notebook gera localmente `data/processed/passos_magicos_clean_eda.csv`. Esse arquivo contém registros linha a linha, permanece ignorado pelo Git e não deve ser compartilhado ou versionado.

### 9. Dashboard

Depois de gerar os artefatos agregados:

```bash
streamlit run app/streamlit_app.py
```

### 10. Artefatos

- `reports/figures/`: gráficos agregados usados no dashboard;
- `reports/tables/`: tabelas agregadas e métricas;
- `data/processed/`: derivados locais sensíveis, nunca versionados;
- `docs/`: metodologia, privacidade, obtenção e decisões técnicas.

### 11. Limitações de reprodução

A reprodução completa depende da obtenção legítima e autorizada da mesma versão da base. Diferenças de versão, correções posteriores ou mudanças de esquema podem alterar o hash, dimensões e resultados. O projeto não inclui dicionário oficial completo nem substitui validação com a organização.

### 12. Política de privacidade

- não versionar dados crus ou processados linha a linha;
- não publicar URL restrita ou automatizar obtenção;
- não expor RA, nomes, nascimento, avaliadores, escolas ou trajetórias identificáveis;
- manter outputs públicos somente em nível agregado;
- limitar uso à finalidade autorizada;
- preservar supervisão humana e proibir decisões punitivas, exclusão, ranking ou diagnóstico individual.

Leia também [docs/reprodutibilidade.md](docs/reprodutibilidade.md) e [docs/consideracoes_eticas.md](docs/consideracoes_eticas.md).

## Uso responsável

O Random Forest é apresentado como modelo candidato preliminar, não como modelo final. O limiar 0,40 é exploratório e não está aprovado para uso operacional. Qualquer evolução deve manter revisão humana, explicabilidade e avaliação de riscos.
