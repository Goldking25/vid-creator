"""
Data models for trending video content.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrendingVideo:
    """Represents a trending video fetched from YouTube."""

    video_id: str
    title: str
    description: str
    channel_title: str
    category_id: str
    thumbnail_url: str
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    tags: list[str] = field(default_factory=list)
    published_at: str = ""

    @property
    def engagement_score(self) -> float:
        """
        Calculate a simple engagement score based on views, likes, and comments.
        Weighted: views (1x) + likes (10x) + comments (50x)
        """
        return self.view_count + (self.like_count * 10) + (self.comment_count * 50)

    def summary(self) -> str:
        """Return a one-line summary of the video."""
        return (
            f"[{self.video_id}] {self.title} by {self.channel_title} "
            f"| Views: {self.view_count:,} | Likes: {self.like_count:,}"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "channel_title": self.channel_title,
            "category_id": self.category_id,
            "thumbnail_url": self.thumbnail_url,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "tags": self.tags,
            "published_at": self.published_at,
            "engagement_score": self.engagement_score,
        }
