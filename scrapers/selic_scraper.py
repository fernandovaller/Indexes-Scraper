#!/usr/bin/env python3
"""Scraper específico para SELIC.

A página SELIC tem estrutura diferente dos outros índices:
- Não tem tabela dos últimos 12 meses
- Não tem blockquote com valor atual
- Apenas tabela histórica anual com meses
- Precisa clicar em "Ver tabela completa" para carregar todos os anos

Sobrescreve apenas os hooks necessários do BaseScraper:
- _carregar_pagina: clica em "Ver tabela completa" após carregar
- _extrair_valor_atual: SELIC não tem blockquote
- _extrair_tabela_ultimos_meses: calcula a partir do histórico (faz cache)
- _extrair_historico: usa a primeira tabela (índice 0) e retorna cache
- _print_resumo: log específico para formato SELIC
"""

import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

sys.path.insert(0, str(Path(__file__).parent))
from base_scraper import BaseScraper

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import URLS, TITULOS, OUTPUT_FILES

logger = logging.getLogger(__name__)

MESES_ORDENADOS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


class SELICScraper(BaseScraper):
    """Scraper específico para SELIC."""

    def __init__(self):
        super().__init__(
            url=URLS["selic"],
            titulo_padrao=TITULOS["selic"],
            arquivo_saida=OUTPUT_FILES["selic"],
        )
        self._historico_cache: dict | None = None

    def _carregar_pagina(self) -> None:
        """Carrega a página e clica em "Ver tabela completa" para expandir histórico."""
        self.driver.get(self.url)
        self._wait_for((By.CSS_SELECTOR, "table.table-hover"))

        try:
            btn_completa = self.driver.find_element(By.ID, "btnTabelaCompleta")
            btn_completa.click()
            logger.info("Carregando tabela completa...")
            self._wait_for((By.CSS_SELECTOR, "table.table-hover tbody tr"))
        except Exception as e:
            logger.warning(f"Botão tabela completa não encontrado ou erro: {e}")

    def _extrair_valor_atual(self, soup) -> str:
        """SELIC não tem blockquote com valor atual."""
        return ""

    def _extrair_tabela_ultimos_meses(self, soup) -> list:
        """SELIC não tem tabela de 12 meses separada.

        Extrai o histórico completo da primeira tabela (índice 0), armazena
        em cache para reuso em _extrair_historico, e calcula os últimos 12
        meses a partir dele.
        """
        historico = self._extrair_tabela_historica(soup, indice_tabela=0)
        self._historico_cache = historico
        logger.info(f"Extraído histórico SELIC: {len(historico)} anos")
        return self._calcular_ultimos_12_meses(historico)

    def _extrair_historico(self, soup) -> dict:
        """Retorna o histórico já extraído em _extrair_tabela_ultimos_meses.

        Se o cache não existir (chamada direta sem passar pelos 12 meses),
        extrai da primeira tabela.
        """
        if self._historico_cache is not None:
            return self._historico_cache
        dados = self._extrair_tabela_historica(soup, indice_tabela=0)
        logger.info(f"Extraído histórico SELIC: {len(dados)} anos")
        return dados

    def _calcular_ultimos_12_meses(self, historico: dict) -> list:
        """Calcula os últimos 12 meses a partir do histórico anual.

        Retorna lista no formato: [{"data": "Jun/2026", "taxa": 13.25}, ...]
        Ordenado do mais recente para o mais antigo.
        """
        if not historico:
            return []

        ultimos_12 = []
        meses_coletados = 0

        for ano in sorted(historico.keys(), reverse=True):
            if meses_coletados >= 12:
                break

            dados_ano = historico.get(ano, {})
            for mes in reversed(MESES_ORDENADOS):
                if mes in dados_ano:
                    ultimos_12.append({
                        "data": f"{mes}/{ano}",
                        "taxa": dados_ano[mes]
                    })
                    meses_coletados += 1
                    if meses_coletados >= 12:
                        break

        return list(reversed(ultimos_12))

    def _print_resumo(self, ultimos_meses: list, historico: dict) -> None:
        """Mostra resumo da extração SELIC."""
        if historico:
            anos = sorted(historico.keys())
            logger.info(f"Histórico SELIC: {len(historico)} anos (de {anos[0]} a {anos[-1]})")
            meses_recente = len(historico[anos[-1]])
            logger.info(f"  - Ano mais recente ({anos[-1]}): {meses_recente} meses com dados")

        if ultimos_meses:
            logger.info(f"Últimos 12 meses: {len(ultimos_meses)} registros")
            logger.info(f"  - Mais antigo: {ultimos_meses[0]['data']}")
            logger.info(f"  - Mais recente: {ultimos_meses[-1]['data']}")


def run_selic(driver=None) -> bool:
    """Função para executar scraper SELIC."""
    scraper = SELICScraper()
    return scraper.run(driver)


if __name__ == "__main__":
    run_selic()