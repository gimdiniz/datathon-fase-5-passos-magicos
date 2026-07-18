from __future__ import annotations

import json
import time
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from src.avaliacao_modelos import avaliar_classificacao
from src.modelagem import (
    COLUNA_TARGET,
    COLUNAS_PROIBIDAS,
    FEATURES_PRINCIPAIS,
    SEMENTE,
    construir_preprocessador,
)


SCORING = {
    "pr_auc": "average_precision",
    "recall": "recall",
    "precision": "precision",
    "f1": "f1",
    "brier": "neg_brier_score",
}

PESOS_LOGISTICA_ARVORE: list[Any] = [
    None,
    "balanced",
    {0: 1, 1: 1.5},
    {0: 1, 1: 2.0},
    {0: 1, 1: 3.0},
]

PESOS_RANDOM_FOREST: list[Any] = [
    None,
    "balanced",
    "balanced_subsample",
    {0: 1, 1: 1.5},
    {0: 1, 1: 2.0},
    {0: 1, 1: 3.0},
]

METRICAS_CV = ("pr_auc", "recall", "precision", "f1", "brier")


def construir_grids() -> dict[str, dict[str, list[Any]]]:
    """Constrói os grids aprovados, incluindo apenas pesos válidos."""
    return {
        "LogisticRegression": {
            "modelo__C": [0.01, 0.1, 1.0, 10.0, 100.0],
            "modelo__solver": ["liblinear", "lbfgs"],
            "modelo__class_weight": PESOS_LOGISTICA_ARVORE,
        },
        "DecisionTreeClassifier": {
            "modelo__criterion": ["gini", "entropy"],
            "modelo__max_depth": [3, 5, 8, None],
            "modelo__min_samples_split": [2, 10, 30],
            "modelo__min_samples_leaf": [5, 10, 20],
            "modelo__class_weight": PESOS_LOGISTICA_ARVORE,
        },
        "RandomForestClassifier": {
            "modelo__n_estimators": [300, 600],
            "modelo__max_depth": [6, 10, None],
            "modelo__min_samples_split": [2, 10],
            "modelo__min_samples_leaf": [3, 5, 10],
            "modelo__max_features": ["sqrt", 0.7],
            "modelo__class_weight": PESOS_RANDOM_FOREST,
        },
        "GradientBoostingClassifier": {
            "modelo__n_estimators": [100, 150, 250],
            "modelo__learning_rate": [0.03, 0.05, 0.1],
            "modelo__max_depth": [1, 2, 3],
            "modelo__min_samples_leaf": [5, 10, 20],
            "modelo__subsample": [0.7, 1.0],
        },
    }


def construir_modelos_candidatos() -> dict[str, Pipeline]:
    """Cria pipelines sem alterar o preprocessing aprovado."""
    estimadores = {
        "LogisticRegression": LogisticRegression(
            max_iter=2_000,
            random_state=SEMENTE,
        ),
        "DecisionTreeClassifier": DecisionTreeClassifier(random_state=SEMENTE),
        "RandomForestClassifier": RandomForestClassifier(
            random_state=SEMENTE,
            n_jobs=1,
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            random_state=SEMENTE,
        ),
    }
    return {
        nome: Pipeline(
            [
                ("preprocessamento", construir_preprocessador()),
                ("modelo", estimador),
            ]
        )
        for nome, estimador in estimadores.items()
    }


def contar_combinacoes(grids: Mapping[str, Mapping[str, list[Any]]]) -> pd.DataFrame:
    linhas = []
    for modelo, grid in grids.items():
        combinacoes = int(np.prod([len(valores) for valores in grid.values()]))
        linhas.append(
            {
                "modelo": modelo,
                "combinacoes": combinacoes,
                "fits_cv": combinacoes * 5,
                "refit_pr_auc": 1,
                "ajustes_grid_total": combinacoes * 5 + 1,
            }
        )
    return pd.DataFrame(linhas)


def validar_isolamento_grid_search(
    pares_treino: pd.DataFrame,
    pares_teste: pd.DataFrame,
) -> dict[str, int | bool]:
    """Audita em memória a proveniência temporal sem exportar identificadores."""
    colunas = {"RA", "ano_features", "ano_target", COLUNA_TARGET}
    for nome, pares in (("treino", pares_treino), ("teste", pares_teste)):
        ausentes = colunas.difference(pares.columns)
        if ausentes:
            raise KeyError(f"Colunas ausentes em {nome}: {sorted(ausentes)}")
        if pares["RA"].isna().any() or pares["RA"].duplicated().any():
            raise ValueError(f"RA ausente ou duplicado dentro do conjunto de {nome}.")

    treino_temporal_ok = bool(
        pares_treino["ano_features"].eq(2022).all()
        and pares_treino["ano_target"].eq(2023).all()
    )
    teste_temporal_ok = bool(
        pares_teste["ano_features"].eq(2023).all()
        and pares_teste["ano_target"].eq(2024).all()
    )
    if not treino_temporal_ok or not teste_temporal_ok:
        raise ValueError("As janelas temporais não correspondem ao desenho aprovado.")

    chaves_treino = set(
        pares_treino[["RA", "ano_features", "ano_target"]].itertuples(
            index=False, name=None
        )
    )
    chaves_teste = set(
        pares_teste[["RA", "ano_features", "ano_target"]].itertuples(
            index=False, name=None
        )
    )
    chaves_compartilhadas = len(chaves_treino.intersection(chaves_teste))
    if chaves_compartilhadas:
        raise ValueError("Uma ou mais linhas temporais do teste também estão no treino.")

    alunos_sobrepostos = int(pares_teste["RA"].isin(pares_treino["RA"]).sum())
    alunos_novos_teste = int((~pares_teste["RA"].isin(pares_treino["RA"])).sum())
    return {
        "treino_temporal_ok": treino_temporal_ok,
        "teste_temporal_ok": teste_temporal_ok,
        "linhas_treino": int(len(pares_treino)),
        "linhas_teste": int(len(pares_teste)),
        "chaves_temporais_compartilhadas": chaves_compartilhadas,
        "duplicidades_ra_treino": int(pares_treino["RA"].duplicated().sum()),
        "duplicidades_ra_teste": int(pares_teste["RA"].duplicated().sum()),
        "alunos_sobrepostos": alunos_sobrepostos,
        "alunos_novos_teste": alunos_novos_teste,
        "teste_entrou_grid_search": False,
    }


def _validar_entrada_treino(x_treino: pd.DataFrame, y_treino: pd.Series) -> None:
    if len(x_treino) != len(y_treino) or len(x_treino) != 570:
        raise ValueError("A entrada do Grid Search não corresponde às 570 linhas de treino.")
    if list(x_treino.columns) != FEATURES_PRINCIPAIS:
        raise ValueError("As features do Grid Search diferem das features aprovadas.")
    proibidas = COLUNAS_PROIBIDAS.intersection(x_treino.columns)
    if proibidas:
        raise ValueError(f"Features proibidas no Grid Search: {sorted(proibidas)}")
    if y_treino.isna().any() or set(y_treino.unique()).difference({0, 1}):
        raise ValueError("Target de treino ausente ou fora do domínio binário.")


def executar_grid_search(
    x_treino: pd.DataFrame,
    y_treino: pd.Series,
    modelos: Mapping[str, Pipeline] | None = None,
    grids: Mapping[str, Mapping[str, list[Any]]] | None = None,
    verbose: int = 1,
) -> tuple[dict[str, GridSearchCV], pd.DataFrame]:
    """Executa as buscas usando somente a janela de treino recebida."""
    _validar_entrada_treino(x_treino, y_treino)
    modelos = construir_modelos_candidatos() if modelos is None else dict(modelos)
    grids = construir_grids() if grids is None else dict(grids)
    if set(modelos) != set(grids):
        raise ValueError("Modelos e grids devem conter exatamente as mesmas famílias.")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    buscas: dict[str, GridSearchCV] = {}
    tempos = []
    for nome in modelos:
        inicio = time.perf_counter()
        busca = GridSearchCV(
            estimator=modelos[nome],
            param_grid=grids[nome],
            scoring=SCORING,
            refit="pr_auc",
            cv=cv,
            n_jobs=-1,
            verbose=verbose,
            error_score="raise",
            return_train_score=True,
        )
        busca.fit(x_treino, y_treino)
        duracao = time.perf_counter() - inicio
        buscas[nome] = busca
        tempos.append(
            {
                "modelo": nome,
                "tempo_grid_segundos": duracao,
                "combinacoes": len(busca.cv_results_["params"]),
                "fits_cv": len(busca.cv_results_["params"]) * 5,
            }
        )
    return buscas, pd.DataFrame(tempos)


def _serializar_valor(valor: Any) -> str:
    if valor is None:
        return "None"
    if isinstance(valor, dict):
        return json.dumps(valor, ensure_ascii=False, sort_keys=True)
    return str(valor)


def _serializar_parametros(parametros: Mapping[str, Any]) -> str:
    simplificados = {
        chave.removeprefix("modelo__"): valor for chave, valor in parametros.items()
    }
    return json.dumps(simplificados, ensure_ascii=False, sort_keys=True)


def resumir_cv_results(buscas: Mapping[str, GridSearchCV]) -> pd.DataFrame:
    """Consolida métricas de treino/validação sem qualquer dado por aluno."""
    blocos = []
    for modelo, busca in buscas.items():
        cv = busca.cv_results_
        bloco = pd.DataFrame(
            {
                "modelo": modelo,
                "indice_configuracao": np.arange(len(cv["params"]), dtype=int),
                "posicao_pr_auc": cv["rank_test_pr_auc"].astype(int),
                "parametros": [_serializar_parametros(p) for p in cv["params"]],
                "class_weight": [
                    _serializar_valor(p.get("modelo__class_weight", "não aplicável"))
                    for p in cv["params"]
                ],
                "tempo_medio_ajuste": cv["mean_fit_time"],
                "desvio_tempo_ajuste": cv["std_fit_time"],
            }
        )
        for metrica in METRICAS_CV:
            media_teste = np.asarray(cv[f"mean_test_{metrica}"], dtype=float)
            media_treino = np.asarray(cv[f"mean_train_{metrica}"], dtype=float)
            desvio_teste = np.asarray(cv[f"std_test_{metrica}"], dtype=float)
            if metrica == "brier":
                media_teste = -media_teste
                media_treino = -media_treino
            bloco[f"media_cv_{metrica}"] = media_teste
            bloco[f"desvio_cv_{metrica}"] = desvio_teste
            bloco[f"media_treino_{metrica}"] = media_treino
            bloco[f"gap_treino_validacao_{metrica}"] = media_treino - media_teste

        todas_chaves = sorted({chave for p in cv["params"] for chave in p})
        for chave in todas_chaves:
            coluna = "param_" + chave.removeprefix("modelo__")
            bloco[coluna] = [
                _serializar_valor(p[chave]) if chave in p else "" for p in cv["params"]
            ]
        blocos.append(bloco)

    resultado = pd.concat(blocos, ignore_index=True)
    return resultado.sort_values(
        ["modelo", "media_cv_pr_auc", "desvio_cv_pr_auc"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def _complexidade(modelo: str, parametros: Mapping[str, Any]) -> tuple[Any, ...]:
    p = {k.removeprefix("modelo__"): v for k, v in parametros.items()}
    peso_ordem = {
        "None": 0,
        "balanced": 1,
        "balanced_subsample": 2,
        "{\"0\": 1, \"1\": 1.5}": 3,
        "{\"0\": 1, \"1\": 2.0}": 4,
        "{\"0\": 1, \"1\": 3.0}": 5,
    }
    peso = peso_ordem.get(_serializar_valor(p.get("class_weight")), 0)
    if modelo == "LogisticRegression":
        return (float(p["C"]), peso, 0 if p["solver"] == "lbfgs" else 1)
    if modelo == "DecisionTreeClassifier":
        profundidade = 10_000 if p["max_depth"] is None else int(p["max_depth"])
        return (
            profundidade,
            -int(p["min_samples_leaf"]),
            -int(p["min_samples_split"]),
            peso,
            0 if p["criterion"] == "gini" else 1,
        )
    if modelo == "RandomForestClassifier":
        profundidade = 10_000 if p["max_depth"] is None else int(p["max_depth"])
        return (
            int(p["n_estimators"]) * profundidade,
            profundidade,
            int(p["n_estimators"]),
            -int(p["min_samples_leaf"]),
            -int(p["min_samples_split"]),
            0 if p["max_features"] == "sqrt" else 1,
            peso,
        )
    if modelo == "GradientBoostingClassifier":
        return (
            int(p["n_estimators"]) * int(p["max_depth"]),
            int(p["max_depth"]),
            int(p["n_estimators"]),
            -int(p["min_samples_leaf"]),
            -float(p["subsample"]),
            float(p["learning_rate"]),
        )
    raise KeyError(f"Família desconhecida: {modelo}")


def selecionar_melhores_estimadores(
    buscas: Mapping[str, GridSearchCV],
    resumo_cv: pd.DataFrame,
    x_treino: pd.DataFrame,
    y_treino: pd.Series,
    tolerancia_pr_auc: float = 0.01,
) -> tuple[dict[str, BaseEstimator], pd.DataFrame]:
    """Aplica parcimônia entre resultados próximos e ajusta a escolha no treino."""
    selecionados: dict[str, BaseEstimator] = {}
    linhas = []
    for modelo, busca in buscas.items():
        familia = resumo_cv.loc[resumo_cv["modelo"].eq(modelo)].copy()
        melhor_media = float(familia["media_cv_pr_auc"].max())
        lider = familia.sort_values(
            ["media_cv_pr_auc", "desvio_cv_pr_auc"], ascending=[False, True]
        ).iloc[0]
        compativel_delta = (melhor_media - familia["media_cv_pr_auc"]) < tolerancia_pr_auc
        erro_padrao_diferenca = np.sqrt(
            lider["desvio_cv_pr_auc"] ** 2 + familia["desvio_cv_pr_auc"] ** 2
        ) / np.sqrt(5)
        compativel_desvio = (
            melhor_media - familia["media_cv_pr_auc"] <= erro_padrao_diferenca
        )
        candidatas = familia.loc[compativel_delta | compativel_desvio].copy()
        candidatas["complexidade"] = [
            _complexidade(
                modelo,
                busca.cv_results_["params"][int(indice)],
            )
            for indice in candidatas["indice_configuracao"]
        ]
        candidatas["gap_abs"] = candidatas["gap_treino_validacao_pr_auc"].abs()
        candidatas = candidatas.sort_values(
            ["complexidade", "gap_abs", "desvio_cv_pr_auc", "media_cv_pr_auc"],
            ascending=[True, True, True, False],
        )
        escolhida = candidatas.iloc[0]
        indice = int(escolhida["indice_configuracao"])
        parametros = busca.cv_results_["params"][indice]

        if indice == int(busca.best_index_):
            estimador = busca.best_estimator_
            refit_adicional = False
        else:
            estimador = clone(busca.estimator).set_params(**parametros)
            estimador.fit(x_treino, y_treino)
            refit_adicional = True
        selecionados[modelo] = estimador
        linhas.append(
            {
                "modelo": modelo,
                "parametros_selecionados": _serializar_parametros(parametros),
                "class_weight_selecionado": _serializar_valor(
                    parametros.get("modelo__class_weight", "não aplicável")
                ),
                "indice_configuracao_selecionada": indice,
                "posicao_pr_auc": int(escolhida["posicao_pr_auc"]),
                "media_cv_pr_auc": escolhida["media_cv_pr_auc"],
                "desvio_cv_pr_auc": escolhida["desvio_cv_pr_auc"],
                "media_cv_recall": escolhida["media_cv_recall"],
                "desvio_cv_recall": escolhida["desvio_cv_recall"],
                "media_cv_precision": escolhida["media_cv_precision"],
                "desvio_cv_precision": escolhida["desvio_cv_precision"],
                "media_cv_f1": escolhida["media_cv_f1"],
                "desvio_cv_f1": escolhida["desvio_cv_f1"],
                "media_cv_brier": escolhida["media_cv_brier"],
                "desvio_cv_brier": escolhida["desvio_cv_brier"],
                "media_treino_pr_auc": escolhida["media_treino_pr_auc"],
                "gap_treino_validacao_pr_auc": escolhida[
                    "gap_treino_validacao_pr_auc"
                ],
                "maior_pr_auc_media_familia": melhor_media,
                "delta_para_maior_pr_auc": melhor_media
                - escolhida["media_cv_pr_auc"],
                "configuracoes_compativeis": int(len(candidatas)),
                "refit_adicional_parcimonia": refit_adicional,
                "criterio_selecao": (
                    "PR-AUC compatível por diferença <0,01 ou erro-padrão combinado "
                    "dos 5 folds; desempate por simplicidade, gap, estabilidade e PR-AUC"
                ),
            }
        )
    return selecionados, pd.DataFrame(linhas)


def resumir_top_candidates(
    resumo_cv: pd.DataFrame,
    selecao: pd.DataFrame,
    n: int = 10,
) -> pd.DataFrame:
    selecionadas = set(
        zip(selecao["modelo"], selecao["indice_configuracao_selecionada"])
    )
    blocos = []
    for modelo, familia in resumo_cv.groupby("modelo", sort=False):
        top = familia.nsmallest(n, "posicao_pr_auc").copy()
        top["selecionada_por_parcimonia"] = [
            (modelo, indice) in selecionadas for indice in top["indice_configuracao"]
        ]
        blocos.append(top)
    colunas = [
        "modelo",
        "posicao_pr_auc",
        "parametros",
        "class_weight",
        "selecionada_por_parcimonia",
        "media_cv_pr_auc",
        "desvio_cv_pr_auc",
        "media_cv_recall",
        "desvio_cv_recall",
        "media_cv_precision",
        "desvio_cv_precision",
        "media_cv_f1",
        "desvio_cv_f1",
        "media_cv_brier",
        "media_treino_pr_auc",
        "gap_treino_validacao_pr_auc",
        "tempo_medio_ajuste",
    ]
    return pd.concat(blocos, ignore_index=True)[colunas]


def resumir_class_weight(resumo_cv: pd.DataFrame) -> pd.DataFrame:
    agregacoes = (
        resumo_cv.groupby(["modelo", "class_weight"], dropna=False)
        .agg(
            quantidade_configuracoes=("indice_configuracao", "size"),
            melhor_pr_auc_media=("media_cv_pr_auc", "max"),
            pr_auc_media_configuracoes=("media_cv_pr_auc", "mean"),
            recall_medio=("media_cv_recall", "mean"),
            precision_media=("media_cv_precision", "mean"),
            f1_medio=("media_cv_f1", "mean"),
            brier_medio=("media_cv_brier", "mean"),
            estabilidade_pr_auc_desvio_medio=("desvio_cv_pr_auc", "mean"),
            melhor_estabilidade_pr_auc=("desvio_cv_pr_auc", "min"),
        )
        .reset_index()
    )
    return agregacoes.sort_values(
        ["modelo", "melhor_pr_auc_media"], ascending=[True, False]
    ).reset_index(drop=True)


def avaliar_melhores_no_teste_temporal(
    estimadores: Mapping[str, BaseEstimator],
    x_teste: pd.DataFrame,
    y_teste: pd.Series,
    limiar: float = 0.50,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, np.ndarray]]:
    """Realiza a avaliação agregada única no teste temporal, com limiar fixo."""
    if limiar != 0.50:
        raise ValueError("A avaliação tuned desta etapa exige limiar fixo em 0,50.")
    resultados = []
    matrizes: dict[str, pd.DataFrame] = {}
    probabilidades_memoria: dict[str, np.ndarray] = {}
    for modelo, estimador in estimadores.items():
        probabilidades = estimador.predict_proba(x_teste)[:, 1]
        predicoes = (probabilidades >= limiar).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_teste, predicoes, labels=[0, 1]).ravel()
        linha = avaliar_classificacao(y_teste, probabilidades, predicoes)
        linha.update(
            {
                "modelo": modelo,
                "limiar": limiar,
                "verdadeiros_negativos": int(tn),
                "falsos_positivos": int(fp),
                "falsos_negativos": int(fn),
                "verdadeiros_positivos": int(tp),
            }
        )
        resultados.append(linha)
        matrizes[modelo] = pd.DataFrame(
            [[tn, fp], [fn, tp]],
            index=["Real: sem risco", "Real: risco"],
            columns=["Previsto: sem risco", "Previsto: risco"],
        )
        probabilidades_memoria[modelo] = probabilidades
    metricas = pd.DataFrame(resultados).sort_values("pr_auc", ascending=False)
    return metricas, matrizes, probabilidades_memoria


def comparar_baseline_tuned(
    metricas_baseline: pd.DataFrame,
    matrizes_baseline: Mapping[str, pd.DataFrame],
    metricas_tuned: pd.DataFrame,
    selecao_cv: pd.DataFrame,
) -> pd.DataFrame:
    alteracoes_complexidade = {
        "LogisticRegression": (
            "complexidade estrutural equivalente (C=1 e solver lbfgs); muda apenas "
            "o custo da classe 1 de balanced para 3,0"
        ),
        "DecisionTreeClassifier": (
            "complexidade mista: mantém profundidade 5, reduz folha mínima de 15 "
            "para 10 e aumenta min_samples_split de 2 para 30"
        ),
        "RandomForestClassifier": (
            "mais regularizado em profundidade/folhas/split (8→6, 5→10, 2→10), "
            "mesmas 300 árvores e maior fração de features por split"
        ),
        "GradientBoostingClassifier": (
            "mais raso e regularizado (profundidade 3→1, folha mínima 1→20), "
            "mesmos 150 estágios e learning_rate 0,05→0,1"
        ),
    }
    linhas = []
    baseline = metricas_baseline.copy()
    if "modelo" in baseline.columns:
        baseline = baseline.set_index("modelo")
    tuned = metricas_tuned.set_index("modelo")
    cv = selecao_cv.set_index("modelo")
    for modelo in tuned.index:
        matriz = matrizes_baseline[modelo].to_numpy()
        _, fp_base, fn_base, _ = matriz.ravel()
        b = baseline.loc[modelo]
        t = tuned.loc[modelo]
        c = cv.loc[modelo]
        linhas.append(
            {
                "modelo": modelo,
                "baseline_pr_auc": b["pr_auc"],
                "tuned_pr_auc": t["pr_auc"],
                "delta_pr_auc": t["pr_auc"] - b["pr_auc"],
                "baseline_recall": b["recall_risco"],
                "tuned_recall": t["recall_risco"],
                "delta_recall": t["recall_risco"] - b["recall_risco"],
                "baseline_precision": b["precision_risco"],
                "tuned_precision": t["precision_risco"],
                "delta_precision": t["precision_risco"] - b["precision_risco"],
                "baseline_f1": b["f1_risco"],
                "tuned_f1": t["f1_risco"],
                "delta_f1": t["f1_risco"] - b["f1_risco"],
                "baseline_brier": b["brier_score"],
                "tuned_brier": t["brier_score"],
                "delta_brier": t["brier_score"] - b["brier_score"],
                "baseline_falsos_positivos": int(fp_base),
                "tuned_falsos_positivos": int(t["falsos_positivos"]),
                "delta_falsos_positivos": int(t["falsos_positivos"] - fp_base),
                "baseline_falsos_negativos": int(fn_base),
                "tuned_falsos_negativos": int(t["falsos_negativos"]),
                "delta_falsos_negativos": int(t["falsos_negativos"] - fn_base),
                "tuned_pr_auc_cv": c["media_cv_pr_auc"],
                "tuned_desvio_pr_auc_cv": c["desvio_cv_pr_auc"],
                "tuned_gap_treino_validacao_pr_auc": c[
                    "gap_treino_validacao_pr_auc"
                ],
                "delta_pr_auc_teste_menos_cv": t["pr_auc"]
                - c["media_cv_pr_auc"],
                "alteracao_complexidade": alteracoes_complexidade[modelo],
            }
        )
    return pd.DataFrame(linhas)
