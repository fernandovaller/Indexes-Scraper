#!/usr/bin/env python3
"""Scraper para IGP-DI."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class IGPDIScraper(BaseScraper):
    """Scraper para IGP-DI."""

    def __init__(self):
        super().__init__(
            url=URLS["igpdi"],
            titulo_padrao=TITULOS["igpdi"],
            arquivo_saida=OUTPUT_FILES["igpdi"],
        )


def run_igpdi(driver=None) -> bool:
    """Função para executar scraper IGP-DI."""
    scraper = IGPDIScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_igpdi()
