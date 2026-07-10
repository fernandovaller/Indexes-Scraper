#!/usr/bin/env python3
"""Configurações do projeto."""

from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# Garante que diretório de saída existe
OUTPUT_DIR.mkdir(exist_ok=True)

# URLs dos índices
URLS = {
    "igpdi": "https://www.debit.com.br/tabelas/igp-fgv-indice-geral-de-precos",
    "igpm": "https://www.debit.com.br/tabelas/igpm-fgv-indice-geral-de-precos-mercado",
    "inccdi": "https://www.debit.com.br/tabelas/incc-indice-nacional-da-construcao-civil",
    "inpc": "https://www.debit.com.br/tabelas/inpc-indice-nacional-de-precos-ao-consumidor",
    "ipca": "https://www.debit.com.br/tabelas/ipca-indice-nacional-de-precos-ao-consumidor-amplo",
    "ivar": "https://www.debit.com.br/tabelas/ivar-indice-variacao-de-alugueis-residenciais",
    "selic": "https://www.debit.com.br/tabelas/selic",
}

# Títulos padrão
TITULOS = {
    "igpdi": "IGP-DI - FGV",
    "igpm": "IGP-M - FGV",
    "inccdi": "INCC-DI - FGV",
    "inpc": "INPC - IBGE",
    "ipca": "IPCA - IBGE",
    "ivar": "IVAR - FGV",
    "selic": "SELIC - Banco Central",
}

# Arquivos de saída
OUTPUT_FILES = {
    "igpdi": OUTPUT_DIR / "igpdi_fgv.json",
    "igpm": OUTPUT_DIR / "igpm_fgv.json",
    "inccdi": OUTPUT_DIR / "inccdi_fgv.json",
    "inpc": OUTPUT_DIR / "inpc.json",
    "ipca": OUTPUT_DIR / "ipca.json",
    "ivar": OUTPUT_DIR / "ivar_fgv.json",
    "selic": OUTPUT_DIR / "selic.json",
}
