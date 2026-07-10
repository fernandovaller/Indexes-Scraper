# Indexes Scraper

Scrapers para coleta automatizada de índices econômicos brasileiros do site [Debit](https://www.debit.com.br).

## Índices Suportados

| Índice | Fonte | Descrição |
|--------|-------|-----------|
| IGP-DI | FGV | Índice Geral de Preços - Disponibilidade Interna |
| IGP-M | FGV | Índice Geral de Preços do Mercado |
| INCC-DI | FGV | Índice Nacional da Construção Civil |
| INPC | IBGE | Índice Nacional de Preços ao Consumidor |
| IPCA | IBGE | Índice Nacional de Preços ao Consumidor Amplo |
| IVAR | FGV | Índice de Variação de Aluguéis Residenciais |
| SELIC | Banco Central | Taxa Básica de Juros |
| CDI | B3 | Certificado de Depósito Interbancário |
| TR | Banco Central | Taxa Referencial |
| IPC-Fipe | Fipe | Índice de Preços ao Consumidor |

## Estrutura

```
.
├── api.py                  # API FastAPI para servir os dados coletados
├── config.py               # Configurações (URLs, caminhos, env vars)
├── main.py                 # Entry point principal
├── output/                 # JSONs gerados (gitignored)
├── pyproject.toml          # Metadados e dependências do projeto
├── requirements.txt        # Dependências runtime
├── .env.example            # Template de configuração via env vars
├── scrapers/
│   ├── __init__.py         # Registry SCRAPERS
│   ├── base_scraper.py    # Classe base com lógica comum (template method)
│   ├── selic_scraper.py   # Scraper SELIC (sobrescreve hooks do base)
│   ├── igpm_scraper.py    # Scraper IGP-M
│   ├── inpc_scraper.py    # Scraper INPC
│   ├── ipca_scraper.py    # Scraper IPCA
│   ├── cdi_scraper.py     # Scraper CDI
│   ├── tr_scraper.py      # Scraper TR
│   └── ...                # Demais scrapers
└── utils/
    ├── webdriver_helper.py # Configuração do Selenium
    ├── retry.py            # Decorador de retry com backoff exponencial
    ├── validation.py       # Validação de dados (detecta anomalias)
    └── logging_config.py  # Logging estruturado (text/JSON)
```

## Requisitos

- Python 3.10+
- Google Chrome ou Chromium
- ChromeDriver (instalado automaticamente via `webdriver-manager`)

## Instalação em Ambiente Virtual

### Linux/macOS

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Para instalar com dependências de API (opcional)
pip install -r requirements.txt  # já inclui fastapi + uvicorn

# Para instalar em modo desenvolvimento (opcional)
pip install -e ".[dev]"
```

### Windows

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Verificar instalação

```bash
python main.py --help
```

## Configuração

As configurações podem ser feitas via arquivo `.env` ou variáveis de ambiente.

```bash
# Copiar template
cp .env.example .env

# Editar conforme necessário
nano .env
```

Variáveis disponíveis:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `INDEXES_OUTPUT_DIR` | `output/` | Diretório de saída dos JSONs |
| `INDEXES_LOG_FORMAT` | `text` | Formato de log: `text` ou `json` |
| `INDEXES_LOG_LEVEL` | `INFO` | Nível de log: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `INDEXES_HEADLESS` | `true` | Chrome headless: `true` ou `false` |
| `INDEXES_USER_AGENT` | Chrome 120 | User agent do Chrome |
| `INDEXES_API_PORT` | `8000` | Porta da API |

## Uso

### Executar todos os scrapers (sequencial)

```bash
python main.py
```

### Executar em paralelo (1 Chrome por scraper)

```bash
python main.py --parallel
```

Mais rápido, porém usa mais memória (uma instância do Chrome por scraper).

### Executar scraper específico

```bash
python main.py igpm
python main.py selic cdi
```

Índices disponíveis: `igpdi`, `igpm`, `inccdi`, `inpc`, `ipca`, `ivar`, `selic`, `cdi`, `tr`, `ipcfipe`

### Executar individualmente

```bash
python -m scrapers.igpm_scraper
python -m scrapers.selic_scraper
```

### Logs estruturados (JSON)

```bash
python main.py --log-format json
# ou via env var
INDEXES_LOG_FORMAT=json python main.py
```

Exemplo de saída:
```json
{"timestamp": "2026-07-10T11:29:15-03:00", "level": "INFO", "logger": "main", "message": "Executando todos os scrapers"}
```

## API

O projeto inclui uma API FastAPI para consultar os dados coletados.

### Iniciar a API

```bash
python api.py
# ou
uvicorn api:app --reload
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Informações da API |
| `GET` | `/indices` | Lista todos os índices disponíveis |
| `GET` | `/{indice}` | Dados completos de um índice |
| `GET` | `/{indice}/atual` | Informação atual do índice |
| `GET` | `/{indice}/12meses` | Últimos 12 meses |
| `GET` | `/{indice}/historico` | Histórico completo |
| `GET` | `/{indice}/historico?ano=2024` | Histórico filtrado por ano |

### Exemplos

```bash
# Listar índices
curl http://localhost:8000/indices

# Dados do IGP-M
curl http://localhost:8000/igpm

# Últimos 12 meses da SELIC
curl http://localhost:8000/selic/12meses

# Histórico de 2024 do IPCA
curl http://localhost:8000/ipca/historico?ano=2024
```

## Saída

Os arquivos JSON são salvos em `output/` com a seguinte estrutura:

```json
{
  "fonte": "https://www.debit.com.br/tabelas/...",
  "titulo": "IGP-M - FGV",
  "informacao_atual": "O IGP-M de junho/2026 é 0,45%",
  "data_coleta": "2026-07-10T11:29:15-03:00",
  "ultimos_12_meses": [
    {
      "data": "Jun/2026",
      "variacao": 0.45,
      "variacao_periodo": 0.45,
      "acumulado_12_meses": 4.32
    }
  ],
  "historico": {
    "2024": {
      "Jan": 0.45,
      "Fev": 0.38
    }
  }
}
```

### Validação automática

Ao salvar, o sistema compara os dados novos com a coleta anterior e emite alertas se detectar:

- **Dados vazios**: histórico ou últimos 12 meses sem registros
- **Perda de anos**: anos que existiam antes e desapareceram
- **Variação anômala**: diferença superior a 10 pontos percentuais no mesmo mês/ano

Os alertas são logados mas **não impedem o salvamento** — é melhor ter dados novos que nenhum.

## Desenvolvimento

### Adicionar novo índice

1. Adicione a URL em `config.py`:
```python
URLS = {
    ...
    "novo_indice": "https://www.debit.com.br/tabelas/...",
}

TITULOS = {
    ...
    "novo_indice": "Novo Índice - Fonte",
}

OUTPUT_FILES = {
    ...
    "novo_indice": OUTPUT_DIR / "novo_indice.json",
}
```

2. Crie o scraper em `scrapers/novo_indice_scraper.py`:
```python
from base_scraper import BaseScraper
from config import URLS, TITULOS, OUTPUT_FILES


class NovoIndiceScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            url=URLS["novo_indice"],
            titulo_padrao=TITULOS["novo_indice"],
            arquivo_saida=OUTPUT_FILES["novo_indice"],
        )


def run_novo_indice(driver=None) -> bool:
    scraper = NovoIndiceScraper()
    return scraper.run(driver)
```

3. Registre em `scrapers/__init__.py`:
```python
from .novo_indice_scraper import run_novo_indice

SCRAPERS = {
    ...
    "novo_indice": run_novo_indice,
}
```

### Testes

```bash
# Instalar deps de desenvolvimento
pip install -e ".[dev]"

# Rodar testes
pytest
```

## Licença

MIT