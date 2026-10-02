from pathlib import Path

# Project root:
# revenue_ai_agent_complete/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# SQLite database:
DB_PATH = PROJECT_ROOT / "data" / "revenue.db"