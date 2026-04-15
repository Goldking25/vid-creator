# 🎬 Trending Video Creator

Fetch trending YouTube videos and automatically generate animated videos using Google Veo 3.1.

## Pipeline

```
YouTube Trending → Rank by Engagement → Gemini Pro Prompt → Veo 3.1 Animation → .mp4
```

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Add your API keys
cp .env.example .env
# Edit .env with your YouTube + Google AI Studio keys

# Fetch trending (no generation)
python main.py --skip-generation --count 5

# Generate animated videos
python main.py --count 3 --region IN
```

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--region` | `IN` | YouTube region code |
| `--count` | `3` | Videos to generate |
| `--fetch-count` | `10` | Videos to fetch |
| `--output` | `./output` | Output directory |
| `--skip-generation` | - | Fetch only, no video gen |
| `-v` | - | Verbose logging |

## API Keys Required

1. **YouTube Data API v3** → [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Google AI Studio** → [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

## License

MIT
