# Metodologia analítica e preditiva

## Princípios

O projeto deve produzir uma ferramenta de priorização de apoio educacional, e não um mecanismo automático de punição, exclusão ou diagnóstico. As decisões metodológicas devem privilegiar reprodutibilidade, explicabilidade, avaliação temporal e supervisão humana.

## Separação das etapas

O fluxo recomendado é:

1. entendimento da fonte;
2. limpeza e padronização;
3. validação independente da base processada;
4. análise exploratória;
5. definição temporal do problema;
6. engenharia de atributos;
7. modelagem e calibração;
8. interpretação, análise de erros e avaliação por subgrupos;
9. comunicação e monitoramento.

Os notebooks existentes devem ser preservados. Novos notebooks devem separar validação, preparação e modelagem.

## Problema preditivo

O target definitivo ainda não está aprovado. Alternativas a investigar:

- estar em defasagem no ano seguinte;
- agravar a defasagem entre dois anos;
- permanecer em defasagem;
- transitar de “em fase” para “moderada” ou “severa”.

Antes da escolha, é obrigatório confirmar:

- significado e sinal de `Defasagem`;
- regra de cálculo do IAN;
- relação entre IAN, Fase Ideal e Defasagem;
- disponibilidade histórica por RA;
- momento em que cada indicador se torna conhecido.

## Estratégia temporal

Sempre que a cobertura permitir:

- usar atributos medidos em 2022 para prever um desfecho em 2023;
- usar atributos medidos em 2023 para prever um desfecho em 2024;
- reservar a janela mais recente para avaliação final;
- impedir que o mesmo desfecho ou informação futura entre nas features.

Divisão aleatória de linhas não é recomendada. O mesmo aluno não deve aparecer simultaneamente em treino e teste de uma mesma janela de avaliação.

## Baselines e modelos

Priorizar modelos tabulares simples e defensáveis:

- regra de referência baseada na prevalência;
- regressão logística regularizada;
- árvore de decisão com controle de complexidade;
- Random Forest ou gradient boosting somente após baselines e com explicabilidade adequada.

### Decisão metodológica sobre Deep Learning

Deep Learning foi considerado, mas não é a abordagem mais adequada para esta versão do projeto. A base reúne 2.845 registros longitudinais de 1.586 alunos, distribuídos entre 2022, 2023 e 2024. Esse desenho produz somente duas transições temporais e uma única janela efetiva de teste, volume insuficiente para treinar, ajustar e validar redes neurais com estabilidade. Nessas condições, a maior flexibilidade desses modelos ampliaria o risco de sobreajuste sem que fosse possível verificar de forma robusta sua generalização entre diferentes safras.

Os dados são predominantemente tabulares e contêm poucas variáveis preditoras. Não há imagens, textos, áudios ou sequências extensas, nem uma necessidade clara de aprender automaticamente representações complexas. Modelos tabulares regularizados e baseados em árvores aproveitam diretamente a estrutura informacional disponível, já apresentam sinal preditivo relevante e permitem comparar desempenho, erros e sensibilidade de maneira mais defensável diante da única janela temporal disponível.

A escolha também considera o contexto educacional. Explicações compreensíveis, auditoria, supervisão humana e análise dos falsos negativos e falsos positivos são requisitos centrais. Redes neurais aumentariam a dificuldade de explicação e auditoria, além do custo de ajuste, monitoramento e manutenção, sem evidência de benefício proporcional nesta base. A decisão, portanto, é técnica e contextual, não decorre de desconhecimento da abordagem nem de uma limitação meramente computacional.

Deep Learning poderá ser reconsiderado quando houver um volume substancialmente maior de alunos e ciclos, múltiplas janelas temporais independentes para validação e maior complexidade informacional — por exemplo, textos, imagens, áudios ou sequências longitudinais mais extensas. Qualquer reavaliação deverá demonstrar ganho consistente sobre os modelos tabulares, preservar explicabilidade suficiente para o uso educacional e manter revisão humana das sinalizações.

## Métricas

A avaliação deve incluir:

- recall da classe de risco;
- precisão e F1 da classe de risco;
- PR-AUC;
- matriz de confusão;
- calibração das probabilidades;
- desempenho por subgrupos relevantes;
- análise dos falsos negativos e falsos positivos.

Acurácia isolada não é suficiente. O limiar de decisão deve ser escolhido com base no custo operacional e educacional dos erros.

## Leakage

Se o target for defasagem futura, devem ser inicialmente bloqueados ou tratados como condicionais:

- Defasagem do mesmo período do target;
- IAN do mesmo período;
- Fase Ideal do mesmo período;
- INDE e Pedra quando calculados com informações contemporâneas ao desfecho;
- flags ou rótulos produzidos depois do evento;
- indicadores futuros armazenados na linha do ano atual.

Datas, RA e nomes podem ser usados exclusivamente para junção e separação, nunca como sinal preditivo.

## Validação das conclusões exploratórias

Correlação e regressão exploratória não comprovam causalidade. Expressões como “prova”, “impacto comprovado” e “preditor” devem ser usadas somente após desenho e validação compatíveis. Na EDA, preferir “associação observada”, “hipótese” ou “evidência descritiva”.

## Reprodutibilidade

Cada execução deve registrar:

- versões de dependências;
- parâmetros e semente quando houver aleatoriedade;
- janela temporal;
- colunas utilizadas e excluídas;
- prevalência do target;
- critérios de exclusão;
- métricas e intervalos de incerteza quando viável.
