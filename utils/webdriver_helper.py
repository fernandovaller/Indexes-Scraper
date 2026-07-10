#!/usr/bin/env python3
"""Funções utilitárias para web scraping."""

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def configurar_driver():
    """Configura o Chrome em modo headless.

    Configurável via env vars:
    - INDEXES_HEADLESS: "true" (padrão) ou "false"
    - INDEXES_USER_AGENT: string do user agent
    """
    chrome_options = Options()

    headless = os.environ.get("INDEXES_HEADLESS", "true").lower() == "true"
    if headless:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    user_agent = os.environ.get("INDEXES_USER_AGENT", DEFAULT_USER_AGENT)
    chrome_options.add_argument(f"user-agent={user_agent}")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def parse_porcentagem(valor_str: str) -> float | None:
    """Converte string de porcentagem para float."""
    valor_str = valor_str.strip().replace("%", "").replace(",", ".")
    try:
        return float(valor_str)
    except ValueError:
        return None
