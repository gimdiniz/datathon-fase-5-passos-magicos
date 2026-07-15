"""Dashboard executivo do Datathon Passos Mágicos.

A aplicação consome exclusivamente artefatos agregados e auditados em ``reports/``.
Ela não acessa bases em ``data/`` nem produz previsões individuais.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st


RAIZ = Path(__file__).resolve().parents[1]
PASTA_REPORTS = RAIZ / "reports"
CAMINHO_MANIFESTO = PASTA_REPORTS / "tables" / "manifesto_artefatos_eda.csv"

COLUNAS_PROIBIDAS = {
    "ra",
    "nome",
    "data_nascimento",
    "data de nascimento",
    "nascimento",
}

FIGURAS_MODELO = {
    "comparacao": "reports/figures/comparacao_modelos.png",
    "curva_pr": "reports/figures/curva_precision_recall_random_forest.png",
    "matriz_050": "reports/figures/matriz_confusao_random_forest.png",
    "matriz_040": "reports/figures/matriz_confusao_random_forest_limiar_alternativo.png",
}

TABELAS_MODELO = {
    "metricas": "reports/tables/model_metrics.csv",
    "limiares": "reports/tables/threshold_analysis_random_forest.csv",
    "sensibilidade": "reports/tables/model_metrics_sem_fase_idade.csv",
}


st.set_page_config(
    page_title="Passos Mágicos | Inteligência educacional",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def aplicar_estilo() -> None:
    st.markdown(
        """
        <style>
        :root {
            --azul-profundo: #123B5D;
            --azul: #176B87;
            --turquesa: #2A9D8F;
            --amarelo: #F2C14E;
            --coral: #E76F51;
            --neutro: #F4F7F8;
            --texto: #18323F;
            --texto-suave: #526A76;
            --borda: #DDE7EB;
        }

        .stApp { background: #F8FAFB; color: var(--texto); }
        .block-container { max-width: 1220px; padding-top: 2rem; padding-bottom: 4rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0E304A 0%, #164F68 100%); }
        [data-testid="stSidebar"] * { color: #F7FBFC; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.18); }
        [data-testid="stSidebar"] [data-baseweb="radio"] label {
            padding: .35rem .2rem; border-radius: .5rem;
        }
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid var(--borda);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 7px 22px rgba(18, 59, 93, .06);
        }
        [data-testid="stMetricLabel"] { color: var(--texto-suave); }
        [data-testid="stMetricValue"] { color: var(--azul-profundo); }
        h1, h2, h3 { color: var(--azul-profundo); letter-spacing: -.02em; }
        h1 { font-size: 2.45rem !important; }
        h2 { margin-top: 1.1rem !important; }
        p, li { line-height: 1.65; }

        .hero {
            background: linear-gradient(120deg, #103A59 0%, #176B87 58%, #2A9D8F 100%);
            padding: 2.3rem 2.5rem;
            border-radius: 24px;
            color: white;
            box-shadow: 0 16px 38px rgba(18, 59, 93, .18);
            margin-bottom: 1.6rem;
        }
        .hero h1 { color: white; margin: .25rem 0 .65rem; font-size: 2.55rem !important; }
        .hero p { color: #E7F4F5; max-width: 850px; font-size: 1.06rem; margin-bottom: 0; }
        .eyebrow {
            font-size: .77rem; font-weight: 750; letter-spacing: .12em;
            text-transform: uppercase; color: #BFE9E2;
        }
        .section-intro { color: var(--texto-suave); font-size: 1.03rem; max-width: 920px; margin-bottom: 1.1rem; }
        .question-box {
            background: #FFFFFF; border: 1px solid var(--borda); border-left: 5px solid var(--turquesa);
            border-radius: 14px; padding: 1.2rem 1.35rem; margin: 1rem 0 1.6rem;
            box-shadow: 0 6px 18px rgba(18, 59, 93, .05);
        }
        .question-box small { color: var(--azul); font-weight: 750; text-transform: uppercase; letter-spacing: .08em; }
        .question-box strong { display: block; color: var(--azul-profundo); font-size: 1.22rem; margin-top: .3rem; }
        .context-card {
            height: 100%; background: #FFFFFF; border: 1px solid var(--borda); border-radius: 14px;
            padding: 1rem 1.15rem; margin: .25rem 0 1.1rem;
        }
        .context-card.observacao { border-top: 4px solid var(--azul); }
        .context-card.importancia { border-top: 4px solid var(--amarelo); }
        .card-title {
            color: var(--azul-profundo);
            margin: .35rem 0;
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.25;
        }
        .context-card .card-title { margin: 0 0 .35rem; font-size: .98rem; }
        .context-card p { color: var(--texto-suave); margin: 0; font-size: .94rem; }
        .insight {
            background: #EAF6F4; border: 1px solid #BFE3DD; border-radius: 14px;
            padding: 1rem 1.2rem; color: #164F50; margin: .6rem 0 1.2rem;
        }
        .alerta {
            background: #FFF6E3; border: 1px solid #F3D58B; border-radius: 14px;
            padding: 1rem 1.2rem; color: #6A5015; margin: .6rem 0 1.2rem;
        }
        .etica {
            background: #FDEDEA; border: 1px solid #F2C1B5; border-radius: 14px;
            padding: 1rem 1.2rem; color: #733628; margin: .6rem 0 1.2rem;
        }
        .action-card {
            min-height: 180px; background: white; border: 1px solid var(--borda); border-radius: 16px;
            padding: 1.2rem; box-shadow: 0 7px 20px rgba(18, 59, 93, .05); margin-bottom: 1rem;
        }
        .action-card .numero { color: var(--turquesa); font-weight: 800; font-size: .78rem; letter-spacing: .1em; }
        .action-card p { color: var(--texto-suave); font-size: .93rem; margin: 0; }
        .rodape { color: #6B7E87; font-size: .82rem; text-align: center; margin-top: 3rem; }
        div[data-testid="stImage"] img { border-radius: 14px; border: 1px solid var(--borda); }
        div[data-testid="stDataFrame"] { border: 1px solid var(--borda); border-radius: 12px; overflow: hidden; }
        .stTabs [data-baseweb="tab-list"] { gap: .35rem; }
        .stTabs [data-baseweb="tab"] { background: #EEF4F6; border-radius: 10px 10px 0 0; padding: .55rem .9rem; }
        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
        @media (max-width: 800px) {
            .hero { padding: 1.5rem; }
            .hero h1 { font-size: 2rem !important; }
            .block-container { padding-top: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def carregar_manifesto() -> pd.DataFrame:
    if not CAMINHO_MANIFESTO.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(CAMINHO_MANIFESTO)
    except Exception:
        return pd.DataFrame()


def caminhos_auditados(manifesto: pd.DataFrame) -> set[str]:
    if manifesto.empty or "arquivo_gerado" not in manifesto.columns:
        return set()
    return {
        str(valor).strip().replace("\\", "/")
        for valor in manifesto["arquivo_gerado"].dropna()
        if str(valor).strip()
    }


MANIFESTO = carregar_manifesto()
CAMINHOS_AUDITADOS = caminhos_auditados(MANIFESTO)


def resolver_caminho(caminho_relativo: str, exigir_auditoria: bool = False) -> Path | None:
    caminho_normalizado = caminho_relativo.replace("\\", "/")
    if exigir_auditoria and caminho_normalizado not in CAMINHOS_AUDITADOS:
        return None

    candidato = (RAIZ / caminho_normalizado).resolve()
    try:
        candidato.relative_to(PASTA_REPORTS.resolve())
    except ValueError:
        return None
    return candidato if candidato.is_file() else None


@st.cache_data(show_spinner=False)
def ler_csv_seguro(caminho: str) -> pd.DataFrame | None:
    try:
        tabela = pd.read_csv(caminho)
    except Exception:
        return None

    cabecalhos = {str(coluna).strip().lower() for coluna in tabela.columns}
    if cabecalhos & COLUNAS_PROIBIDAS:
        return None
    return tabela


def carregar_tabela(caminho_relativo: str, auditada: bool = True) -> pd.DataFrame | None:
    caminho = resolver_caminho(caminho_relativo, exigir_auditoria=auditada)
    if caminho is None:
        st.info(f"Tabela indisponível no momento: `{Path(caminho_relativo).name}`.")
        return None
    tabela = ler_csv_seguro(str(caminho))
    if tabela is None:
        st.info(f"Não foi possível carregar com segurança: `{caminho.name}`.")
    return tabela


def mostrar_figura(
    caminho_relativo: str,
    titulo: str,
    observacao: str,
    importancia: str,
    *,
    auditada: bool = True,
) -> None:
    st.subheader(titulo)
    caminho = resolver_caminho(caminho_relativo, exigir_auditoria=auditada)
    if caminho is None:
        st.info(f"Figura indisponível no momento: `{Path(caminho_relativo).name}`.")
    else:
        st.image(str(caminho), width="stretch")

    coluna_a, coluna_b = st.columns(2)
    with coluna_a:
        st.markdown(
            f'<div class="context-card observacao"><div class="card-title">O que observamos</div><p>{observacao}</p></div>',
            unsafe_allow_html=True,
        )
    with coluna_b:
        st.markdown(
            f'<div class="context-card importancia"><div class="card-title">Por que importa</div><p>{importancia}</p></div>',
            unsafe_allow_html=True,
        )


def mostrar_tabela_em_expansor(
    titulo: str,
    caminho_relativo: str,
    *,
    renomear: dict[str, str] | None = None,
    auditada: bool = True,
) -> None:
    with st.expander(titulo):
        tabela = carregar_tabela(caminho_relativo, auditada=auditada)
        if tabela is not None:
            if renomear:
                tabela = tabela.rename(columns=renomear)
            st.dataframe(tabela, hide_index=True, width="stretch")
            st.caption("Tabela agregada. Não contém identificadores nem registros individuais.")


def cabecalho_secao(sobretitulo: str, titulo: str, descricao: str) -> None:
    st.markdown(f'<div class="eyebrow" style="color:#2A7F7A">{sobretitulo}</div>', unsafe_allow_html=True)
    st.title(titulo)
    st.markdown(f'<div class="section-intro">{descricao}</div>', unsafe_allow_html=True)


def formatar_percentual(valor: float) -> str:
    return f"{valor * 100:.1f}%".replace(".", ",")


def formatar_decimal(valor: float, casas: int = 3) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def pagina_visao_geral() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Datathon PósTech • Case Passos Mágicos</div>
            <h1>Dados para antecipar apoio educacional</h1>
            <p>Uma leitura executiva da trajetória dos estudantes e dos sinais associados à defasagem, com foco em prevenção, supervisão pedagógica e impacto social responsável.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="question-box">
            <small>Pergunta central</small>
            <strong>Quais sinais indicam que um aluno pode entrar ou permanecer em risco de defasagem?</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    colunas = st.columns(4)
    colunas[0].metric("Período analisado", "3 ciclos", "2022–2024", delta_color="off")
    colunas[1].metric("Análises auditadas", "15")
    colunas[2].metric("Modelos comparados", "5")
    colunas[3].metric("Finalidade", "Prevenção")

    st.header("Da compreensão à ação responsável")
    st.markdown(
        """
        A Passos Mágicos atua para transformar a vida de crianças e jovens por meio da educação. Este dashboard organiza as evidências já produzidas no projeto em uma jornada decisória: primeiro entendemos o cenário educacional; depois reconhecemos sinais de atenção; por fim, avaliamos como um modelo preliminar pode apoiar — e nunca substituir — a equipe pedagógica.
        """
    )

    etapa_1, etapa_2, etapa_3 = st.columns(3)
    with etapa_1:
        st.markdown('<div class="action-card"><div class="numero">01 • CONTEXTO</div><div class="card-title">Entender trajetórias</div><p>Observar defasagem, desempenho, engajamento e dimensões psicossociais ao longo de três ciclos.</p></div>', unsafe_allow_html=True)
    with etapa_2:
        st.markdown('<div class="action-card"><div class="numero">02 • SINAIS</div><div class="card-title">Reconhecer pontos de atenção</div><p>Combinar evidências acadêmicas e psicossociais sem reduzir o estudante a uma única nota.</p></div>', unsafe_allow_html=True)
    with etapa_3:
        st.markdown('<div class="action-card"><div class="numero">03 • AÇÃO</div><div class="card-title">Apoiar decisões humanas</div><p>Usar o modelo como triagem complementar, com revisão profissional e oferta de apoio.</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="insight"><strong>Compromisso do produto:</strong> esta aplicação utiliza apenas figuras e tabelas agregadas de <code>reports/</code>. Nenhuma base individual é carregada.</div>', unsafe_allow_html=True)


def pagina_diagnostico() -> None:
    cabecalho_secao(
        "Capítulo 1 • Diagnóstico",
        "Como evoluiu o cenário educacional?",
        "A leitura começa pela defasagem e avança para desempenho e trajetória no programa. Os resultados são descritivos e não demonstram causalidade.",
    )

    st.markdown("### Indicadores em linguagem simples")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("**IAN**\n\nAdequação do estudante à fase esperada para sua idade.")
    c2.info("**IDA**\n\nDesempenho acadêmico observado nas avaliações.")
    c3.info("**IEG**\n\nParticipação e engajamento nas atividades propostas.")
    c4.info("**INDE**\n\nÍndice sintético que reúne dimensões da trajetória educacional.")
    st.caption("Fases representam etapas educacionais. Pedras — Quartzo, Ágata, Ametista e Topázio — são faixas derivadas do INDE e não constituem uma medida independente.")

    aba_ian, aba_desempenho, aba_ciclo = st.tabs(["Defasagem e IAN", "Desempenho por fase", "INDE e Pedras"])

    with aba_ian:
        mostrar_figura(
            "reports/figures/fig_eda_01_perfil_defasagem_ian.png",
            "O perfil de defasagem mudou ao longo dos ciclos",
            "A participação de estudantes classificados como “Em Fase” passou de 30,12% em 2022 para 49,34% em 2024, enquanto a defasagem severa diminuiu.",
            "A fotografia anual indica uma evolução descritiva favorável, mas deve ser acompanhada da trajetória dos mesmos estudantes para evitar conclusões causais apressadas.",
        )
        mostrar_tabela_em_expansor("Consultar distribuição agregada do IAN", "reports/tables/eda_ian_distribuicao.csv")

        mostrar_figura(
            "reports/figures/fig_eda_02_transicao_ian_longitudinal.png",
            "A trajetória longitudinal complementa a fotografia anual",
            "Entre 434 estudantes presentes nos três ciclos, 36,64% reduziram a defasagem e 6,91% aumentaram. A transição de Moderada para Em Fase concentrou 153 casos.",
            "A matriz ajuda a distinguir mudança de composição da base e mobilidade educacional. O grupo que permaneceu em defasagem moderada merece investigação e apoio, não rotulação.",
        )
        mostrar_tabela_em_expansor("Consultar resumo longitudinal", "reports/tables/eda_ian_evolucao_longitudinal.csv")
        mostrar_tabela_em_expansor("Consultar matriz de transição agregada", "reports/tables/eda_ian_matriz_transicao.csv")

    with aba_desempenho:
        mostrar_figura(
            "reports/figures/fig_eda_03_desempenho_ida_fase_ano.png",
            "O desempenho varia entre fases e ciclos",
            "A EDA identificou médias menores e maior dispersão nas fases intermediárias, com destaque para a FASE 3 e continuidade de atenção na FASE 4.",
            "A leitura por fase orienta onde reforçar acompanhamento pedagógico. Diferenças entre turmas e tamanhos amostrais precisam ser consideradas antes de qualquer decisão.",
        )

    with aba_ciclo:
        mostrar_figura(
            "reports/figures/fig_eda_04_inde_pedra_ano.png",
            "As Pedras organizam faixas do INDE",
            "As médias crescem de Quartzo a Topázio e mantêm relativa estabilidade entre os anos, como esperado pela própria regra de classificação das Pedras.",
            "O gráfico é útil para consistência e comunicação do ciclo, mas não deve ser interpretado como prova independente de impacto, pois Pedra é derivada do INDE.",
        )
        mostrar_tabela_em_expansor("Consultar INDE médio por Pedra e ano", "reports/tables/eda_inde_pedra_ano.csv")


def pagina_sinais_eda() -> None:
    cabecalho_secao(
        "Capítulo 2 • Sinais",
        "O risco educacional é multidimensional",
        "Engajamento, desempenho, autopercepção e dimensões psicossociais oferecem sinais complementares. Associação não significa causa nem autoriza diagnóstico individual.",
    )

    aba_engajamento, aba_autopercepcao, aba_psicossocial, aba_indices = st.tabs(
        ["Engajamento", "Autopercepção", "Dimensão psicossocial", "INDE e IPV"]
    )

    with aba_engajamento:
        mostrar_figura(
            "reports/figures/fig_eda_05_correlacao_engajamento_desempenho_ipv.png",
            "Engajamento, desempenho e ponto de virada caminham juntos",
            "A EDA encontrou correlações positivas moderadas entre IEG, IDA e IPV, próximas de 0,54 a 0,56 no recorte analisado.",
            "Quedas combinadas podem funcionar como sinal de atenção. As correlações não definem direção da relação nem comprovam que uma dimensão cause a outra.",
        )

    with aba_autopercepcao:
        mostrar_figura(
            "reports/figures/fig_eda_06_autoavaliacao_desempenho_engajamento.png",
            "A autoavaliação se aproxima mais do engajamento que das notas",
            "Os gaps observados sugerem maior coerência entre IAA e IEG. Em parte da distribuição, a autoavaliação aparece acima do desempenho acadêmico medido.",
            "A divergência pode orientar conversas pedagógicas sobre consciência de aprendizagem, sem transformar percepção ou nota em julgamento sobre capacidade.",
        )
        mostrar_figura(
            "reports/figures/fig_eda_07_gap_autoavaliacao_por_pedra.png",
            "A aderência da autopercepção varia ao longo das Pedras",
            "As médias do gap IAA–IDA se aproximam de zero nas etapas mais avançadas, com diferenças entre anos e dispersões relevantes.",
            "A evolução sugere uma hipótese de maior consciência acadêmica ao longo do ciclo, mas diferenças de coorte e metodologia impedem interpretação causal.",
        )

    with aba_psicossocial:
        mostrar_figura(
            "reports/figures/fig_eda_08_relacao_ian_ipp.png",
            "IAN e IPP oferecem leituras complementares",
            "A correlação linear entre defasagem e avaliação psicopedagógica foi baixa no recorte de 2023–2024, indicando pouca associação linear entre as medidas.",
            "Um estudante em fase pode ainda demandar apoio psicopedagógico, e vice-versa. Nenhum dos indicadores deve ser usado isoladamente como diagnóstico.",
        )
        mostrar_figura(
            "reports/figures/fig_eda_09_ips_anterior_variacoes_futuras.png",
            "IPS baixo antecede parte das quedas observadas",
            "As distribuições mostram ocorrências de queda posterior em engajamento e desempenho entre estudantes com IPS anterior mais baixo.",
            "O IPS pode compor uma rotina preventiva de acompanhamento conjunto. O padrão não estima evasão e não demonstra causalidade.",
        )

    with aba_indices:
        mostrar_figura(
            "reports/figures/fig_eda_10_composicao_inde.png",
            "IDA e IEG aparecem fortemente associados ao INDE",
            "IDA e IEG apresentaram as maiores correlações isoladas com o INDE; na regressão exploratória, IEG, IDA e IPP tiveram coeficientes próximos.",
            "Como o INDE é construído a partir desses indicadores, parte da associação é esperada. Coeficientes não equivalem a percentuais de impacto causal.",
        )
        mostrar_figura(
            "reports/figures/fig_eda_11_relacoes_ipv.png",
            "O IPV reúne dimensões acadêmicas e psicopedagógicas",
            "No modelo exploratório da EDA, o IPP apresentou o maior coeficiente condicionado às demais variáveis incluídas, seguido por IEG e IDA.",
            "A leitura reforça o caráter multidimensional do ponto de virada, mas ainda exige validação temporal antes de orientar qualquer intervenção.",
        )


def pagina_perguntas_extras() -> None:
    cabecalho_secao(
        "Capítulo 3 • Perguntas extras",
        "Onde estão os sinais acionáveis?",
        "Quatro investigações aprofundam a narrativa: permanência, perfis exploratórios, transições críticas e recuperação após queda psicossocial.",
    )

    aba_tempo, aba_personas, aba_gargalos, aba_resiliencia = st.tabs(
        ["Tempo no programa", "Personas", "Gargalos de fase", "Resiliência"]
    )

    with aba_tempo:
        mostrar_figura(
            "reports/figures/fig_perguntas_extra_01_tempo_programa.png",
            "Permanência mais longa não garante evolução linear",
            "Na amostra com histórico completo e ingresso consistente, o grupo Antigos teve maior inclinação média, mas as trajetórias individuais incluem estabilidade, oscilação e quedas.",
            "Tempo no programa deve ser analisado junto a fase, idade e composição das coortes. A trajetória é mais informativa que uma fotografia isolada.",
        )
        mostrar_tabela_em_expansor("Consultar resumo por tempo no programa", "reports/tables/eda_tempo_programa_resumo.csv")

    with aba_personas:
        mostrar_figura(
            "reports/figures/fig_perguntas_extra_02_personas_pca.png",
            "Dois perfis exploratórios resumem combinações recorrentes",
            "O melhor silhouette entre as alternativas testadas ocorreu com dois perfis. A projeção PCA simplifica a separação para fins exploratórios.",
            "Personas podem orientar trilhas de apoio, mas não são diagnósticos nem descrições completas dos estudantes. A segmentação precisa ser revisada a cada ciclo.",
        )
        mostrar_figura(
            "reports/figures/fig_perguntas_extra_02_personas_heatmap.png",
            "Os perfis combinam dimensões diferentes",
            "A assinatura média mostra diferenças simultâneas em desempenho, engajamento e dimensões psicossociais, não apenas uma nota geral.",
            "O heatmap ajuda a desenhar estratégias multidimensionais. Médias de grupo não devem ser convertidas em rótulos individuais permanentes.",
        )
        mostrar_tabela_em_expansor("Consultar avaliação do número de perfis", "reports/tables/eda_personas_avaliacao_k.csv")
        mostrar_tabela_em_expansor("Consultar distribuição agregada dos perfis", "reports/tables/eda_personas_distribuicao.csv")
        mostrar_tabela_em_expansor("Consultar médias dos perfis", "reports/tables/eda_personas_perfil_medio.csv")

    with aba_gargalos:
        mostrar_figura(
            "reports/figures/fig_perguntas_extra_03_gargalos_transicao.png",
            "A transição FASE 2 → FASE 3 concentra atenção",
            "Entre as transições com pelo menos 15 observações, FASE 2 → FASE 3 apresentou 50,97% de queda relevante no INDE, com n=155.",
            "O resultado orienta investigação e monitoramento antecipado de IDA e IEG. Não deve ser usado para punir turmas, estudantes ou profissionais.",
        )
        mostrar_tabela_em_expansor("Consultar transições agregadas", "reports/tables/eda_transicoes_fase_resumo.csv")

    with aba_resiliencia:
        mostrar_figura(
            "reports/figures/fig_perguntas_extra_04_resiliencia.png",
            "Parte dos estudantes recupera o INDE após queda no IPS",
            "Entre 265 estudantes com queda de IPS de pelo menos um ponto em 2022→2023, 52,08% recuperaram o patamar de INDE até 2024.",
            "Uma queda relevante no IPS pode disparar acolhimento e acompanhamento conjunto. Com três anos, só é possível observar recuperação em até um ciclo.",
        )
        mostrar_tabela_em_expansor("Consultar resumo de recuperação", "reports/tables/eda_resiliencia_ips_resumo.csv")


def pagina_modelo() -> None:
    cabecalho_secao(
        "Capítulo 4 • Apoio preditivo",
        "Um modelo preliminar para ampliar a prevenção",
        "O target provisório representa risco de defasagem no ano seguinte. O desenho respeita o tempo: treino em 2022→2023 e teste em 2023→2024.",
    )

    st.markdown('<div class="alerta"><strong>Status:</strong> estudo preliminar. O Random Forest é um modelo candidato para continuidade, não um modelo final ou aprovado para operação.</div>', unsafe_allow_html=True)

    metricas = carregar_tabela(TABELAS_MODELO["metricas"], auditada=False)
    rf = None
    logistica = None
    if metricas is not None and "modelo" in metricas.columns:
        rf_linhas = metricas[metricas["modelo"] == "RandomForestClassifier"]
        log_linhas = metricas[metricas["modelo"] == "LogisticRegression"]
        rf = rf_linhas.iloc[0] if not rf_linhas.empty else None
        logistica = log_linhas.iloc[0] if not log_linhas.empty else None

    if rf is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Recall de risco", formatar_percentual(float(rf["recall_risco"])))
        c2.metric("F1 de risco", formatar_percentual(float(rf["f1_risco"])))
        c3.metric("PR-AUC", formatar_decimal(float(rf["pr_auc"])))
        c4.metric("Brier score", formatar_decimal(float(rf["brier_score"])))

    st.markdown("### Por que acurácia não é a métrica principal?")
    st.write("A acurácia pode parecer alta mesmo quando o modelo deixa de reconhecer muitos estudantes em risco. Neste contexto, o recall mostra quanto do risco real foi encontrado; F1 equilibra recall e precisão; PR-AUC avalia a separação da classe de interesse; e Brier score verifica a qualidade das probabilidades.")

    mostrar_figura(
        FIGURAS_MODELO["comparacao"],
        "Comparação dos modelos avaliados",
        "A Regressão Logística obteve a maior PR-AUC preliminar. O Random Forest apresentou maior recall da classe de risco, melhor F1 e menor Brier score entre os modelos candidatos comparados.",
        "Como deixar de sinalizar quem precisa de apoio é especialmente crítico, o Random Forest foi escolhido como candidato principal para a próxima etapa de validação — sem encerrar a decisão metodológica.",
        auditada=False,
    )

    if metricas is not None:
        tabela_exibicao = metricas.rename(
            columns={
                "modelo": "Modelo",
                "recall_risco": "Recall de risco",
                "precision_risco": "Precisão de risco",
                "f1_risco": "F1 de risco",
                "pr_auc": "PR-AUC",
                "brier_score": "Brier score",
            }
        )
        colunas_numericas = [c for c in tabela_exibicao.columns if c != "Modelo"]
        tabela_exibicao[colunas_numericas] = tabela_exibicao[colunas_numericas].round(3)
        st.dataframe(tabela_exibicao, hide_index=True, width="stretch")
        st.caption("Resultados agregados da única janela temporal de teste disponível.")

    aba_curva, aba_matriz = st.tabs(["Curva precision–recall", "Matriz de confusão • 0,50"])
    with aba_curva:
        mostrar_figura(
            FIGURAS_MODELO["curva_pr"],
            "Precisão e cobertura variam com o limiar",
            "A curva evidencia o compromisso entre encontrar mais estudantes em risco e aumentar a quantidade de sinalizações incorretas.",
            "A escolha do limiar precisa combinar evidência técnica, capacidade de atendimento e risco de estigmatização.",
            auditada=False,
        )
    with aba_matriz:
        mostrar_figura(
            FIGURAS_MODELO["matriz_050"],
            "Erros têm custos educacionais diferentes",
            "No limiar padrão 0,50, o modelo registrou 206 verdadeiros positivos, 99 falsos negativos, 70 falsos positivos e 303 verdadeiros negativos.",
            "Falsos negativos podem deixar estudantes sem apoio preventivo; falsos positivos podem gerar rotulação e uso inadequado de recursos. Ambos exigem revisão humana.",
            auditada=False,
        )

    with st.expander("Análise de sensibilidade sem Fase e Idade"):
        sensibilidade = carregar_tabela(TABELAS_MODELO["sensibilidade"], auditada=False)
        if sensibilidade is not None:
            st.dataframe(sensibilidade.round(3), hide_index=True, width="stretch")
            st.caption("Teste agregado exploratório para apoiar a discussão sobre possíveis proxies. Não constitui validação de equidade.")


def pagina_limiar() -> None:
    cabecalho_secao(
        "Capítulo 5 • Decisão exploratória",
        "O que muda ao reduzir o limiar para 0,40?",
        "O limiar transforma probabilidades em sinalizações. Reduzi-lo aumenta a cobertura do risco, mas também amplia falsos positivos e demanda operacional.",
    )

    limiares = carregar_tabela(TABELAS_MODELO["limiares"], auditada=False)
    linha_050 = None
    linha_040 = None
    if limiares is not None and "limiar" in limiares.columns:
        linha_050_df = limiares[(limiares["limiar"] - 0.50).abs() < 1e-9]
        linha_040_df = limiares[(limiares["limiar"] - 0.40).abs() < 1e-9]
        linha_050 = linha_050_df.iloc[0] if not linha_050_df.empty else None
        linha_040 = linha_040_df.iloc[0] if not linha_040_df.empty else None

    st.markdown('<div class="etica"><strong>Guardrail:</strong> o limiar 0,40 é exclusivamente exploratório. Não está aprovado para triagem real, priorização de atendimento ou qualquer decisão operacional.</div>', unsafe_allow_html=True)

    if linha_050 is not None and linha_040 is not None:
        esquerda, direita = st.columns(2)
        with esquerda:
            st.markdown("### Limiar padrão • 0,50")
            a, b, c = st.columns(3)
            a.metric("Recall", formatar_percentual(float(linha_050["recall_risco"])))
            b.metric("Falsos negativos", int(linha_050["falsos_negativos"]))
            c.metric("Falsos positivos", int(linha_050["falsos_positivos"]))
        with direita:
            st.markdown("### Limiar exploratório • 0,40")
            a, b, c = st.columns(3)
            a.metric("Recall", formatar_percentual(float(linha_040["recall_risco"])))
            b.metric("Falsos negativos", int(linha_040["falsos_negativos"]), delta=-50)
            c.metric("Falsos positivos", int(linha_040["falsos_positivos"]), delta=48, delta_color="inverse")

    mostrar_figura(
        FIGURAS_MODELO["matriz_040"],
        "Mais cobertura, maior volume de revisão",
        "No limiar 0,40, o recall sobe para 83,9% e os falsos negativos caem de 99 para 49. Em contrapartida, os falsos positivos aumentam de 70 para 118.",
        "A redução pode favorecer prevenção, mas exige capacidade de acolhimento e mecanismos para reduzir estigma. A escolha não pode ser apenas matemática.",
        auditada=False,
    )

    if limiares is not None:
        with st.expander("Consultar análise completa de limiares"):
            st.dataframe(limiares.round(3), hide_index=True, width="stretch")
            st.caption("Tabela agregada da avaliação preliminar. Nenhum estudante é identificado.")


def pagina_recomendacoes() -> None:
    cabecalho_secao(
        "Capítulo 6 • Ação",
        "Recomendações para uma prevenção responsável",
        "As evidências apontam caminhos de acompanhamento. A implementação deve começar pequena, supervisionada e alinhada à capacidade real da equipe pedagógica.",
    )

    recomendacoes = [
        ("01", "Combinar sinais", "Priorizar acompanhamento quando quedas acadêmicas, de engajamento e psicossociais aparecem em conjunto, evitando decisões por um único indicador."),
        ("02", "Revisar com equipe pedagógica", "Transformar sinalizações em pauta de revisão humana, considerando contexto, trajetória e informações que não estão na base."),
        ("03", "Acompanhar transições críticas", "Criar atenção preventiva antes e depois da passagem da FASE 2 para a FASE 3, com monitoramento de IDA e IEG."),
        ("04", "Integrar IPS e aprendizagem", "Acompanhar quedas relevantes no IPS junto a desempenho e engajamento, oferecendo acolhimento em vez de rotulação."),
        ("05", "Dimensionar capacidade", "Definir qualquer limiar conforme a capacidade de atendimento e o custo educacional de falsos negativos e falsos positivos."),
        ("06", "Reavaliar anualmente", "Revisar target, calibração, desempenho por grupos, mudança de distribuição e consequências das intervenções a cada ciclo."),
    ]
    for inicio in range(0, len(recomendacoes), 3):
        colunas = st.columns(3)
        for coluna, (numero, titulo, texto) in zip(colunas, recomendacoes[inicio : inicio + 3]):
            with coluna:
                st.markdown(f'<div class="action-card"><div class="numero">AÇÃO {numero}</div><div class="card-title">{titulo}</div><p>{texto}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="insight"><strong>Princípio de produto:</strong> o modelo deve ampliar a capacidade de cuidado da equipe — nunca automatizar decisões sobre oportunidades, mérito ou permanência.</div>', unsafe_allow_html=True)


def pagina_etica() -> None:
    cabecalho_secao(
        "Capítulo 7 • Governança",
        "Limitações, ética e privacidade",
        "A utilidade do projeto depende de reconhecer onde a evidência termina. Este produto não está pronto para uso operacional e não publica qualquer dado individual.",
    )

    esquerda, direita = st.columns(2)
    with esquerda:
        st.markdown("### Limitações metodológicas")
        st.markdown(
            """
            - O target de risco de defasagem no ano seguinte é provisório.
            - Há somente três anos de dados e uma única janela temporal de teste.
            - Não foi realizada validação externa em outra população ou período.
            - As probabilidades ainda precisam de calibração e monitoramento.
            - Fase e Idade podem funcionar como proxies e exigem avaliação de equidade.
            - Correlações e regressões exploratórias não demonstram causalidade.
            - Personas são segmentações operacionais, não diagnósticos.
            """
        )
    with direita:
        st.markdown("### Usos expressamente proibidos")
        st.markdown(
            """
            - Excluir ou punir estudantes.
            - Criar ranking individual de mérito ou risco.
            - Restringir acesso a oportunidades.
            - Automatizar sanções ou decisões pedagógicas.
            - Inferir diagnósticos clínicos ou capacidade individual.
            - Avaliar profissionais sem contexto.
            - Expor RA, nome, nascimento ou trajetória identificável.
            """
        )

    st.markdown('<div class="etica"><strong>Regra de decisão:</strong> uma sinalização deve levar à revisão humana e à oferta de apoio. Nunca deve ser apresentada ao estudante como destino, rótulo ou classificação definitiva.</div>', unsafe_allow_html=True)

    st.markdown("### Checklist antes de qualquer piloto")
    itens = [
        "Aprovar formalmente o target e a finalidade de uso.",
        "Validar o modelo em nova janela temporal e, quando possível, externamente.",
        "Definir capacidade de atendimento e protocolo de revisão humana.",
        "Avaliar calibração, erros e equidade por grupos suficientemente amplos.",
        "Documentar versão, responsáveis, validade e critérios de interrupção.",
        "Monitorar resultados das intervenções e possíveis efeitos adversos.",
    ]
    for item in itens:
        st.checkbox(item, value=False, disabled=True)


def rodape() -> None:
    st.markdown(
        '<div class="rodape">Datathon PósTech • Case Passos Mágicos • Conteúdo agregado para fins acadêmicos e de apoio à decisão</div>',
        unsafe_allow_html=True,
    )


def barra_lateral() -> str:
    with st.sidebar:
        st.markdown("## ✨ Passos Mágicos")
        st.caption("Inteligência educacional responsável")
        st.divider()
        pagina = st.radio(
            "Navegação",
            [
                "Visão geral",
                "Diagnóstico educacional",
                "Sinais da EDA",
                "Perguntas extras",
                "Modelo preliminar",
                "Limiar exploratório",
                "Recomendações",
                "Ética e limitações",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        if MANIFESTO.empty:
            st.warning("Manifesto da EDA indisponível")
        else:
            total = len(MANIFESTO)
            disponiveis = sum(
                1
                for caminho in MANIFESTO.get("arquivo_gerado", pd.Series(dtype=str)).dropna()
                if resolver_caminho(str(caminho), exigir_auditoria=True) is not None
            )
            textos = int((MANIFESTO.get("tipo_artefato", pd.Series(dtype=str)) == "texto").sum())
            st.caption(f"Auditoria da EDA: {disponiveis} arquivos disponíveis • {textos} síntese textual")
        st.success("Somente dados agregados")
        st.caption("Sem busca individual • Sem ranking • Sem decisão automática")
        return pagina


def main() -> None:
    aplicar_estilo()
    pagina = barra_lateral()
    paginas = {
        "Visão geral": pagina_visao_geral,
        "Diagnóstico educacional": pagina_diagnostico,
        "Sinais da EDA": pagina_sinais_eda,
        "Perguntas extras": pagina_perguntas_extras,
        "Modelo preliminar": pagina_modelo,
        "Limiar exploratório": pagina_limiar,
        "Recomendações": pagina_recomendacoes,
        "Ética e limitações": pagina_etica,
    }
    paginas[pagina]()
    rodape()


if __name__ == "__main__":
    main()
