# Reprodutibilidade controlada

## Ambiente recomendado

Recomenda-se Python 3.11 ou 3.12 em ambiente virtual isolado. O arquivo `requirements.txt` fixa as principais dependências, incluindo `pandas`, `openpyxl`, `scikit-learn`, `matplotlib`, `seaborn`, Jupyter e Streamlit.

## Instalação

```bash
git clone https://github.com/gimdiniz/datathon-fase-5-passos-magicos.git
cd datathon-fase-5-passos-magicos
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

No Linux ou macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Estrutura relevante

```text
app/                  dashboard Streamlit
data/raw/             base autorizada local, ignorada pelo Git
data/processed/       derivados locais linha a linha, ignorados pelo Git
docs/                 documentação e decisões
notebooks/            fluxo analítico numerado
reports/figures/      gráficos agregados
reports/tables/       tabelas e métricas agregadas
scripts/              validação local
src/                  carregamento, features e modelagem
```

## Obtenção manual

Obtenha autorização da organização e siga [obtencao_dados.md](obtencao_dados.md). A reprodução completa requer o arquivo:

```text
data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx
```

Não há download automático ou fallback remoto.

## Validação

```bash
python scripts/validar_base_local.py
```

O comando retorna código diferente de zero quando o arquivo está ausente, ilegível, incompleto ou incompatível com o esquema essencial.

## Ordem de execução

Inicie o Jupyter a partir da raiz e execute:

1. `notebooks/01_visao_geral_base.ipynb`;
2. `notebooks/02_EDA.ipynb`;
3. `notebooks/03_preparacao_modelagem.ipynb`;
4. `notebooks/04_modelagem_risco_defasagem.ipynb`.

O notebook 01 produz o CSV processado local consumido pelos notebooks seguintes. O módulo `src/carregamento_dados.py` centraliza tanto a leitura das abas cruas quanto a leitura desse derivado, sempre a partir de caminhos internos do projeto.

## Artefatos

O notebook 02 gera gráficos e tabelas exploratórias agregadas. O notebook 04 gera métricas, análises de limiar e figuras de avaliação. Os artefatos públicos ficam em `reports/`; derivados linha a linha permanecem somente em `data/processed/`.

## Streamlit

```bash
streamlit run app/streamlit_app.py
```

O dashboard lê apenas artefatos agregados. Ele não precisa da base crua durante a visualização.

## Decisões de privacidade

- obtenção exclusivamente manual e autorizada;
- ausência de URLs de dados e de código de download;
- exclusão de `data/raw/` e `data/processed/` do versionamento;
- outputs de notebook limitados a estrutura, qualidade e estatísticas agregadas;
- nenhum registro individual no dashboard;
- SHA-256 calculado localmente, sem cadastro central da base;
- ausência de transformação durante o carregamento central.

## Limitações

- não é possível reproduzir a análise sem acesso legítimo à base;
- versões diferentes podem produzir resultados diferentes;
- o esquema é validado contra as colunas essenciais conhecidas, mas não substitui dicionário oficial;
- resultados não constituem avaliação causal nem autorização de uso operacional;
- o histórico Git ainda contém uma versão processada sensível e requer saneamento separado.

## Por que o download não é automatizado

Automatizar o download exigiria publicar ou embutir uma localização restrita, credenciais ou um mecanismo de autenticação fora do controle da organização. Isso aumentaria o risco de acesso indevido, redistribuição e uso fora da finalidade autorizada. A etapa manual preserva a decisão de acesso da organização e torna explícita a responsabilidade de cada usuário.
