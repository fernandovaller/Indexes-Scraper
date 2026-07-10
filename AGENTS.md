# AGENTS.md - Indexes Scraper

## Commands

```bash
# Run all scrapers
python main.py

# Run specific scrapers
python main.py igpm inpc ipca

# Run single scraper directly
python -m scrapers.igpm_scraper
```

## Architecture

- `main.py` - Entry point, routes to scrapers via SCRAPERS dict
- `config.py` - URLs map, titles, output paths. All scraper configs here.
- `scrapers/__init__.py` - SCRAPERS registry. Add new scrapers here.
- `scrapers/base_scraper.py` - Base class with Selenium + BeautifulSoup logic
- `output/` - Generated JSON files (gitignored)

## Adding a New Index

1. Add URL to `config.py` URLS dict
2. Add title to TITULOS dict
3. Add output path to OUTPUT_FILES dict
4. Create `scrapers/<name>_scraper.py` inheriting from BaseScraper
5. Register in `scrapers/__init__.py` SCRAPERS dict
6. `run_*()` function must accept `driver=None` param and pass it to `scraper.run(driver)`

## Dependencies

- Python 3.8+
- Google Chrome/Chromium (Selenium needs browser)
- `pip install -r requirements.txt`

## Output Format

JSON files in `output/` with: `fonte`, `titulo`, `informacao_atual`, `data_coleta`, `ultimos_12_meses[]`, `historico{year{month}}`
