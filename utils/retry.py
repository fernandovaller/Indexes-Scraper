#!/usr/bin/env python3
"""Decorator de retry com backoff exponencial."""

import functools
import logging
import time
from typing import Callable, Type

logger = logging.getLogger(__name__)

ExceptionTypes = Type[Exception] | tuple[Type[Exception], ...]


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    exceptions: ExceptionTypes = Exception,
    on_retry: Callable[[Exception, int, int], None] | None = None,
):
    """Decorator de retry com backoff exponencial.

    Args:
        max_attempts: Numero maximo de tentativas (incluindo a primeira).
        base_delay: Atraso inicial em segundos.
        max_delay: Atraso maximo em segundos (cap).
        backoff_factor: Multiplicador do atraso a cada tentativa.
        exceptions: Tipo(s) de excecao que disparam retry.
        on_retry: Callback opcional (excecao, tentativa_atual, max_tentativas).

    Returns:
        Decorador aplicavel a funcoes/metodos.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"{func.__name__} falhou apos {attempt} tentativas: {e}"
                        )
                        raise
                    if on_retry:
                        on_retry(e, attempt, max_attempts)
                    logger.warning(
                        f"{func.__name__} tentativa {attempt}/{max_attempts} falhou: {e}. "
                        f"Tentando novamente em {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                    attempt += 1
        return wrapper
    return decorator