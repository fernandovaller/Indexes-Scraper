#!/usr/bin/env python3
"""Scraper para CDI."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class CDIScraper(BaseScraper):
    """Scraper para CDI."""

    def __init__(self):
        super().__init__(
            url=URLS["cdi"],
            titulo_padrao=TITULOS["cdi"],
            arquivo_saida=OUTPUT_FILES["cdi"],
        )


def run_cdi(driver=None) -> bool:
    """Função para executar scraper CDI."""
    scraper = CDIScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_cdi()