"""Catálogo inicial de features e regras contra vazamento temporal.

Este módulo não define o target definitivo e não treina modelos.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ConfiguracaoTemporal:
    """Define a janela de observação e o ano do desfecho."""

    ano_features: int
    ano_target: int

    def validar(self) -> None:
        if self.ano_features >= self.ano_target:
            raise ValueError("O ano das features deve ser anterior ao ano do target.")


IDENTIFICADORES_PROIBIDOS = {
    "ra",
    "nome",
    "nome_anonimizado",
    "data_de_nasc",
    "avaliador1",
    "avaliador2",
    "avaliador3",
    "avaliador4",
    "avaliador5",
    "avaliador6",
}

LEAKAGE_SE_TARGET_DEFASAGEM = {
    "defasagem",
    "ian",
    "fase_ideal",
    "inde",
    "pedra",
}

FEATURES_CANDIDATAS_COM_VALIDACAO_TEMPORAL = {
    "fase",
    "idade",
    "genero",
    "ano_ingresso",
    "instituicao_de_ensino",
    "iaa",
    "ieg",
    "ips",
    "ipp",
    "ida",
    "mat",
    "por",
    "ing",
    "ipv",
}


def classificar_colunas(colunas: list[str] | pd.Index) -> pd.DataFrame:
    """Classifica colunas sem afirmar que uma feature já está aprovada."""
    linhas = []
    for coluna_original in colunas:
        coluna = str(coluna_original).lower()
        if coluna in IDENTIFICADORES_PROIBIDOS:
            categoria = "proibida_identificacao"
            justificativa = "Identificador ou quase-identificador; não usar como feature."
        elif coluna in LEAKAGE_SE_TARGET_DEFASAGEM:
            categoria = "proibida_ou_condicional_leakage"
            justificativa = "Pode derivar do próprio desfecho ou ser calculada no mesmo período."
        elif coluna in FEATURES_CANDIDATAS_COM_VALIDACAO_TEMPORAL:
            categoria = "candidata_condicional"
            justificativa = "Usar somente se disponível antes do desfecho e com justificativa ética."
        elif coluna.startswith("flag_"):
            categoria = "controle_qualidade"
            justificativa = "Preferencialmente usar na validação, não como sinal preditivo."
        else:
            categoria = "requer_avaliacao"
            justificativa = "Sem classificação automática; exige dicionário e data de disponibilidade."
        linhas.append(
            {
                "coluna": coluna_original,
                "categoria": categoria,
                "justificativa": justificativa,
            }
        )
    return pd.DataFrame(linhas)


def separar_janela_temporal(
    df: pd.DataFrame,
    configuracao: ConfiguracaoTemporal,
    coluna_ano: str = "ano_referencia",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa observações de features e target, sem realizar junção por aluno."""
    configuracao.validar()
    if coluna_ano not in df.columns:
        raise KeyError(f"Coluna temporal ausente: {coluna_ano}")
    features = df.loc[df[coluna_ano] == configuracao.ano_features].copy()
    target = df.loc[df[coluna_ano] == configuracao.ano_target].copy()
    return features, target
