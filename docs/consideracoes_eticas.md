# Considerações éticas e de privacidade

## Finalidade legítima

O modelo deve apoiar a identificação antecipada de alunos que possam se beneficiar de acompanhamento. A saída não deve ser interpretada como diagnóstico, mérito, capacidade individual ou destino educacional.

## Dados de crianças e adolescentes

O conjunto inclui informações educacionais, psicossociais e de trajetória de menores. Mesmo pseudonimizados, esses dados permanecem sensíveis e podem permitir reidentificação quando combinados.

Quase-identificadores relevantes incluem:

- RA persistente;
- data completa de nascimento;
- idade e gênero;
- turma, fase, escola e instituição;
- ano de ingresso;
- trajetória anual;
- identificadores de avaliadores.

## Minimização e exposição

Recomendações obrigatórias para dashboard, relatório e apresentação:

- não publicar bases linha a linha;
- não exibir RA ou data completa de nascimento;
- não oferecer busca individual em aplicação pública;
- não divulgar grupos muito pequenos;
- agregar resultados por período ou grupo suficientemente amplo;
- não incluir exemplos que permitam reconhecer um aluno;
- armazenar segredos e credenciais fora do repositório;
- evitar logs contendo registros individuais.

## Riscos de viés

Ausências de indicadores podem não ser aleatórias. Excluir alunos com dados incompletos pode favorecer perfis com acompanhamento mais regular. O desempenho deve ser avaliado por grupos, quando ética e estatisticamente possível, sem expor grupos pequenos.

Variáveis como gênero, escola, instituição e indicadores psicossociais exigem justificativa explícita. Mesmo quando aumentam uma métrica, podem reproduzir desigualdades ou criar estigmatização.

## Supervisão humana

Uma sinalização de risco deve gerar revisão humana e oferta de apoio. O profissional deve conhecer:

- probabilidade estimada e grau de incerteza;
- fatores que influenciaram a estimativa;
- limitações do modelo;
- possibilidade de erro;
- alternativas de intervenção não punitiva.

Nenhuma decisão relevante deve ser tomada apenas pelo score.

## Falsos positivos e falsos negativos

- Falso negativo: um aluno que precisa de apoio pode não ser sinalizado.
- Falso positivo: um aluno pode ser rotulado indevidamente, gerando estigma ou alocação inadequada.

O limiar deve equilibrar capacidade de atendimento, recall e risco de rotulação. O score não deve ser apresentado ao aluno como classificação definitiva.

## Uso inadequado proibido

Não utilizar o modelo para:

- excluir alunos do programa;
- ordenar mérito ou valor pessoal;
- restringir oportunidades;
- automatizar sanções;
- divulgar ranking individual;
- inferir diagnósticos clínicos;
- avaliar profissionais sem contexto;
- usar dados fora da finalidade informada.

## Transparência e monitoramento

Documentar versão, período de validade, população, métricas, limitações e responsável. Após implantação, monitorar mudança de distribuição, calibração, erros por grupo, volume de alertas e consequências das intervenções.
