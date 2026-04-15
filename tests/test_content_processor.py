"""Tests for ContentProcessor."""

import pytest
from processors.content_processor import ContentProcessor
from models.trending import TrendingVideo


def _make_video(video_id: str, views: int, likes: int, comments: int, title: str = "") -> TrendingVideo:
    """Helper to create a TrendingVideo with specific engagement stats."""
    return TrendingVideo(
        video_id=video_id,
        title=title or f"Video {video_id}",
        description="Test description",
        channel_title="TestChannel",
        category_id="10",
        thumbnail_url="https://example.com/thumb.jpg",
        view_count=views,
        like_count=likes,
        comment_count=comments,
    )


class TestContentProcessor:
    """Tests for the ContentProcessor class."""

    def setup_method(self):
        self.processor = ContentProcessor()

    def test_rank_videos_sorted_by_engagement(self):
        videos = [
            _make_video("low", views=100, likes=10, comments=1),     # 100 + 100 + 50 = 250
            _make_video("high", views=1000, likes=100, comments=50), # 1000 + 1000 + 2500 = 4500
            _make_video("mid", views=500, likes=50, comments=10),    # 500 + 500 + 500 = 1500
        ]
        ranked = self.processor.rank_videos(videos)

        assert ranked[0].video_id == "high"
        assert ranked[1].video_id == "mid"
        assert ranked[2].video_id == "low"

    def test_rank_empty_list(self):
        ranked = self.processor.rank_videos([])
        assert ranked == []

    def test_select_top_returns_n(self):
        videos = [
            _make_video("a", 1000, 100, 10),
            _make_video("b", 2000, 200, 20),
            _make_video("c", 3000, 300, 30),
            _make_video("d", 4000, 400, 40),
        ]
        top = self.processor.select_top(videos, n=2)
        assert len(top) == 2
        assert top[0].video_id == "d"
        assert top[1].video_id == "c"

    def test_select_top_when_n_exceeds_list(self):
        videos = [_make_video("a", 100, 10, 1)]
        top = self.processor.select_top(videos, n=5)
        assert len(top) == 1

    def test_deduplicate_removes_duplicates(self):
        videos = [
            _make_video("abc", 1000, 100, 10),
            _make_video("def", 2000, 200, 20),
            _make_video("abc", 1000, 100, 10),  # duplicate
        ]
        unique = self.processor.deduplicate(videos)
        assert len(unique) == 2
        assert unique[0].video_id == "abc"
        assert unique[1].video_id == "def"

    def test_deduplicate_no_duplicates(self):
        videos = [
            _make_video("a", 100, 10, 1),
            _make_video("b", 200, 20, 2),
        ]
        unique = self.processor.deduplicate(videos)
        assert len(unique) == 2

    def test_deduplicate_preserves_order(self):
        videos = [
            _make_video("x", 100, 10, 1),
            _make_video("y", 200, 20, 2),
            _make_video("z", 300, 30, 3),
            _make_video("y", 200, 20, 2),  # duplicate
        ]
        unique = self.processor.deduplicate(videos)
        assert [v.video_id for v in unique] == ["x", "y", "z"]
