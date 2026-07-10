#!/usr/bin/env python3
"""Scraper para TR (Taxa Referencial)."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class TRScraper(BaseScraper):
    """Scraper para TR."""

    def __init__(self):
        super().__init__(
            url=URLS["tr"],
            titulo_padrao=TITULOS["tr"],
            arquivo_saida=OUTPUT_FILES["tr"],
        )


def run_tr(driver=None) -> bool:
    """Função para executar scraper TR."""
    scraper = TRScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_tr()