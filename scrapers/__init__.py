# Scrapers para índices econômicos
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from .igpdi_scraper import run_igpdi
from .igpm_scraper import run_igpm
from .inccdi_scraper import run_inccdi
from .inpc_scraper import run_inpc
from .ipca_scraper import run_ipca
from .ivar_scraper import run_ivar
from .selic_scraper import run_selic

SCRAPERS = {
    "igpdi": run_igpdi,
    "igpm": run_igpm,
    "inccdi": run_inccdi,
    "inpc": run_inpc,
    "ipca": run_ipca,
    "ivar": run_ivar,
    "selic": run_selic,
}

__all__ = ['SCRAPERS', 'run_igpdi', 'run_igpm', 'run_inccdi', 'run_inpc', 'run_ipca', 'run_ivar', 'run_selic']
