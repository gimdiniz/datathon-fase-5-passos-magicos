from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


SEMENTE = 42
COLUNA_TARGET = "risco_defasagem"

FEATURES_NUMERICAS = [
    "Idade",
    "Tempo_no_programa",
    "IAA",
    "IEG",
    "IPS",
    "IDA",
    "Nota_Matematica",
    "Nota_Portugues",
    "IPV",
]

FEATURES_CATEGORICAS = ["Fase"]
FEATURES_PRINCIPAIS = FEATURES_NUMERICAS + FEATURES_CATEGORICAS

COLUNAS_PROIBIDAS = {
    "RA",
    "Nome",
    "Nome Anonimizado",
    "Ano Nascimento",
    "Data de Nasc",
    "data_de_nasc",
    "Avaliador1",
    "Avaliador2",
    "Avaliador3",
    "Avaliador4",
    "Avaliador5",
    "Avaliador6",
    "Defasagem",
    "IAN",
    "Fase Ideal",
    "INDE",
    "Pedra",
    "Pedra 20",
    "Pedra 21",
}


def validar_target_defasagem(df: pd.DataFrame) -> dict[str, int | bool]:
    obrigatorias = {"Defasagem", "IAN"}
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise KeyError(f"Colunas obrigatórias ausentes: {sorted(ausentes)}")

    defasagem = pd.to_numeric(df["Defasagem"], errors="coerce")
    ian = pd.to_numeric(df["IAN"], errors="coerce")
    nulos_defasagem = int(defasagem.isna().sum())
    nulos_ian = int(ian.isna().sum())

    ian_esperado = np.select(
        [defasagem <= -3, defasagem.isin([-2, -1]), defasagem >= 0],
        [2.5, 5.0, 10.0],
        default=np.nan,
    )
    inconsistencias = int((ian.to_numpy() != ian_esperado).sum())
    dominio_ian_valido = bool(ian.dropna().isin([2.5, 5.0, 10.0]).all())

    return {
        "registros": int(len(df)),
        "nulos_defasagem": nulos_defasagem,
        "nulos_ian": nulos_ian,
        "inconsistencias_defasagem_ian": inconsistencias,
        "dominio_ian_valido": dominio_ian_valido,
    }


def criar_variavel_risco(defasagem: pd.Series) -> pd.Series:
    """Cria o target binário: 1 quando Defasagem é negativa."""
    valores = pd.to_numeric(defasagem, errors="coerce")
    if valores.isna().any():
        raise ValueError("O target Defasagem contém valores ausentes ou inválidos.")
    return (valores < 0).astype("int8").rename(COLUNA_TARGET)


def _validar_unicidade_aluno_ano(df: pd.DataFrame) -> None:
    duplicados = int(df.duplicated(["RA", "Ano_Referencia"]).sum())
    if duplicados:
        raise ValueError(
            f"Foram encontrados {duplicados} registros duplicados por RA e ano."
        )


def criar_pares_temporais(
    df: pd.DataFrame,
    ano_features: int,
    ano_target: int,
    features: Iterable[str] = FEATURES_PRINCIPAIS,
) -> pd.DataFrame:

    if ano_target != ano_features + 1:
        raise ValueError("Esta versão aceita somente anos consecutivos.")

    _validar_unicidade_aluno_ano(df)
    features = list(features)
    colunas_necessarias = {
        "RA",
        "Ano_Referencia",
        "Ano ingresso",
        "Defasagem",
        *features,
    }
    colunas_necessarias.discard("Tempo_no_programa")
    ausentes = colunas_necessarias.difference(df.columns)
    if ausentes:
        raise KeyError(f"Colunas necessárias ausentes: {sorted(ausentes)}")

    observacao = df.loc[df["Ano_Referencia"] == ano_features].copy()
    desfecho = df.loc[
        df["Ano_Referencia"] == ano_target, ["RA", "Defasagem"]
    ].copy()

    observacao["Tempo_no_programa"] = (
        ano_features - pd.to_numeric(observacao["Ano ingresso"], errors="coerce")
    )
    observacao = observacao[["RA", *features]]
    desfecho[COLUNA_TARGET] = criar_variavel_risco(desfecho["Defasagem"])
    desfecho = desfecho[["RA", COLUNA_TARGET]]

    pares = observacao.merge(
        desfecho,
        on="RA",
        how="inner",
        validate="one_to_one",
    )
    pares.insert(1, "ano_features", ano_features)
    pares.insert(2, "ano_target", ano_target)
    return pares


def separar_matriz_target(
    pares: pd.DataFrame,
    features: Iterable[str] = FEATURES_PRINCIPAIS,
) -> tuple[pd.DataFrame, pd.Series]:
    """Separa X e y garantindo que identificadores não entrem no modelo."""
    features = list(features)
    proibidas_presentes = COLUNAS_PROIBIDAS.intersection(features)
    if proibidas_presentes:
        raise ValueError(
            "Features proibidas detectadas: " + ", ".join(sorted(proibidas_presentes))
        )
    return pares[features].copy(), pares[COLUNA_TARGET].copy()


def construir_preprocessador(
    features_numericas: Iterable[str] = FEATURES_NUMERICAS,
    features_categoricas: Iterable[str] = FEATURES_CATEGORICAS,
) -> ColumnTransformer:
    pipeline_numerico = Pipeline(
        [
            ("imputador", SimpleImputer(strategy="median", add_indicator=True)),
            ("padronizacao", StandardScaler()),
        ]
    )
    pipeline_categorico = Pipeline(
        [
            ("imputador", SimpleImputer(strategy="most_frequent")),
            (
                "encoding",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numericas", pipeline_numerico, list(features_numericas)),
            ("categoricas", pipeline_categorico, list(features_categoricas)),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def construir_modelos_iniciais() -> dict[str, Pipeline]:
    estimadores = {
        "DummyClassifier": DummyClassifier(strategy="prior"),
        "LogisticRegression": LogisticRegression(
            max_iter=2_000,
            class_weight="balanced",
            random_state=SEMENTE,
        ),
        "DecisionTreeClassifier": DecisionTreeClassifier(
            max_depth=5,
            min_samples_leaf=15,
            class_weight="balanced",
            random_state=SEMENTE,
        ),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=SEMENTE,
            n_jobs=-1,
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
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
