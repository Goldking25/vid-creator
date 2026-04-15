"""
Prompt builder – converts trending video data into cinematic video generation prompts.
Uses Gemini Pro (text model) to enhance prompts creatively.
"""

import logging
from google import genai
from google.genai import types

from models.trending import TrendingVideo

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds and enhances cinematic prompts for video generation from trending video data."""

    SYSTEM_INSTRUCTION = (
        "You are a creative director for animated short videos. "
        "Given information about a trending YouTube video, create a vivid, "
        "cinematic prompt for an AI video generator (Veo 3.1). "
        "The prompt should describe an animated scene that captures the essence "
        "and theme of the trending topic. Keep it to 2-3 sentences. "
        "Focus on visual elements: colors, camera movement, lighting, mood, "
        "and animation style. Do NOT mention YouTube or the original video. "
        "Output ONLY the video generation prompt, nothing else."
    )

    def __init__(self, api_key: str, model: str = "gemini-2.5-pro-preview-05-06"):
        if not api_key:
            raise ValueError("Google API key is required for prompt building.")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def build_prompt(self, video: TrendingVideo) -> str:
        """
        Build a basic cinematic prompt from trending video metadata.

        Args:
            video: A TrendingVideo object.

        Returns:
            A plain text prompt string.
        """
        tags_str = ", ".join(video.tags[:5]) if video.tags else "general"
        prompt = (
            f"Create an animated video about: {video.title}. "
            f"Theme/tags: {tags_str}. "
            f"Description context: {video.description[:200]}"
        )
        return prompt

    def enhance_prompt(self, video: TrendingVideo) -> str:
        """
        Use Gemini Pro to transform trending video metadata into a
        creative, cinematic video generation prompt.

        Args:
            video: A TrendingVideo object.

        Returns:
            An enhanced cinematic prompt string.
        """
        raw_prompt = self.build_prompt(video)

        try:
            logger.info("Enhancing prompt for: %s", video.title)
            response = self._client.models.generate_content(
                model=self._model,
                contents=raw_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=0.9,
                    max_output_tokens=256,
                ),
            )
            enhanced = response.text.strip()
            logger.info("Enhanced prompt: %s", enhanced[:100])
            return enhanced

        except Exception as e:
            logger.warning(
                "Prompt enhancement failed, using basic prompt: %s", e
            )
            return raw_prompt
