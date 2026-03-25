from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parents[1]
print(f"Project root: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
