#!/usr/bin/env python3
"""
Entry point para executar todos os scrapers de índices econômicos.

Uso:
    python main.py              # Executa todos os scrapers
    python main.py igpm         # Executa apenas IGP-M
    python main.py inpc ipca    # Executa INPC e IPCA
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers import SCRAPERS
from utils import configurar_driver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _run_with_shared_driver(scraper_funcs: dict, names: list[str]) -> dict:
    """Executa scrapers reusando uma única instância do WebDriver.

    Args:
        scraper_funcs: Dict {nome: função_run}.
        names: Ordem dos nomes a executar.

    Returns:
        Dict {nome: sucesso (bool)}.
    """
    results = {}
    try:
        driver = configurar_driver()
    except Exception as e:
        logger.error(f"Erro ao configurar ChromeDriver: {e}")
        for name in names:
            results[name] = False
        return results

    try:
        for name in names:
            logger.info(f"\n{'='*50}")
            logger.info(f"Scraper: {name.upper()}")
            logger.info("=" * 50)
            try:
                results[name] = scraper_funcs[name](driver)
            except Exception as e:
                logger.error(f"Erro ao executar {name}: {e}")
                results[name] = False
    finally:
        driver.quit()

    return results


def run_all() -> bool:
    """Executa todos os scrapers."""
    logger.info("=" * 50)
    logger.info("Executando todos os scrapers")
    logger.info("=" * 50)

    results = _run_with_shared_driver(SCRAPERS, list(SCRAPERS.keys()))
    _print_resumo(results)
    return all(results.values())


def run_specific(names: list[str]) -> bool:
    """Executa scrapers específicos."""
    results = {}
    valid_names = []
    for name in names:
        if name not in SCRAPERS:
            logger.error(f"Scraper desconhecido: {name}")
            logger.info(f"Disponíveis: {', '.join(SCRAPERS.keys())}")
            results[name] = False
            continue
        valid_names.append(name)

    if valid_names:
        shared_results = _run_with_shared_driver(SCRAPERS, valid_names)
        results.update(shared_results)

    _print_resumo(results)
    return all(results.values())


def _print_resumo(results: dict[str, bool]) -> None:
    """Mostra resumo dos resultados."""
    logger.info(f"\n{'='*50}")
    logger.info("RESUMO")
    logger.info("=" * 50)
    for name, success in results.items():
        status = "OK" if success else "FALHOU"
        logger.info(f"  {name.upper()}: {status}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrapers para índices econômicos (IGP-M, INPC, IPCA)"
    )
    parser.add_argument(
        "indices",
        nargs="*",
        help="Índices a serem executados (igpm, inpc, ipca). Se vazio, executa todos.",
    )

    args = parser.parse_args()

    if not args.indices:
        success = run_all()
    else:
        success = run_specific(args.indices)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
