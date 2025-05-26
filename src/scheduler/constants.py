from decimal import Decimal, getcontext
from pathlib import Path

from platformdirs import user_data_dir

DATA_DIR = Path(user_data_dir("scheduler", "princemuel"))

# /////////////////////////////////////////////
# Constants for the Database
# /////////////////////////////////////////////
# Database file and directory
DATABASE_FILE = "scheduler.db"
DATABASE_PATH = DATA_DIR / DATABASE_FILE
SCHEMA_PATH = Path(__file__).parent / "migrations" / "schema.sql"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# /////////////////////////////////////////////
# Constants for the Scheduler
# /////////////////////////////////////////////
# Enhanced scoring weights (redistributed using exact decimal representations)
PROGRESS_WEIGHT = Decimal("0.35")  # Slightly increased
RECENCY_WEIGHT = Decimal("0.25")  # Increased importance
ROTATION_WEIGHT = Decimal("0.25")  # Weekly rotation weight
CATEGORY_WEIGHT = Decimal("0.15")  # Slightly reduced

# Constants for algorithm tuning
MAX_DAILY_TRACKS = 4
DAYS_FOR_TRACK_ROTATION = 7  # Days to consider for track rotation history
COMPLETION_THRESHOLD = Decimal("0.96")  # Consider a track completed at 96% completion

# Weekly coverage constraints
MIN_APPEARANCES_PER_WEEK = 2
MAX_APPEARANCES_PER_WEEK = 4
BITCOIN_STYLE_SELECTION = True

# Determinism settings
FLOAT_PRECISION = 28  # Precision for Decimal calculations
RANDOM_SEED_MOD = 2**256 - 2**32 - 977  # Modulo for daily seed generation


# Set decimal precision
getcontext().prec = FLOAT_PRECISION
