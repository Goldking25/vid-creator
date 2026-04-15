"""Tests for YouTubeFetcher."""

import pytest
from unittest.mock import MagicMock, patch

from fetchers.youtube_fetcher import YouTubeFetcher


SAMPLE_API_RESPONSE = {
    "items": [
        {
            "id": "abc123",
            "snippet": {
                "title": "Test Trending Video",
                "description": "A test description for trending video.",
                "channelTitle": "TestChannel",
                "categoryId": "10",
                "publishedAt": "2026-04-15T10:00:00Z",
                "tags": ["test", "trending", "viral"],
                "thumbnails": {
                    "high": {"url": "https://img.youtube.com/vi/abc123/hqdefault.jpg"},
                    "default": {"url": "https://img.youtube.com/vi/abc123/default.jpg"},
                },
            },
            "statistics": {
                "viewCount": "1500000",
                "likeCount": "50000",
                "commentCount": "3000",
            },
        },
        {
            "id": "def456",
            "snippet": {
                "title": "Another Trending Video",
                "description": "Another description.",
                "channelTitle": "AnotherChannel",
                "categoryId": "22",
                "publishedAt": "2026-04-14T08:00:00Z",
                "tags": [],
                "thumbnails": {
                    "default": {"url": "https://img.youtube.com/vi/def456/default.jpg"},
                },
            },
            "statistics": {
                "viewCount": "500000",
                "likeCount": "10000",
                "commentCount": "500",
            },
        },
    ]
}


@patch("fetchers.youtube_fetcher.build")
class TestYouTubeFetcher:
    """Tests for the YouTubeFetcher class."""

    def test_init_raises_on_empty_key(self, mock_build):
        with pytest.raises(ValueError, match="API key is required"):
            YouTubeFetcher(api_key="")

    def test_get_trending_returns_videos(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = SAMPLE_API_RESPONSE

        fetcher = YouTubeFetcher(api_key="fake-key")
        videos = fetcher.get_trending(region_code="US", max_results=5)

        assert len(videos) == 2
        assert videos[0].video_id == "abc123"
        assert videos[0].title == "Test Trending Video"
        assert videos[0].view_count == 1500000
        assert videos[0].like_count == 50000
        assert videos[0].comment_count == 3000
        assert videos[0].tags == ["test", "trending", "viral"]

    def test_get_trending_parses_thumbnail(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = SAMPLE_API_RESPONSE

        fetcher = YouTubeFetcher(api_key="fake-key")
        videos = fetcher.get_trending()

        # First video has 'high' quality thumbnail
        assert "hqdefault" in videos[0].thumbnail_url
        # Second video only has 'default'
        assert "default" in videos[1].thumbnail_url

    def test_get_trending_empty_response(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = {"items": []}

        fetcher = YouTubeFetcher(api_key="fake-key")
        videos = fetcher.get_trending()

        assert videos == []

    def test_get_trending_max_results_capped_at_50(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = {"items": []}

        fetcher = YouTubeFetcher(api_key="fake-key")
        fetcher.get_trending(max_results=100)

        call_kwargs = mock_service.videos().list.call_args[1]
        assert call_kwargs["maxResults"] == 50

    def test_get_trending_with_category_filter(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = {"items": []}

        fetcher = YouTubeFetcher(api_key="fake-key")
        fetcher.get_trending(category_id="10")

        call_kwargs = mock_service.videos().list.call_args[1]
        assert call_kwargs["videoCategoryId"] == "10"

    def test_engagement_score_calculation(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.videos().list().execute.return_value = SAMPLE_API_RESPONSE

        fetcher = YouTubeFetcher(api_key="fake-key")
        videos = fetcher.get_trending()

        # views + (likes * 10) + (comments * 50)
        # 1_500_000 + (50_000 * 10) + (3_000 * 50) = 1_500_000 + 500_000 + 150_000
        assert videos[0].engagement_score == 2_150_000
