#!/usr/bin/env python3
"""Scraper para INPC."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class INPCScraper(BaseScraper):
    """Scraper para INPC."""

    def __init__(self):
        super().__init__(
            url=URLS["inpc"],
            titulo_padrao=TITULOS["inpc"],
            arquivo_saida=OUTPUT_FILES["inpc"],
        )


def run_inpc(driver=None) -> bool:
    """Função para executar scraper INPC."""
    scraper = INPCScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_inpc()
