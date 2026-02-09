import os
import pytest
from pathlib import Path


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs from a .env-style file into os.environ if not already set."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # don't overwrite existing env vars
        if key not in os.environ:
            os.environ[key] = val


# Try to load .env.test first (used by docker-compose.test.yml), then fall back to .env
_root = Path(__file__).resolve().parents[1]
_load_env_file(_root / ".env.test")
_load_env_file(_root / ".env")

# Use DATABASE_URL from environment if available; otherwise fall back to a sensible default
TEST_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/webstore",
)


@pytest.fixture(scope="session", autouse=True)
def test_env():
    # Ensure tests always see DATABASE_URL during their run
    os.environ["DATABASE_URL"] = TEST_DB_URL
    yield
