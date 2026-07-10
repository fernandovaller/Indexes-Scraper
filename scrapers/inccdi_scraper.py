#!/usr/bin/env python3
"""Scraper para INCC-DI."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class INCCDIScraper(BaseScraper):
    """Scraper para INCC-DI."""

    def __init__(self):
        super().__init__(
            url=URLS["inccdi"],
            titulo_padrao=TITULOS["inccdi"],
            arquivo_saida=OUTPUT_FILES["inccdi"],
        )


def run_inccdi() -> bool:
    """Função para executar scraper INCC-DI."""
    scraper = INCCDIScraper()
    return scraper.run()


if __name__ == "__main__":
    run_inccdi()
