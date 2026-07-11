# Registro de decisões de limpeza

## Estado inicial da auditoria

Data da auditoria: 11/07/2026.

Nenhuma base existente foi alterada. Este registro separa achados, decisões já observadas e propostas ainda dependentes de aprovação.

## Fluxos identificados

### Notebook histórico

`notebooks/01_visao_geral_base.ipynb` carrega 2022–2024, padroniza colunas, seleciona uma interseção de atributos, concatena anos e declara a exportação de `passos_magicos_clean_eda.csv`.

### Base processada local

`data/processed/base_2024_clean.csv` contém somente 2024 e possui padronização distinta, incluindo nomes em `snake_case` e flags de faixa. O código-fonte gerador não estava disponível.

## Decisões observadas que exigem revisão

| Decisão observada | Risco | Recomendação |
|---|---|---|
| Excluir linhas sem todos os indicadores mandatórios | Viés de seleção e perda de alunos vulneráveis | Quantificar perdas por ano, fase e perfil antes de decidir. |
| Interpolar notas após concatenação | Valores podem vir de outro aluno/ano | Não repetir; validar ausência ou imputar somente com regra agrupada e defensável. |
| Preencher escola aleatoriamente | Inventa informação e não é reproduzível | Manter ausente ou criar categoria “Não informado”. |
| Remover qualquer coluna com algum nulo | Perda excessiva e confusão entre ausência estrutural e erro | Definir regra por coluna e por ano. |
| Preservar apenas IPP entre colunas nulas | Critério assimétrico | Documentar disponibilidade estrutural de cada indicador. |
| Converter `INCLUIR` em nulo no INDE | Pode eliminar código operacional relevante | Preservar campo bruto ou mapear com regra oficial. |
| Tratar valores acima de 10 como inválidos | IAA 10,002 pode ser arredondamento | Confirmar fórmula; não truncar silenciosamente. |

## Achados quantitativos da base de 2024

- original e processada possuem 1.156 registros;
- não há perda de linhas;
- não há duplicidade integral ou por RA;
- 38 valores não numéricos `INCLUIR` em INDE tornam-se nulos;
- 122 valores de IAA são 10,002;
- `Agata` requer padronização de acento;
- `INCLUIR` na Pedra requer definição de negócio;
- colunas integralmente nulas devem ser mantidas na fonte e excluídas apenas da camada analítica, com registro;
- as duas colunas de status são constantes e aparentemente duplicadas.

## Política proposta para a próxima base derivada

1. Nunca sobrescrever a base atual.
2. Gerar uma nova versão com nome e data ou versão explícita.
3. Preservar colunas brutas relevantes junto às versões normalizadas.
4. Não imputar categorias aleatoriamente.
5. Não imputar ausência estrutural de indicadores.
6. Registrar contagens antes e depois de cada filtro.
7. Criar testes de faixa sem corrigir automaticamente.
8. Confirmar regras de negócio antes de mapear `INCLUIR`, IAN ou Defasagem.
9. Separar identificadores da matriz de modelagem.
10. Garantir que todas as features antecedam temporalmente o target.

## Pendências de decisão

- Qual é a definição oficial e o sinal de Defasagem?
- `INCLUIR` significa registro pendente, elegibilidade ou erro?
- IAA 10,002 deve ser arredondado para 10?
- Qual é o evento exato que o modelo deve antecipar?
- Em que momento de cada ano cada indicador é medido?
- Quais variáveis podem aparecer no dashboard público?
