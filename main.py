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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_all() -> bool:
    """Executa todos os scrapers."""
    logger.info("=" * 50)
    logger.info("Executando todos os scrapers")
    logger.info("=" * 50)

    results = {}
    for name, scraper_func in SCRAPERS.items():
        logger.info(f"\n{'='*50}")
        logger.info(f"Scraper: {name.upper()}")
        logger.info("=" * 50)
        try:
            results[name] = scraper_func()
        except Exception as e:
            logger.error(f"Erro ao executar {name}: {e}")
            results[name] = False

    _print_resumo(results)
    return all(results.values())


def run_specific(names: list[str]) -> bool:
    """Executa scrapers específicos."""
    results = {}
    for name in names:
        if name not in SCRAPERS:
            logger.error(f"Scraper desconhecido: {name}")
            logger.info(f"Disponíveis: {', '.join(SCRAPERS.keys())}")
            results[name] = False
            continue

        logger.info(f"\n{'='*50}")
        logger.info(f"Scraper: {name.upper()}")
        logger.info("=" * 50)
        try:
            results[name] = SCRAPERS[name]()
        except Exception as e:
            logger.error(f"Erro ao executar {name}: {e}")
            results[name] = False

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
