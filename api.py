#!/usr/bin/env python3
"""API FastAPI para servir os índices econômicos coletados.

Uso:
    uvicorn api:app --reload

Endpoints:
    GET /               — Lista todos os índices disponíveis
    GET /indices        — Lista todos os índices com metadados
    GET /{indice}       — Dados completos de um índice
    GET /{indice}/atual — Valor atual / informação mais recente
    GET /{indice}/12meses — Últimos 12 meses
    GET /{indice}/historico — Histórico completo por ano
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import OUTPUT_FILES, TITULOS, URLS

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Indexes Scraper API",
    description="API para consulta de índices econômicos brasileiros coletados do site Debit",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _carregar_indice(nome: str) -> dict:
    """Carrega JSON de um índice do disco."""
    if nome not in OUTPUT_FILES:
        raise HTTPException(status_code=404, detail=f"Índice '{nome}' não encontrado")

    caminho = Path(OUTPUT_FILES[nome])
    if not caminho.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dados do índice '{nome}' ainda não coletados. "
            f"Execute: python main.py {nome}",
        )

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao ler dados do índice '{nome}': {e}",
        )


@app.get("/")
def root():
    """Endpoint raiz com informações da API."""
    return {
        "api": "Indexes Scraper API",
        "version": "1.0.0",
        "indices_disponiveis": list(OUTPUT_FILES.keys()),
        "endpoints": {
            "/indices": "Lista todos os índices",
            "/{indice}": "Dados completos de um índice",
            "/{indice}/atual": "Informação atual do índice",
            "/{indice}/12meses": "Últimos 12 meses",
            "/{indice}/historico": "Histórico completo",
        },
        "timestamp": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
    }


@app.get("/indices")
def listar_indices():
    """Lista todos os índices disponíveis com metadados."""
    indices = []
    for nome in OUTPUT_FILES:
        caminho = Path(OUTPUT_FILES[nome])
        coletado = caminho.exists()
        indices.append({
            "id": nome,
            "titulo": TITULOS.get(nome, nome),
            "fonte": URLS.get(nome, ""),
            "coletado": coletado,
            "arquivo": str(caminho.name),
        })
    return {
        "total": len(indices),
        "indices": indices,
        "timestamp": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(),
    }


@app.get("/{indice}")
def dados_completos(indice: str):
    """Retorna todos os dados de um índice."""
    return _carregar_indice(indice)


@app.get("/{indice}/atual")
def informacao_atual(indice: str):
    """Retorna a informação atual (valor mais recente) do índice."""
    dados = _carregar_indice(indice)
    return {
        "indice": indice,
        "titulo": dados.get("titulo", ""),
        "informacao_atual": dados.get("informacao_atual", ""),
        "data_coleta": dados.get("data_coleta", ""),
    }


@app.get("/{indice}/12meses")
def ultimos_12_meses(indice: str):
    """Retorna os últimos 12 meses de um índice."""
    dados = _carregar_indice(indice)
    return {
        "indice": indice,
        "titulo": dados.get("titulo", ""),
        "ultimos_12_meses": dados.get("ultimos_12_meses", []),
        "data_coleta": dados.get("data_coleta", ""),
    }


@app.get("/{indice}/historico")
def historico(indice: str, ano: str | None = None):
    """Retorna o histórico completo de um índice, opcionalmente filtrado por ano."""
    dados = _carregar_indice(indice)
    hist = dados.get("historico", {})

    if ano:
        if ano not in hist:
            raise HTTPException(
                status_code=404,
                detail=f"Ano {ano} não encontrado no histórico de '{indice}'",
            )
        return {
            "indice": indice,
            "ano": ano,
            "meses": hist[ano],
        }

    return {
        "indice": indice,
        "titulo": dados.get("titulo", ""),
        "historico": hist,
        "total_anos": len(hist),
    }


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("INDEXES_API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)