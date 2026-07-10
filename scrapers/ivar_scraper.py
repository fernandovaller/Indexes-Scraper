#!/usr/bin/env python3
"""Scraper para IVAR."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class IVARScraper(BaseScraper):
    """Scraper para IVAR - Índice de Variação de Aluguéis Residenciais."""

    def __init__(self):
        super().__init__(
            url=URLS["ivar"],
            titulo_padrao=TITULOS["ivar"],
            arquivo_saida=OUTPUT_FILES["ivar"],
        )


def run_ivar() -> bool:
    """Função para executar scraper IVAR."""
    scraper = IVARScraper()
    return scraper.run()


if __name__ == "__main__":
    run_ivar()
