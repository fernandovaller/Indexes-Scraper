# Scrapers para índices econômicos
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from .cdi_scraper import run_cdi
from .igpdi_scraper import run_igpdi
from .igpm_scraper import run_igpm
from .inccdi_scraper import run_inccdi
from .inpc_scraper import run_inpc
from .ipca_scraper import run_ipca
from .ipcfipe_scraper import run_ipcfipe
from .ivar_scraper import run_ivar
from .selic_scraper import run_selic
from .tr_scraper import run_tr

SCRAPERS = {
    "igpdi": run_igpdi,
    "igpm": run_igpm,
    "inccdi": run_inccdi,
    "inpc": run_inpc,
    "ipca": run_ipca,
    "ivar": run_ivar,
    "selic": run_selic,
    "cdi": run_cdi,
    "tr": run_tr,
    "ipcfipe": run_ipcfipe,
}

__all__ = [
    'SCRAPERS',
    'run_igpdi', 'run_igpm', 'run_inccdi', 'run_inpc', 'run_ipca',
    'run_ivar', 'run_selic', 'run_cdi', 'run_tr', 'run_ipcfipe',
]
