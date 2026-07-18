# Decisões técnicas de reprodutibilidade e privacidade

Data: 18/07/2026.

## Problema identificado

O carregamento estava repetido nos quatro notebooks e dependia do diretório corrente. O notebook 02 possuía fallback para baixar do GitHub uma base processada linha a linha. Notebooks versionados também continham outputs com RA, nome anonimizado, nascimento, avaliadores, escola, instituição e amostras de registros.

Embora os dados atuais estejam ignorados, uma base processada sensível foi adicionada a commits anteriores e continua alcançável no histórico Git, inclusive em `main` e referências remotas.

## Solução adotada

- carregamento centralizado em `src/carregamento_dados.py`;
- localização determinística da raiz a partir do módulo;
- ausência total de download ou fallback remoto;
- validador local somente leitura;
- esquema mínimo explícito por aba;
- mensagens orientativas quando a base está ausente;
- reforço do `.gitignore` para toda a camada processada;
- sanitização dos outputs e substituição por resumos estruturais ou agregados;
- documentação do acesso manual, execução e limitações.

Durante a execução limpa, foi identificado que o notebook 01 usava `Ano_Referencia` antes de defini-la; outputs antigos mascaravam a dependência de estado residual do kernel. A coluna passou a ser atribuída explicitamente a 2022, 2023 e 2024 antes da concatenação. Essa é uma correção de ordem e explicitação da lógica já refletida na base processada e nos resultados aprovados, não uma alteração da regra analítica.

## Arquivos afetados

Foram criados documentos de obtenção e reprodutibilidade, um README para `data/`, o validador, o carregador e este registro. Foram atualizados o README principal, `.gitignore`, `requirements.txt`, a documentação de dados e os quatro notebooks que carregavam bases diretamente.

## Razões para não publicar a base

Os registros descrevem trajetórias educacionais e dimensões psicossociais de crianças e jovens. RA, nascimento, instituição, escola, fase, turma e indicadores formam identificadores ou quase-identificadores. Pseudonimização não elimina o risco de reidentificação nem autoriza redistribuição.

## Razões para não automatizar o download

Automação poderia expor localização restrita, credenciais ou uma forma de contornar a decisão de acesso da organização. O projeto exige autorização e cópia manual para manter a governança na origem e tornar a finalidade de uso explícita.

## Riscos mitigados

- novos commits acidentais de dados crus ou derivados;
- download não autorizado;
- dependência de caminho pessoal;
- outputs públicos com registros individuais;
- divergência entre carregamentos duplicados;
- execução silenciosa com arquivo ou esquema incorreto.

## Limitações restantes e estado de sanitização

Uma base processada sensível permanece acessível no histórico Git. Portanto, o repositório **não pode ser declarado integralmente sanitizado** nesta etapa. O `.gitignore`, a remoção do arquivo no estado atual e a sanitização dos notebooks não eliminam objetos já publicados.

A reescrita de histórico está deliberadamente fora do escopo desta tarefa. Ela deverá ocorrer separadamente, mediante autorização, coordenação dos colaboradores, force-push controlado e orientação para substituição de clones e caches antigos.

Também permanecem as limitações de versão da base, ausência de um dicionário oficial completo no repositório e impossibilidade de reprodução por pessoas sem autorização legítima.

## Testes executados

- compilação de `src/`, `scripts/` e `app/` concluída sem erros;
- validação positiva da base autorizada, com as três abas e dimensões agregadas esperadas;
- testes negativos para arquivo ausente e abas ausentes, ambos com código de saída 1;
- teste de XLSX corrompido com código de saída 1 e mensagem orientativa, sem traceback;
- carregamento central das abas cruas e do derivado local concluído sem impressão de linhas;
- execução sequencial dos quatro notebooks em cópia temporária isolada concluída com sucesso;
- todos os CSVs exploratórios e a análise de limiar reproduzidos exatamente;
- CSVs de métricas com mesmos esquemas, rótulos e valores, com diferença máxima de `9,16e-16`, atribuível à representação de ponto flutuante;
- inspeção estática sem fallback remoto, download, caminho absoluto ou leitura direta de dados nos notebooks;
- verificação dos outputs salvos e substituição das amostras por resumos estruturais ou agregados;
- checkpoints locais com cópias de dados removidos após a sanitização;
- smoke test do Streamlit concluído com resposta HTTP 200;
- verificação de que bases cruas e processadas locais continuam ignoradas e não rastreadas pelo Git.

## Decisão sobre versionamento

Nenhum commit é criado automaticamente. Dados em `data/raw/` e `data/processed/` permanecem somente no ambiente autorizado do usuário.
