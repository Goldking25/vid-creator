"""
Video generator – uses Google Veo 3.1 to create animated videos from prompts.
"""

import time
import logging
from pathlib import Path

from google import genai

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generates videos using Google Veo 3.1 model via the Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str = "veo-3.1-generate-preview",
        poll_interval: int = 10,
        poll_timeout: int = 300,
    ):
        if not api_key:
            raise ValueError("Google API key is required for video generation.")
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._poll_interval = poll_interval
        self._poll_timeout = poll_timeout

    def generate(self, prompt: str, output_path: Path) -> Path:
        """
        Generate a video from a text prompt using Veo 3.1.

        Args:
            prompt: Cinematic text prompt for video generation.
            output_path: Path to save the generated .mp4 file.

        Returns:
            Path to the saved video file.

        Raises:
            TimeoutError: If video generation exceeds poll_timeout.
            RuntimeError: If generation fails.
        """
        logger.info("Starting video generation...")
        logger.info("Prompt: %s", prompt[:150])

        try:
            # Initiate async video generation
            operation = self._client.models.generate_videos(
                model=self._model,
                prompt=prompt,
            )

            # Poll until completion
            elapsed = 0
            while not operation.done:
                if elapsed >= self._poll_timeout:
                    raise TimeoutError(
                        f"Video generation timed out after {self._poll_timeout}s."
                    )
                logger.info(
                    "Generating... (%ds elapsed, polling every %ds)",
                    elapsed,
                    self._poll_interval,
                )
                time.sleep(self._poll_interval)
                elapsed += self._poll_interval

            # Check for result
            if not operation.result:
                raise RuntimeError("Video generation completed but returned no result.")

            # Save the generated video
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # The result contains generated videos
            generated_video = operation.result.generated_videos[0]
            video_bytes = self._client.files.download(file=generated_video.video)

            output_path.write_bytes(video_bytes)
            logger.info("Video saved to: %s", output_path)
            return output_path

        except TimeoutError:
            raise
        except Exception as e:
            logger.error("Video generation failed: %s", e)
            raise RuntimeError(f"Video generation failed: {e}") from e
