#!/usr/bin/env python3
"""Validação de dados: compara JSON novo com anterior e detecta anomalias."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Limiares de detecção de anomalia
THRESHOLD_VARIACAO_ABS = 10.0  # pontos percentuais: |novo - antigo| > 10
THRESHORD_DADOS_VAZIOS = 0  # histórico/12 meses com 0 registros
THRESHOLD_PERDA_ANOS = 0  # histórico com menos anos que anterior


def carregar_json_anterior(caminho: Path) -> dict | None:
    """Carrega JSON anterior se existir. Retorna None se não existir."""
    if not caminho.exists():
        return None
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Erro ao carregar JSON anterior ({caminho}): {e}")
        return None


def validar_dados(
    dados_novos: dict,
    dados_anteriores: dict | None,
    limiar_variacao: float = THRESHOLD_VARIACAO_ABS,
) -> list[str]:
    """Compara dados novos com anteriores e retorna lista de alertas.

    Args:
        dados_novos: Dados recém-extraídos.
        dados_anteriores: Dados do JSON anterior (ou None se primeira coleta).
        limiar_variacao: Diferença absoluta (pontos percentuais) que dispara alerta.

    Returns:
        Lista de mensagens de alerta. Vazia se tudo OK.
    """
    alertas: list[str] = []

    # Verificar dados vazios
    historico_novo = dados_novos.get("historico", {})
    ultimos_novo = dados_novos.get("ultimos_12_meses", [])

    if not historico_novo:
        alertas.append("Histórico vazio — possível falha na extração")
    if not ultimos_novo:
        alertas.append("Últimos 12 meses vazio — possível falha na extração")

    # Primeira coleta: sem comparação
    if dados_anteriores is None:
        logger.info("Primeira coleta — sem dados anteriores para comparar")
        return alertas

    # Comparar histórico: perda de anos
    historico_antigo = dados_anteriores.get("historico", {})
    anos_antigos = set(historico_antigo.keys())
    anos_novos = set(historico_novo.keys())
    anos_perdidos = anos_antigos - anos_novos

    if anos_perdidos:
        alertas.append(
            f"Histórico perdeu {len(anos_perdidos)} ano(s): "
            f"{sorted(anos_perdidos)[:5]}{'...' if len(anos_perdidos) > 5 else ''}"
        )

    # Comparar valores: detectar variações drásticas nos mesmos ano/mês
    for ano in anos_antigos & anos_novos:
        meses_antigos = historico_antigo.get(ano, {})
        meses_novos = historico_novo.get(ano, {})
        for mes, valor_antigo in meses_antigos.items():
            valor_novo = meses_novos.get(mes)
            if valor_novo is None:
                continue
            diff = abs(valor_novo - valor_antigo)
            if diff > limiar_variacao:
                alertas.append(
                    f"Variação anômala {mes}/{ano}: {valor_antigo} → {valor_novo} "
                    f"(diff {diff:+.2f} pontos)"
                )

    return alertas


def validar_e_salvar(
    dados_novos: dict,
    caminho: Path,
    limiar_variacao: float = THRESHOLD_VARIACAO_ABS,
) -> tuple[bool, list[str]]:
    """Valida dados contra JSON anterior e salva se não houver anomalias críticas.

    Args:
        dados_novos: Dados recém-extraídos.
        caminho: Caminho do arquivo JSON de saída.
        limiar_variacao: Limiar para detecção de variação anômala.

    Returns:
        Tupla (salvou, alertas). salvou=True se arquivo foi escrito.
        Anomalias não impedem salvamento — apenas emitem alertas.
    """
    dados_anteriores = carregar_json_anterior(caminho)
    alertas = validar_dados(dados_novos, dados_anteriores, limiar_variacao)

    if alertas:
        for alerta in alertas:
            logger.warning(f"[VALIDAÇÃO] {alerta}")
    else:
        logger.info("[VALIDAÇÃO] Dados consistentes com coleta anterior")

    # Salvar mesmo com alertas — melhor ter dados novos que nenhum
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados_novos, f, ensure_ascii=False, indent=2)
    logger.info(f"Dados salvos em: {caminho}")

    return True, alertas