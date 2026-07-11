"""Rotinas reproduzíveis para auditoria das bases do Datathon Passos Mágicos.

O módulo é deliberadamente somente leitura: nenhuma função sobrescreve as bases.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


INDICADORES = ("IAA", "IEG", "IPS", "IPP", "IDA", "IPV", "IAN", "INDE")
COLUNAS_IDENTIFICACAO = (
    "RA",
    "Nome",
    "Nome Anonimizado",
    "nome_anonimizado",
    "ra",
    "Data de Nasc",
    "data_de_nasc",
)
COLUNAS_TARGET_CANDIDATAS = ("Defas", "Defasagem", "defasagem", "IAN", "ian")


def _serializar(valor: Any) -> Any:
    """Converte tipos NumPy/Pandas para estruturas serializáveis em JSON."""
    if pd.isna(valor):
        return None
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return float(valor)
    if isinstance(valor, (pd.Timestamp,)):
        return valor.isoformat()
    return valor


def normalizar_nome_coluna(nome: str) -> str:
    """Normaliza nomes apenas para comparação; não altera o DataFrame original."""
    texto = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto).strip("_").lower()
    return texto


def _normalizar_para_comparacao_2024(nome: str) -> str:
    """Aproxima nomes equivalentes entre a planilha PEDE2024 e a camada limpa."""
    texto = normalizar_nome_coluna(nome)
    if texto in {"inde_2024", "pedra_2024"}:
        return texto.removesuffix("_2024")
    return texto


def carregar_tabela(caminho: str | Path, planilha: str | None = None) -> pd.DataFrame:
    """Carrega CSV ou XLSX sem modificar o arquivo de origem."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    if caminho.suffix.lower() == ".csv":
        return pd.read_csv(caminho)
    if caminho.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(caminho, sheet_name=planilha)
    raise ValueError(f"Formato não suportado: {caminho.suffix}")


def perfil_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Produz perfil de tipos, nulos, cardinalidade e amostras por coluna."""
    linhas: list[dict[str, Any]] = []
    for coluna in df.columns:
        serie = df[coluna]
        unicos = serie.dropna().unique()[:10]
        linhas.append(
            {
                "coluna": coluna,
                "tipo": str(serie.dtype),
                "nulos": int(serie.isna().sum()),
                "percentual_nulos": round(float(serie.isna().mean() * 100), 4),
                "valores_unicos": int(serie.nunique(dropna=True)),
                "amostra_valores": [_serializar(v) for v in unicos],
            }
        )
    return pd.DataFrame(linhas)


def estatisticas_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula estatísticas descritivas dos indicadores encontrados."""
    mapa = {normalizar_nome_coluna(c): c for c in df.columns}
    linhas: list[dict[str, Any]] = []
    for indicador in INDICADORES:
        coluna = mapa.get(indicador.lower())
        if coluna is None:
            continue
        serie = pd.to_numeric(df[coluna], errors="coerce")
        linhas.append(
            {
                "indicador": indicador,
                "coluna_origem": coluna,
                "contagem": int(serie.notna().sum()),
                "mínimo": _serializar(serie.min()),
                "máximo": _serializar(serie.max()),
                "média": _serializar(serie.mean()),
                "mediana": _serializar(serie.median()),
                "fora_0_10": int(((serie < 0) | (serie > 10)).sum()),
            }
        )
    return pd.DataFrame(linhas)


def detectar_colunas_especiais(df: pd.DataFrame) -> dict[str, list[str]]:
    """Sinaliza identificação, targets candidatos e leakage potencial."""
    colunas = set(df.columns)
    identificacao = [c for c in COLUNAS_IDENTIFICACAO if c in colunas]
    targets = [c for c in COLUNAS_TARGET_CANDIDATAS if c in colunas]
    mapa = {normalizar_nome_coluna(c): c for c in df.columns}
    leakage = []
    for nome in ("ian", "defasagem", "fase_ideal", "inde", "pedra"):
        if nome in mapa:
            leakage.append(mapa[nome])
    leakage.extend(c for c in df.columns if c.lower().startswith("flag_") and "fora" not in c.lower())
    return {
        "identificacao_ou_quase_identificacao": sorted(set(identificacao)),
        "targets_candidatos": sorted(set(targets)),
        "leakage_potencial_dependente_do_target": sorted(set(leakage)),
    }


def validar_dataframe(df: pd.DataFrame, nome: str) -> dict[str, Any]:
    """Executa a auditoria estrutural completa de um DataFrame."""
    perfil = perfil_colunas(df)
    indicadores = estatisticas_indicadores(df)
    return {
        "nome": nome,
        "linhas": int(df.shape[0]),
        "colunas": int(df.shape[1]),
        "nomes_colunas": list(map(str, df.columns)),
        "duplicidades_linha_completa": int(df.duplicated().sum()),
        "colunas_totalmente_nulas": perfil.loc[
            perfil["percentual_nulos"] == 100, "coluna"
        ].tolist(),
        "colunas_constantes": [
            c for c in df.columns if df[c].nunique(dropna=False) <= 1
        ],
        "perfil_colunas": perfil.to_dict(orient="records"),
        "estatisticas_indicadores": indicadores.to_dict(orient="records"),
        **detectar_colunas_especiais(df),
    }


def comparar_bases(original: pd.DataFrame, processada: pd.DataFrame) -> dict[str, Any]:
    """Compara estrutura e nulos entre base original e processada."""
    mapa_original = {_normalizar_para_comparacao_2024(c): c for c in original.columns}
    mapa_processada = {_normalizar_para_comparacao_2024(c): c for c in processada.columns}
    comuns = sorted(set(mapa_original) & set(mapa_processada))
    comparacao_nulos = []
    colunas_renomeadas = []
    tipos_alterados = []
    for normalizado in comuns:
        co = mapa_original[normalizado]
        cp = mapa_processada[normalizado]
        comparacao_nulos.append(
            {
                "coluna_original": co,
                "coluna_processada": cp,
                "nulos_original": int(original[co].isna().sum()),
                "nulos_processada": int(processada[cp].isna().sum()),
            }
        )
        if co != cp:
            colunas_renomeadas.append({"de": co, "para": cp})
        if str(original[co].dtype) != str(processada[cp].dtype):
            tipos_alterados.append(
                {
                    "coluna_original": co,
                    "tipo_original": str(original[co].dtype),
                    "coluna_processada": cp,
                    "tipo_processada": str(processada[cp].dtype),
                }
            )
    return {
        "linhas_antes": int(original.shape[0]),
        "linhas_depois": int(processada.shape[0]),
        "diferenca_linhas": int(processada.shape[0] - original.shape[0]),
        "colunas_antes": int(original.shape[1]),
        "colunas_depois": int(processada.shape[1]),
        "colunas_removidas": [mapa_original[c] for c in sorted(set(mapa_original) - set(mapa_processada))],
        "colunas_criadas": [mapa_processada[c] for c in sorted(set(mapa_processada) - set(mapa_original))],
        "colunas_renomeadas": colunas_renomeadas,
        "tipos_alterados": tipos_alterados,
        "comparacao_nulos": comparacao_nulos,
    }


def executar_auditoria(
    base_original: str | Path,
    base_processada: str | Path,
    planilha: str = "PEDE2024",
) -> dict[str, Any]:
    """Carrega, valida e compara as duas bases indicadas."""
    original = carregar_tabela(base_original, planilha=planilha)
    processada = carregar_tabela(base_processada)
    return {
        "original": validar_dataframe(original, f"original:{planilha}"),
        "processada": validar_dataframe(processada, "processada"),
        "comparacao": comparar_bases(original, processada),
        "observacao": "Relatório somente leitura; nenhuma base foi alterada.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita bases do Datathon Passos Mágicos.")
    parser.add_argument("--original", required=True, help="Caminho do XLSX original.")
    parser.add_argument("--processada", required=True, help="Caminho do CSV processado.")
    parser.add_argument("--planilha", default="PEDE2024", help="Planilha do XLSX a comparar.")
    parser.add_argument("--saida", help="JSON opcional. Não use um caminho de base existente.")
    args = parser.parse_args()
    relatorio = executar_auditoria(args.original, args.processada, args.planilha)
    conteudo = json.dumps(relatorio, ensure_ascii=False, indent=2, default=_serializar)
    if args.saida:
        Path(args.saida).write_text(conteudo, encoding="utf-8")
        print(f"Relatório salvo em {args.saida}")
    else:
        print(conteudo)


if __name__ == "__main__":
    main()
