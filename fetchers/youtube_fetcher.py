"""
YouTube Data API v3 fetcher for trending videos.
"""

import logging
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.trending import TrendingVideo

logger = logging.getLogger(__name__)


class YouTubeFetcher:
    """Fetches trending (most popular) videos from YouTube Data API v3."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("YouTube API key is required.")
        self._api_key = api_key
        self._youtube = build("youtube", "v3", developerKey=api_key)

    def get_trending(
        self,
        region_code: str = "IN",
        max_results: int = 10,
        category_id: Optional[str] = None,
    ) -> list[TrendingVideo]:
        """
        Fetch the most popular (trending) videos for a given region.

        Args:
            region_code: ISO 3166-1 alpha-2 country code (e.g. 'IN', 'US').
            max_results: Number of results to return (max 50).
            category_id: Optional YouTube category ID to filter by.

        Returns:
            List of TrendingVideo objects, sorted by popularity.
        """
        try:
            request_params = {
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": region_code,
                "maxResults": min(max_results, 50),
            }
            if category_id:
                request_params["videoCategoryId"] = category_id

            logger.info(
                "Fetching trending videos: region=%s, max=%d",
                region_code,
                max_results,
            )

            response = self._youtube.videos().list(**request_params).execute()
            videos = self._parse_response(response)

            logger.info("Fetched %d trending videos.", len(videos))
            return videos

        except HttpError as e:
            logger.error("YouTube API error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error fetching trending videos: %s", e)
            raise

    def _parse_response(self, response: dict) -> list[TrendingVideo]:
        """Parse the YouTube API response into TrendingVideo objects."""
        videos = []

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            thumbnails = snippet.get("thumbnails", {})

            # Pick the best available thumbnail
            thumbnail_url = ""
            for quality in ("maxres", "high", "medium", "default"):
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality].get("url", "")
                    break

            video = TrendingVideo(
                video_id=item.get("id", ""),
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                channel_title=snippet.get("channelTitle", ""),
                category_id=snippet.get("categoryId", ""),
                thumbnail_url=thumbnail_url,
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                comment_count=int(statistics.get("commentCount", 0)),
                tags=snippet.get("tags", []),
                published_at=snippet.get("publishedAt", ""),
            )
            videos.append(video)

        return videos
