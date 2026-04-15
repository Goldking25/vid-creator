"""
Trending Video Creator – CLI Entry Point

Fetches trending YouTube videos, generates cinematic prompts via Gemini Pro,
and creates animated videos using Veo 3.1.
"""

import argparse
import logging
import sys
from pathlib import Path

import config
from fetchers.youtube_fetcher import YouTubeFetcher
from processors.content_processor import ContentProcessor
from processors.prompt_builder import PromptBuilder
from generators.video_generator import VideoGenerator
from generators.output_manager import OutputManager


def setup_logging(verbose: bool = False) -> None:
    """Configure logging format and level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch trending YouTube videos and generate animated videos with Veo 3.1.",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=config.YOUTUBE_REGION_CODE,
        help=f"YouTube region code (default: {config.YOUTUBE_REGION_CODE})",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=config.TOP_N_VIDEOS,
        help=f"Number of top trending videos to process (default: {config.TOP_N_VIDEOS})",
    )
    parser.add_argument(
        "--fetch-count",
        type=int,
        default=config.YOUTUBE_MAX_RESULTS,
        help=f"Number of trending videos to fetch from YouTube (default: {config.YOUTUBE_MAX_RESULTS})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(config.OUTPUT_DIR),
        help=f"Output directory for generated videos (default: {config.OUTPUT_DIR})",
    )
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Fetch and display trending videos without generating videos.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging.",
    )
    return parser.parse_args()


def main() -> int:
    """Main pipeline: fetch → process → prompt → generate → save."""
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger("main")
    logger.info("=" * 60)
    logger.info("  Trending Video Creator")
    logger.info("=" * 60)

    # --- Validate API keys ---
    if not config.YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY not set. Copy .env.example to .env and fill in your key.")
        return 1

    if not args.skip_generation and not config.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY not set. Required for video generation.")
        return 1

    # --- Step 1: Fetch trending videos ---
    logger.info("Step 1/4: Fetching trending videos (region=%s)...", args.region)
    fetcher = YouTubeFetcher(api_key=config.YOUTUBE_API_KEY)
    try:
        videos = fetcher.get_trending(
            region_code=args.region,
            max_results=args.fetch_count,
        )
    except Exception as e:
        logger.error("Failed to fetch trending videos: %s", e)
        return 1

    if not videos:
        logger.warning("No trending videos found.")
        return 0

    # --- Step 2: Process and rank ---
    logger.info("Step 2/4: Processing and ranking %d videos...", len(videos))
    processor = ContentProcessor()
    videos = processor.deduplicate(videos)
    top_videos = processor.select_top(videos, n=args.count)

    logger.info("\n--- Top %d Trending Videos ---", len(top_videos))
    for i, v in enumerate(top_videos, 1):
        logger.info("  %d. %s", i, v.summary())

    if args.skip_generation:
        logger.info("Skipping video generation (--skip-generation flag).")
        return 0

    # --- Step 3: Build prompts ---
    logger.info("Step 3/4: Building cinematic prompts via Gemini Pro...")
    prompt_builder = PromptBuilder(
        api_key=config.GOOGLE_API_KEY,
        model=config.GEMINI_TEXT_MODEL,
    )

    prompts: list[tuple[int, str]] = []
    for i, video in enumerate(top_videos):
        try:
            prompt = prompt_builder.enhance_prompt(video)
            prompts.append((i, prompt))
            logger.info("  Prompt %d: %s...", i + 1, prompt[:80])
        except Exception as e:
            logger.warning("  Prompt %d failed, using basic: %s", i + 1, e)
            prompts.append((i, prompt_builder.build_prompt(video)))

    # --- Step 4: Generate videos ---
    logger.info("Step 4/4: Generating animated videos via Veo 3.1...")
    output_dir = Path(args.output)
    generator = VideoGenerator(
        api_key=config.GOOGLE_API_KEY,
        model=config.VEO_MODEL,
        poll_interval=config.VIDEO_POLL_INTERVAL,
        poll_timeout=config.VIDEO_POLL_TIMEOUT,
    )
    output_mgr = OutputManager(output_dir)

    success_count = 0
    for idx, prompt in prompts:
        video = top_videos[idx]
        video_path = output_mgr.get_video_path(video, index=idx)

        try:
            logger.info("  Generating video %d/%d: %s", idx + 1, len(prompts), video.title)
            generator.generate(prompt=prompt, output_path=video_path)
            output_mgr.record_generation(video, prompt, video_path, success=True)
            success_count += 1
        except Exception as e:
            logger.error("  Generation failed for '%s': %s", video.title, e)
            output_mgr.record_generation(
                video, prompt, video_path, success=False, error=str(e)
            )

    # --- Save report ---
    report_path = output_mgr.save_report()

    logger.info("=" * 60)
    logger.info("  Done! %d/%d videos generated.", success_count, len(prompts))
    logger.info("  Output: %s", output_dir)
    logger.info("  Report: %s", report_path)
    logger.info("=" * 60)

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
