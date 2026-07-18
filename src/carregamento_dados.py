"""Carregamento centralizado das bases locais do projeto.

Este módulo não baixa, não altera e não imprime dados. A base crua deve ser
obtida manualmente mediante autorização da organização responsável.
"""

from pathlib import Path
from zipfile import BadZipFile

import pandas as pd


ARQUIVO_BASE = Path("data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx")
ARQUIVO_PROCESSADO = Path("data/processed/passos_magicos_clean_eda.csv")
ABAS_ESPERADAS = ("PEDE2022", "PEDE2023", "PEDE2024")


def localizar_raiz_projeto() -> Path:
    """Retorna a raiz do repositório a partir da localização deste módulo."""

    return Path(__file__).resolve().parents[1]


def localizar_arquivo_base() -> Path:
    """Retorna o caminho da base crua ou lança erro com orientação de acesso."""

    caminho = localizar_raiz_projeto() / ARQUIVO_BASE
    if not caminho.is_file():
        raise FileNotFoundError(
            "Base local não encontrada. Obtenha autorização da organização "
            "responsável e copie o arquivo exatamente para "
            f"'{ARQUIVO_BASE.as_posix()}'. Depois execute "
            "'python scripts/validar_base_local.py'. O projeto não baixa a base."
        )
    return caminho


def carregar_abas_base() -> dict[str, pd.DataFrame]:
    """Carrega as três abas esperadas sem transformar os dados."""

    caminho = localizar_arquivo_base()
    try:
        abas = pd.read_excel(
            caminho,
            sheet_name=list(ABAS_ESPERADAS),
            engine="openpyxl",
        )
    except ValueError as erro:
        raise ValueError(
            "Não foi possível carregar todas as abas esperadas: "
            f"{', '.join(ABAS_ESPERADAS)}. Execute "
            "'python scripts/validar_base_local.py' para obter o diagnóstico."
        ) from erro
    except (OSError, ImportError, BadZipFile) as erro:
        raise RuntimeError(
            "Não foi possível ler a base local. Confirme que o arquivo é um XLSX "
            "legível e que as dependências foram instaladas com "
            "'pip install -r requirements.txt'."
        ) from erro
    return abas


def carregar_base_processada() -> pd.DataFrame:
    """Carrega o artefato local produzido pelo notebook 01, sem fallback remoto."""

    caminho = localizar_raiz_projeto() / ARQUIVO_PROCESSADO
    if not caminho.is_file():
        raise FileNotFoundError(
            "Base processada local não encontrada em "
            f"'{ARQUIVO_PROCESSADO.as_posix()}'. Valide a base autorizada e execute "
            "primeiro 'notebooks/01_visao_geral_base.ipynb'. O projeto não baixa "
            "nem distribui bases processadas linha a linha."
        )
    try:
        return pd.read_csv(caminho)
    except (OSError, pd.errors.ParserError, UnicodeError) as erro:
        raise RuntimeError(
            "Não foi possível ler a base processada local. Gere novamente o "
            "artefato executando 'notebooks/01_visao_geral_base.ipynb'."
        ) from erro
