#!/usr/bin/env python3
"""
Entry point para executar todos os scrapers de índices econômicos.

Uso:
    python main.py              # Executa todos os scrapers (sequencial)
    python main.py igpm         # Executa apenas IGP-M
    python main.py inpc ipca    # Executa INPC e IPCA
    python main.py --parallel   # Executa todos em paralelo (1 driver cada)
"""

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers import SCRAPERS
from utils import configurar_driver, setup_logging

setup_logging()
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


def _run_parallel(scraper_funcs: dict, names: list[str], max_workers: int | None = None) -> dict:
    """Executa scrapers em paralelo (1 WebDriver por scraper).

    Args:
        scraper_funcs: Dict {nome: função_run}.
        names: Nomes dos scrapers a executar.
        max_workers: Máximo de threads. Se None, usa min(len(names), 5).

    Returns:
        Dict {nome: sucesso (bool)}.
    """
    if max_workers is None:
        max_workers = min(len(names), 5)

    logger.info(f"Executando {len(names)} scrapers em paralelo (max {max_workers} threads)")

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {
            executor.submit(scraper_funcs[name]): name
            for name in names
        }
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                logger.error(f"Erro ao executar {name}: {e}")
                results[name] = False

    return results


def run_all(parallel: bool = False) -> bool:
    """Executa todos os scrapers.

    Args:
        parallel: Se True, executa em paralelo (1 driver por scraper).
    """
    logger.info("=" * 50)
    mode = "paralelo" if parallel else "sequencial"
    logger.info(f"Executando todos os scrapers ({mode})")
    logger.info("=" * 50)

    if parallel:
        results = _run_parallel(SCRAPERS, list(SCRAPERS.keys()))
    else:
        results = _run_with_shared_driver(SCRAPERS, list(SCRAPERS.keys()))
    _print_resumo(results)
    return all(results.values())


def run_specific(names: list[str], parallel: bool = False) -> bool:
    """Executa scrapers específicos.

    Args:
        names: Lista de nomes de scrapers.
        parallel: Se True, executa em paralelo.
    """
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
        if parallel and len(valid_names) > 1:
            shared_results = _run_parallel(SCRAPERS, valid_names)
        else:
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
        description="Scrapers para índices econômicos (IGP-M, INPC, IPCA, etc)"
    )
    parser.add_argument(
        "indices",
        nargs="*",
        help="Índices a serem executados. Se vazio, executa todos.",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Executa scrapers em paralelo (1 Chrome por scraper). "
        "Mais rápido, porém usa mais memória.",
    )
    parser.add_argument(
        "--log-format",
        choices=["text", "json"],
        default=None,
        help="Formato de log. Padrão: text (ou env INDEXES_LOG_FORMAT).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nível de log. Padrão: INFO.",
    )

    args = parser.parse_args()

    if args.log_format:
        setup_logging(level=args.log_level, log_format=args.log_format)
    elif args.log_level != "INFO":
        setup_logging(level=args.log_level)

    if not args.indices:
        success = run_all(parallel=args.parallel)
    else:
        success = run_specific(args.indices, parallel=args.parallel)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
