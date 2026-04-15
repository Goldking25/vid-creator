"""
Central configuration for the Trending Video Creator application.
Loads environment variables and defines application-wide defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the project root
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# --- API Keys ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

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
