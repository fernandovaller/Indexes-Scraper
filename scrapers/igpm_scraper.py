#!/usr/bin/env python3
"""Scraper para IGP-M."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class IGPMScraper(BaseScraper):
    """Scraper para IGP-M."""

    def __init__(self):
        super().__init__(
            url=URLS["igpm"],
            titulo_padrao=TITULOS["igpm"],
            arquivo_saida=OUTPUT_FILES["igpm"],
        )


def run_igpm() -> bool:
    """Função para executar scraper IGP-M."""
    scraper = IGPMScraper()
    return scraper.run()


if __name__ == "__main__":
    run_igpm()
