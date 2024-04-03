"""Init dbt_score package."""

import os
from pathlib import Path

MANIFEST_PATH = (
    Path()
    / os.getenv("DBT_PROJECT_DIR", "")
    / os.getenv("DBT_TARGET_DIR", "target")
    / "manifest.json"
)
