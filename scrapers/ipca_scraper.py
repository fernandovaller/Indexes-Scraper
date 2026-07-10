#!/usr/bin/env python3
"""Scraper para IPCA."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class IPCAScraper(BaseScraper):
    """Scraper para IPCA."""

    def __init__(self):
        super().__init__(
            url=URLS["ipca"],
            titulo_padrao=TITULOS["ipca"],
            arquivo_saida=OUTPUT_FILES["ipca"],
        )


def run_ipca() -> bool:
    """Função para executar scraper IPCA."""
    scraper = IPCAScraper()
    return scraper.run()


if __name__ == "__main__":
    run_ipca()
