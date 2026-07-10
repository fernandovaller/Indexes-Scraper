#!/usr/bin/env python3
"""Scraper específico para SELIC.

A página SELIC tem estrutura diferente dos outros índices:
- Não tem tabela dos últimos 12 meses
- Não tem blockquote com valor atual
- Apenas tabela histórica anual com meses
- Precisa clicar em "Ver tabela completa" para carregar todos os anos
"""

import json
import logging
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

sys.path.insert(0, str(Path(__file__).parent))
from base_scraper import BaseScraper

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import URLS, TITULOS, OUTPUT_FILES
from utils import configurar_driver, parse_porcentagem

logger = logging.getLogger(__name__)


class SELICScraper(BaseScraper):
    """Scraper específico para SELIC."""

    def __init__(self):
        super().__init__(
            url=URLS["selic"],
            titulo_padrao=TITULOS["selic"],
            arquivo_saida=OUTPUT_FILES["selic"],
        )

    def run(self) -> bool:
        """Executa o scraper SELIC com lógica específica."""
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

            # Clicar no botão "Ver tabela completa" para carregar todos os anos
            try:
                btn_completa = self.driver.find_element(By.ID, "btnTabelaCompleta")
                btn_completa.click()
                logger.info("Carregando tabela completa...")
                time.sleep(3)  # Aguardar carregamento
            except Exception as e:
                logger.warning(f"Botão tabela completa não encontrado ou erro: {e}")

            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            titulo = self._extrair_titulo(soup)
            
            # Extrair histórico completo
            historico = self._extrair_historico_selic(soup)
            
            # Gerar últimos 12 meses a partir do histórico
            ultimos_12_meses = self._calcular_ultimos_12_meses(historico)

            resultado = {
                "fonte": self.url,
                "titulo": titulo,
                "informacao_atual": "",
                "data_coleta": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ultimos_12_meses": ultimos_12_meses,
                "historico": historico,
            }

            self._salvar_json(resultado)
            self._print_resumo_selic(historico, ultimos_12_meses)
            return True

        except Exception as e:
            logger.error(f"Erro durante scraping SELIC: {e}")
            return False

        finally:
            if self.driver:
                self.driver.quit()

    def _extrair_historico_selic(self, soup) -> dict:
        """Extrai tabela histórica específica da SELIC.
        
        A tabela SELIC tem colunas: Ano, Jan, Fev, Mar, Abr, Mai, Jun, Jul, Ago, Set, Out, Nov, Dez
        """
        dados = {}
        
        # Procurar todas as tabelas
        tabelas = soup.find_all("table", class_="table-hover")
        if not tabelas:
            logger.warning("Nenhuma tabela encontrada na página SELIC")
            return dados

        logger.info(f"Encontradas {len(tabelas)} tabela(s)")
        
        # A primeira tabela contém os dados históricos
        tabela = tabelas[0]
        tbodys = tabela.find_all("tbody")
        
        logger.info(f"Encontrados {len(tbodys)} tbody(s)")

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

                # Primeira coluna é o ano
                ano = tds[0].get_text(strip=True)
                if not ano.isdigit():
                    continue

                meses = {}
                # As colunas seguintes são os meses (1-12)
                for i, mes_nome in enumerate(meses_nomes):
                    if i + 1 < len(tds):
                        valor_str = tds[i + 1].get_text(strip=True)
                        if valor_str and valor_str != "-":
                            valor = parse_porcentagem(valor_str)
                            if valor is not None:
                                meses[mes_nome] = valor

                if meses:
                    dados[ano] = meses

        logger.info(f"Extraído histórico SELIC: {len(dados)} anos")
        return dados

    def _calcular_ultimos_12_meses(self, historico: dict) -> list:
        """Calcula os últimos 12 meses a partir do histórico anual.
        
        Retorna lista no formato: [{"data": "Jun/2026", "taxa": 13.25}, ...]
        Ordenado do mais recente para o mais antigo.
        """
        if not historico:
            return []
        
        meses_ordenados = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                          "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        
        ultimos_12 = []
        
        # Pegar anos ordenados
        anos = sorted(historico.keys(), reverse=True)
        
        meses_coletados = 0
        for ano in anos:
            if meses_coletados >= 12:
                break
                
            dados_ano = historico.get(ano, {})
            # Percorrer meses em ordem reversa (Dez -> Jan) para pegar os mais recentes primeiro
            for mes in reversed(meses_ordenados):
                if mes in dados_ano:
                    ultimos_12.append({
                        "data": f"{mes}/{ano}",
                        "taxa": dados_ano[mes]
                    })
                    meses_coletados += 1
                    if meses_coletados >= 12:
                        break
        
        # Inverter para ficar do mais recente para o mais antigo
        return list(reversed(ultimos_12))

    def _print_resumo_selic(self, historico: dict, ultimos_12_meses: list) -> None:
        """Mostra resumo da extração SELIC."""
        if historico:
            anos = sorted(historico.keys())
            logger.info(f"Histórico SELIC: {len(historico)} anos (de {anos[0]} a {anos[-1]})")
            # Mostrar quantos meses tem o ano mais recente
            if anos:
                meses_recente = len(historico[anos[-1]])
                logger.info(f"  - Ano mais recente ({anos[-1]}): {meses_recente} meses com dados")
        
        if ultimos_12_meses:
            logger.info(f"Últimos 12 meses: {len(ultimos_12_meses)} registros")
            # Mostrar primeiro e último
            logger.info(f"  - Mais antigo: {ultimos_12_meses[0]['data']}")
            logger.info(f"  - Mais recente: {ultimos_12_meses[-1]['data']}")


def run_selic() -> bool:
    """Função para executar scraper SELIC."""
    scraper = SELICScraper()
    return scraper.run()


if __name__ == "__main__":
    run_selic()
