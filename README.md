# Datathon PósTech — Passos Mágicos

Projeto de análise de dados educacionais desenvolvido para o Datathon da PósTech. O repositório reúne entendimento da base, análise exploratória, perguntas complementares, documentação metodológica e uma modelagem preliminar de risco de defasagem.

## Dashboard executivo

O dashboard Streamlit apresenta os resultados em uma narrativa voltada à tomada de decisão responsável:

1. contexto e pergunta central;
2. diagnóstico educacional;
3. sinais encontrados na EDA;
4. perguntas extras;
5. modelo candidato preliminar;
6. análise exploratória de limiar;
7. recomendações, limitações e cuidados éticos.

A aplicação utiliza somente figuras e tabelas agregadas em `reports/`. Ela não carrega a pasta `data/`, não oferece busca individual, não gera previsões por estudante e não exibe RA, nome ou data de nascimento.

### Execução local

Com o ambiente virtual ativado, instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie a aplicação na raiz do repositório:

```bash
streamlit run app/streamlit_app.py
```

O Streamlit informará o endereço local, normalmente `http://localhost:8501`.

## Uso responsável

O Random Forest é apresentado como modelo candidato preliminar, não como modelo final. O limiar 0,40 é exploratório e não está aprovado para uso operacional. Qualquer evolução do projeto deve preservar supervisão humana e impedir usos para punição, exclusão, ranking ou diagnóstico.
