#!/usr/bin/env python3
"""Classe base para scrapers de índices econômicos."""

import json
import logging
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from utils import configurar_driver, parse_porcentagem

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base para scrapers de índices do site Debit."""

    def __init__(self, url: str, titulo_padrao: str, arquivo_saida: str | Path):
        self.url = url
        self.titulo_padrao = titulo_padrao
        self.arquivo_saida = Path(arquivo_saida)
        self.driver = None

    def run(self) -> bool:
        """Executa o scraper completo."""
        logger.info(f"Acessando: {self.url}")

        try:
            self.driver = configurar_driver()
        except Exception as e:
            logger.error(f"Erro ao configurar ChromeDriver: {e}")
            return False

        try:
            self.driver.get(self.url)
            self.driver.implicitly_wait(10)
            time.sleep(3)

            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            titulo = self._extrair_titulo(soup)
            valor_atual = self._extrair_valor_atual(soup)
            ultimos_meses = self._extrair_tabela_ultimos_meses(soup)
            historico = self._extrair_historico(soup)

            resultado = {
                "fonte": self.url,
                "titulo": titulo,
                "informacao_atual": valor_atual,
                "data_coleta": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ultimos_12_meses": ultimos_meses,
                "historico": historico,
            }

            self._salvar_json(resultado)
            self._print_resumo(ultimos_meses, historico)
            return True

        except Exception as e:
            logger.error(f"Erro durante scraping: {e}")
            return False

        finally:
            if self.driver:
                self.driver.quit()

    def _extrair_titulo(self, soup) -> str:
        """Extrai título da página."""
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else self.titulo_padrao

    def _extrair_valor_atual(self, soup) -> str:
        """Extrai informação de valor atual."""
        blockquote = soup.find("blockquote", class_="blockquote")
        return blockquote.get_text(strip=True) if blockquote else ""

    def _extrair_historico(self, soup) -> dict:
        """Extrai dados históricos completos."""
        try:
            btn_completa = self.driver.find_element(By.ID, "btnTabelaCompleta")
            btn_completa.click()
            time.sleep(3)
            html_completo = self.driver.page_source
            soup_completo = BeautifulSoup(html_completo, "html.parser")
            logger.info("Extraindo tabela histórica completa...")
            return self._extrair_tabela_historica(soup_completo)
        except Exception as e:
            logger.warning(f"Não foi possível carregar tabela completa: {e}")
            return self._extrair_tabela_historica(soup)

    def _extrair_tabela_ultimos_meses(self, soup) -> list:
        """Extrai a tabela dos últimos 12 meses."""
        dados = []
        tabela = soup.find("table", class_="table-hover")
        if not tabela:
            logger.warning("Tabela dos últimos 12 meses não encontrada.")
            return dados

        tbody = tabela.find("tbody")
        if not tbody:
            return dados

        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 4:
                dados.append({
                    "data": tds[0].get_text(strip=True),
                    "variacao": parse_porcentagem(tds[1].get_text(strip=True)),
                    "variacao_periodo": parse_porcentagem(tds[2].get_text(strip=True)),
                    "acumulado_12_meses": parse_porcentagem(tds[3].get_text(strip=True)),
                })

        return dados

    def _extrair_tabela_historica(self, soup) -> dict:
        """Extrai a tabela histórica completa."""
        dados = {}
        tabelas = soup.find_all("table", class_="table-hover")
        if len(tabelas) < 2:
            logger.warning("Tabela histórica não encontrada.")
            return dados

        tabela = tabelas[1]
        tbodys = tabela.find_all("tbody")

        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                       "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        for tbody in tbodys:
            rows = tbody.find_all("tr")
            if not rows:
                continue

            for tr in rows:
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue

                ano = tds[0].get_text(strip=True)
                if not ano.isdigit():
                    continue

                meses = {}
                for i, mes_nome in enumerate(meses_nomes):
                    if i + 1 < len(tds):
                        valor_str = tds[i + 1].get_text(strip=True)
                        if valor_str and valor_str != "-":
                            valor = parse_porcentagem(valor_str)
                            if valor is not None:
                                meses[mes_nome] = valor

                if meses:
                    dados[ano] = meses

        return dados

    def _salvar_json(self, dados: dict) -> None:
        """Salva dados em JSON."""
        self.arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        with open(self.arquivo_saida, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        logger.info(f"Dados salvos em: {self.arquivo_saida}")

    def _print_resumo(self, ultimos_meses: list, historico: dict) -> None:
        """Mostra resumo da extração."""
        logger.info(f"Últimos 12 meses: {len(ultimos_meses)} registros")
        if historico:
            anos = sorted(historico.keys())
            logger.info(f"Histórico: {len(historico)} anos (de {anos[0]} a {anos[-1]})")
