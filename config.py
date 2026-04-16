"""
Central configuration for the Trending Video Creator application.
Loads API keys from keyring (Windows Credential Manager), falling back
to environment variables / .env file.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    import keyring
    _HAS_KEYRING = True
except ImportError:
    _HAS_KEYRING = False

SERVICE_NAME = "vid-creator"


def _get_key(name: str) -> str:
    """Get an API key: keyring first, then env var, then empty string."""
    if _HAS_KEYRING:
        try:
            val = keyring.get_password(SERVICE_NAME, name)
            if val:
                return val
        except Exception:
            pass  # No keyring backend (headless Linux, CI, etc.)
    return os.getenv(name, "")


# --- API Keys ---
YOUTUBE_API_KEY = _get_key("YOUTUBE_API_KEY")
GOOGLE_API_KEY = _get_key("GOOGLE_API_KEY")

# --- YouTube Settings ---
YOUTUBE_REGION_CODE = os.getenv("YOUTUBE_REGION_CODE", "IN")
YOUTUBE_MAX_RESULTS = int(os.getenv("YOUTUBE_MAX_RESULTS", "10"))

# --- Video Generation Settings ---
VEO_MODEL = "veo-3.1-generate-preview"
GEMINI_TEXT_MODEL = "gemini-2.5-pro"
VIDEO_RESOLUTION = "720p"
VIDEO_POLL_INTERVAL = 10  # seconds between polling for video completion
VIDEO_POLL_TIMEOUT = 300  # max seconds to wait for video generation

# --- Output Settings ---
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(Path(__file__).parent / "output")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Content Processing ---
TOP_N_VIDEOS = int(os.getenv("TOP_N_VIDEOS", "3"))
