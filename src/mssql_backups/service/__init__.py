from .bak import app as bak_app
from .cache import app as cache_app
from .config import app as config_app
from .db import app as db_app
from .restore import app as restore_app

cache = cache_app
config = config_app
restore = restore_app
db = db_app
bak = bak_app
