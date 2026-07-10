#!/usr/bin/env python3
"""Scraper para IPC-Fipe."""

from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class IPCFipeScraper(BaseScraper):
    """Scraper para IPC-Fipe."""

    def __init__(self):
        super().__init__(
            url=URLS["ipcfipe"],
            titulo_padrao=TITULOS["ipcfipe"],
            arquivo_saida=OUTPUT_FILES["ipcfipe"],
        )


def run_ipcfipe(driver=None) -> bool:
    """Função para executar scraper IPC-Fipe."""
    scraper = IPCFipeScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_ipcfipe()