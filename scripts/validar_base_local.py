"""Valida localmente a base autorizada, sem imprimir registros individuais."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from zipfile import BadZipFile

import pandas as pd


ARQUIVO_ESPERADO = Path("data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx")
ABAS_ESPERADAS = ("PEDE2022", "PEDE2023", "PEDE2024")

COLUNAS_ESSENCIAIS = {
    "PEDE2022": {
        "RA", "Fase", "Turma", "Nome", "Ano nasc", "Idade 22", "Gênero",
        "Ano ingresso", "Instituição de ensino", "INDE 22", "Pedra 22",
        "IAA", "IEG", "IPS", "IDA", "Matem", "Portug", "IPV", "IAN",
        "Fase ideal", "Defas",
    },
    "PEDE2023": {
        "RA", "Fase", "Turma", "Nome Anonimizado", "Data de Nasc", "Idade",
        "Gênero", "Ano ingresso", "Instituição de ensino", "INDE 2023",
        "Pedra 2023", "IAA", "IEG", "IPS", "IPP", "IDA", "Mat", "Por",
        "IPV", "IAN", "Fase Ideal", "Defasagem",
    },
    "PEDE2024": {
        "RA", "Fase", "Turma", "Nome Anonimizado", "Data de Nasc", "Idade",
        "Gênero", "Ano ingresso", "Instituição de ensino", "INDE 2024",
        "Pedra 2024", "IAA", "IEG", "IPS", "IPP", "IDA", "Mat", "Por",
        "IPV", "IAN", "Fase Ideal", "Defasagem",
    },
}


def localizar_raiz_projeto() -> Path:
    return Path(__file__).resolve().parents[1]


def calcular_sha256(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def validar() -> int:
    caminho = localizar_raiz_projeto() / ARQUIVO_ESPERADO
    erros: list[str] = []

    print("Validação local da base educacional")
    print(f"Caminho esperado: {ARQUIVO_ESPERADO.as_posix()}")

    if not caminho.is_file():
        print(
            "ERRO: arquivo não encontrado. Solicite acesso autorizado à "
            "organização responsável e copie o arquivo para o caminho acima."
        )
        print("O projeto não realiza download automático da base.")
        return 1

    if caminho.suffix.lower() != ".xlsx":
        print("ERRO: a base deve possuir extensão .xlsx.")
        return 1

    try:
        with caminho.open("rb") as arquivo:
            arquivo.read(1)
    except OSError as erro:
        print(f"ERRO: o arquivo não está legível: {erro}")
        return 1

    try:
        excel = pd.ExcelFile(caminho, engine="openpyxl")
    except (OSError, ValueError, ImportError, BadZipFile) as erro:
        print(f"ERRO: não foi possível abrir o XLSX: {erro}")
        print("Confirme que o arquivo não está corrompido e instale requirements.txt.")
        return 1

    ausentes = [aba for aba in ABAS_ESPERADAS if aba not in excel.sheet_names]
    if ausentes:
        erros.append("Abas ausentes: " + ", ".join(ausentes))

    dimensoes: dict[str, tuple[int, int]] = {}
    for aba in ABAS_ESPERADAS:
        if aba not in excel.sheet_names:
            continue
        try:
            quadro = pd.read_excel(excel, sheet_name=aba)
        except (OSError, ValueError) as erro:
            erros.append(f"Aba {aba} não pôde ser lida: {erro}")
            continue
        dimensoes[aba] = quadro.shape
        colunas_ausentes = sorted(COLUNAS_ESSENCIAIS[aba] - set(quadro.columns))
        if colunas_ausentes:
            erros.append(
                f"Colunas essenciais ausentes em {aba}: "
                + ", ".join(colunas_ausentes)
            )

    if erros:
        print("VALIDAÇÃO REPROVADA")
        for erro in erros:
            print(f"- {erro}")
        print("Confirme se recebeu a versão esperada da base com a organização.")
        return 1

    print("VALIDAÇÃO APROVADA")
    print("Dimensões agregadas:")
    for aba in ABAS_ESPERADAS:
        linhas, colunas = dimensoes[aba]
        print(f"- {aba}: {linhas} linhas x {colunas} colunas")
    print(f"SHA-256 local: {calcular_sha256(caminho)}")
    print("Nenhum registro individual foi exibido e nenhum arquivo foi modificado.")
    return 0


if __name__ == "__main__":
    sys.exit(validar())
