"""Tests for PromptBuilder."""

import pytest
from unittest.mock import MagicMock, patch

from processors.prompt_builder import PromptBuilder
from models.trending import TrendingVideo


def _sample_video() -> TrendingVideo:
    return TrendingVideo(
        video_id="abc123",
        title="Epic Space Exploration Documentary",
        description="Journey through the cosmos exploring distant galaxies and nebulae.",
        channel_title="SpaceChannel",
        category_id="28",
        thumbnail_url="https://example.com/thumb.jpg",
        view_count=5000000,
        like_count=200000,
        comment_count=15000,
        tags=["space", "galaxy", "cosmos", "documentary", "science"],
    )


class TestPromptBuilder:
    """Tests for the PromptBuilder class."""

    def test_init_raises_on_empty_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            PromptBuilder(api_key="")

    @patch("processors.prompt_builder.genai.Client")
    def test_build_prompt_contains_video_info(self, mock_client_cls):
        builder = PromptBuilder(api_key="fake-key")
        video = _sample_video()

        prompt = builder.build_prompt(video)

        assert "Epic Space Exploration Documentary" in prompt
        assert "space" in prompt
        assert "cosmos" in prompt

    @patch("processors.prompt_builder.genai.Client")
    def test_build_prompt_with_no_tags(self, mock_client_cls):
        builder = PromptBuilder(api_key="fake-key")
        video = _sample_video()
        video.tags = []

        prompt = builder.build_prompt(video)

        assert "general" in prompt

    @patch("processors.prompt_builder.genai.Client")
    def test_enhance_prompt_calls_gemini(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = (
            "A sweeping cinematic shot through an endless nebula, "
            "with vibrant purples and blues illuminating the scene."
        )
        mock_client.models.generate_content.return_value = mock_response

        builder = PromptBuilder(api_key="fake-key")
        video = _sample_video()

        enhanced = builder.enhance_prompt(video)

        assert "nebula" in enhanced
        mock_client.models.generate_content.assert_called_once()

    @patch("processors.prompt_builder.genai.Client")
    def test_enhance_prompt_falls_back_on_error(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API error")

        builder = PromptBuilder(api_key="fake-key")
        video = _sample_video()

        result = builder.enhance_prompt(video)

        # Should fall back to basic prompt
        assert "Epic Space Exploration Documentary" in result

    @patch("processors.prompt_builder.genai.Client")
    def test_build_prompt_truncates_long_description(self, mock_client_cls):
        builder = PromptBuilder(api_key="fake-key")
        video = _sample_video()
        video.description = "A" * 500

        prompt = builder.build_prompt(video)

        # Description context should be truncated to 200 chars
        assert len(prompt) < 600
