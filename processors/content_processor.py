"""
Content processor – ranks and selects top trending videos for video generation.
"""

import logging
from models.trending import TrendingVideo

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Processes and ranks trending videos by engagement."""

    def rank_videos(self, videos: list[TrendingVideo]) -> list[TrendingVideo]:
        """
        Sort videos by engagement score (descending).

        Args:
            videos: List of TrendingVideo objects.

        Returns:
            Same list sorted by engagement_score descending.
        """
        ranked = sorted(videos, key=lambda v: v.engagement_score, reverse=True)
        logger.info(
            "Ranked %d videos. Top: %s (score=%s)",
            len(ranked),
            ranked[0].title if ranked else "N/A",
            f"{ranked[0].engagement_score:,.0f}" if ranked else "N/A",
        )
        return ranked

    def select_top(
        self, videos: list[TrendingVideo], n: int = 3
    ) -> list[TrendingVideo]:
        """
        Select top N videos from a ranked list.

        Args:
            videos: List of TrendingVideo objects (ideally pre-ranked).
            n: Number of top videos to select.

        Returns:
            Top N videos.
        """
        ranked = self.rank_videos(videos)
        selected = ranked[:n]
        logger.info(
            "Selected top %d videos: %s",
            len(selected),
            [v.title for v in selected],
        )
        return selected

    def deduplicate(self, videos: list[TrendingVideo]) -> list[TrendingVideo]:
        """
        Remove duplicate videos based on video_id.

        Args:
            videos: List of TrendingVideo objects.

        Returns:
            Deduplicated list preserving original order.
        """
        seen = set()
        unique = []
        for video in videos:
            if video.video_id not in seen:
                seen.add(video.video_id)
                unique.append(video)
        if len(unique) < len(videos):
            logger.info(
                "Removed %d duplicate(s).", len(videos) - len(unique)
            )
        return unique
