# Indexes Scraper

Scrapers para coleta automatizada de índices econômicos brasileiros (IGP-M, INPC, IPCA) do site [Debit](https://www.debit.com.br).

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

## Estrutura

```
.
├── config.py              # Configurações (URLs, caminhos)
├── main.py                # Entry point principal
├── output/                # JSONs gerados
├── scrapers/
│   ├── base_scraper.py    # Classe base com lógica comum
│   ├── igpm_scraper.py    # Scraper IGP-M
│   ├── inpc_scraper.py    # Scraper INPC
│   └── ipca_scraper.py    # Scraper IPCA
└── utils/
    └── webdriver_helper.py # Configuração do Selenium
```

## Requisitos

- Python 3.8+
- Google Chrome ou Chromium
- ChromeDriver (instalado automaticamente)

```bash
# Instalar dependências
pip install selenium webdriver-manager beautifulsoup4

# Ou se houver requirements.txt
pip install -r requirements.txt
```

## Uso

### Executar todos os scrapers

```bash
python main.py
```

### Executar scraper específico

```bash
python main.py igpm
python main.py inpc
python main.py ipca
```

### Executar múltiplos scrapers

```bash
python main.py inpc ipca
```

### Executar individualmente

```bash
python -m scrapers.igpm_scraper
python -m scrapers.inpc_scraper
python -m scrapers.ipca_scraper
```

## Saída

Os arquivos JSON são salvos em `output/` com a seguinte estrutura:

```json
{
  "fonte": "https://www.debit.com.br/tabelas/...",
  "titulo": "IGP-M - FGV",
  "informacao_atual": "...",
  "data_coleta": "2024-01-15 10:30:00",
  "ultimos_12_meses": [
    {
      "data": "Jan/2024",
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

## Desenvolvimento

### Adicionar novo índice

1. Adicione a URL em `config.py`:
```python
URLS = {
    ...
    "novo_indice": "https://www.debit.com.br/tabelas/...",
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

def run_novo_indice() -> bool:
    scraper = NovoIndiceScraper()
    return scraper.run()
```

3. Registre em `scrapers/__init__.py`:
```python
from .novo_indice_scraper import run_novo_indice

SCRAPERS = {
    ...
    "novo_indice": run_novo_indice,
}
```

## Licença

MIT
