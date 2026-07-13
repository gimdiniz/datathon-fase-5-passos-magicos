from __future__ import annotations

import math

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)


def avaliar_classificacao(
    y_verdadeiro: pd.Series,
    probabilidades: pd.Series,
    predicoes: pd.Series,
) -> dict[str, float]:
    return {
        "recall_risco": recall_score(y_verdadeiro, predicoes, zero_division=0),
        "precision_risco": precision_score(
            y_verdadeiro, predicoes, zero_division=0
        ),
        "f1_risco": f1_score(y_verdadeiro, predicoes, zero_division=0),
        "pr_auc": average_precision_score(y_verdadeiro, probabilidades),
        "brier_score": brier_score_loss(y_verdadeiro, probabilidades),
    }


def treinar_e_avaliar_modelos(
    modelos: dict[str, BaseEstimator],
    x_treino: pd.DataFrame,
    y_treino: pd.Series,
    x_teste: pd.DataFrame,
    y_teste: pd.Series,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, BaseEstimator]]:
    resultados = []
    matrizes = {}
    ajustados = {}

    for nome, modelo in modelos.items():
        modelo.fit(x_treino, y_treino)
        probabilidades = modelo.predict_proba(x_teste)[:, 1]
        predicoes = modelo.predict(x_teste)
        metricas = avaliar_classificacao(y_teste, probabilidades, predicoes)
        metricas["modelo"] = nome
        resultados.append(metricas)
        matrizes[nome] = pd.DataFrame(
            confusion_matrix(y_teste, predicoes, labels=[0, 1]),
            index=["Real: sem risco", "Real: risco"],
            columns=["Previsto: sem risco", "Previsto: risco"],
        )
        ajustados[nome] = modelo

    comparacao = (
        pd.DataFrame(resultados)
        .set_index("modelo")
        .sort_values("pr_auc", ascending=False)
    )
    return comparacao, matrizes, ajustados


def avaliar_modelos_ajustados(
    modelos_ajustados: dict[str, BaseEstimator],
    x: pd.DataFrame,
    y: pd.Series,
) -> pd.DataFrame:
    resultados = []
    for nome, modelo in modelos_ajustados.items():
        probabilidades = modelo.predict_proba(x)[:, 1]
        predicoes = modelo.predict(x)
        metricas = avaliar_classificacao(y, probabilidades, predicoes)
        metricas["modelo"] = nome
        resultados.append(metricas)
    return pd.DataFrame(resultados).set_index("modelo").sort_values(
        "pr_auc", ascending=False
    )


def plotar_matrizes_confusao(
    matrizes: dict[str, pd.DataFrame],
) -> tuple[plt.Figure, list[plt.Axes]]:
    colunas = 2
    linhas = math.ceil(len(matrizes) / colunas)
    figura, eixos = plt.subplots(linhas, colunas, figsize=(12, 4.5 * linhas))
    eixos_lista = list(eixos.flat)
    for eixo, (nome, matriz) in zip(eixos_lista, matrizes.items()):
        sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", cbar=False, ax=eixo)
        eixo.set_title(nome)
        eixo.set_xlabel("")
        eixo.set_ylabel("")
    for eixo in eixos_lista[len(matrizes) :]:
        eixo.axis("off")
    figura.suptitle("Matrizes de confusão no teste temporal 2023→2024", y=1.01)
    figura.tight_layout()
    return figura, eixos_lista


def plotar_curvas_precision_recall(
    modelos_ajustados: dict[str, BaseEstimator],
    x_teste: pd.DataFrame,
    y_teste: pd.Series,
) -> tuple[plt.Figure, plt.Axes]:
    figura, eixo = plt.subplots(figsize=(12, 6))
    for nome, modelo in modelos_ajustados.items():
        probabilidades = modelo.predict_proba(x_teste)[:, 1]
        precisao, recall, _ = precision_recall_curve(y_teste, probabilidades)
        pr_auc = average_precision_score(y_teste, probabilidades)
        eixo.plot(recall, precisao, label=f"{nome} (PR-AUC={pr_auc:.3f})")
    eixo.axhline(
        y_teste.mean(),
        linestyle="--",
        color="gray",
        label=f"Prevalência do risco ({y_teste.mean():.3f})",
    )
    eixo.set_xlabel("Recall da classe de risco")
    eixo.set_ylabel("Precisão da classe de risco")
    eixo.set_title("Curvas precisão-recall no teste temporal")
    eixo.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    figura.tight_layout()
    return figura, eixo
