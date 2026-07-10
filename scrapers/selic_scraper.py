#!/usr/bin/env python3
"""Scraper para SELIC."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class SELICScraper(BaseScraper):
    """Scraper para SELIC - Taxa Básica de Juros."""

    def __init__(self):
        super().__init__(
            url=URLS["selic"],
            titulo_padrao=TITULOS["selic"],
            arquivo_saida=OUTPUT_FILES["selic"],
        )


def run_selic() -> bool:
    """Função para executar scraper SELIC."""
    scraper = SELICScraper()
    return scraper.run()


if __name__ == "__main__":
    run_selic()
