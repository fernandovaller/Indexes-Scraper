#!/usr/bin/env python3
"""Configuração de logging estruturado em JSON.

Suporta dois modos:
- texto (padrão): formato legível para terminal
- json: estrutura JSON para coleta por sistemas de monitoramento

Seleção via env var INDEXES_LOG_FORMAT (text|json) ou parâmetro direto.
"""

import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo


class JsonFormatter(logging.Formatter):
    """Formatter que gera logs em JSON com campos estruturados."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "scraper"):
            log_entry["scraper"] = record.scraper

        if hasattr(record, "url"):
            log_entry["url"] = record.url

        return json.dumps(log_entry, ensure_ascii=False)


TEXT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(level: int | str = logging.INFO, log_format: str | None = None):
    """Configura logging global.

    Args:
        level: Nível de log (logging.INFO, logging.DEBUG, etc).
        log_format: Formato ("text" ou "json"). Se None, lê env var
                   INDEXES_LOG_FORMAT (padrão: text).
    """
    if log_format is None:
        log_format = os.environ.get("INDEXES_LOG_FORMAT", "text")

    root = logging.getLogger()
    root.setLevel(level)

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler()

    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(TEXT_FORMAT))

    root.addHandler(handler)

    logging.getLogger("uvicorn").handlers = [handler]
    logging.getLogger("uvicorn.access").handlers = [handler]