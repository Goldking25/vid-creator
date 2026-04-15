"""
Output manager – organises generated video files and produces summary reports.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.trending import TrendingVideo

logger = logging.getLogger(__name__)


class OutputManager:
    """Manages output file naming, organisation, and summary reports."""

    def __init__(self, output_dir: Path):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._generated: list[dict] = []

    def get_video_path(self, video: TrendingVideo, index: int = 0) -> Path:
        """
        Generate a timestamped output file path for a video.

        Args:
            video: Source TrendingVideo this generation is based on.
            index: Index in the generation batch.

        Returns:
            Path object for the .mp4 output file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else ""
            for c in video.title[:50]
        ).strip().replace(" ", "_")
        filename = f"{timestamp}_{index:02d}_{safe_title}.mp4"
        return self._output_dir / filename

    def record_generation(
        self,
        video: TrendingVideo,
        prompt: str,
        output_path: Path,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Record a generation attempt for the summary report.

        Args:
            video: Source TrendingVideo.
            prompt: The prompt used for generation.
            output_path: Path where the video was saved.
            success: Whether generation succeeded.
            error: Error message if generation failed.
        """
        record = {
            "source_video": video.to_dict(),
            "prompt": prompt,
            "output_path": str(output_path),
            "success": success,
            "error": error,
            "generated_at": datetime.now().isoformat(),
        }
        self._generated.append(record)
        logger.info(
            "Recorded generation: %s -> %s (success=%s)",
            video.title,
            output_path.name,
            success,
        )

    def save_report(self) -> Path:
        """
        Save a JSON summary report of all generations in this session.

        Returns:
            Path to the saved report file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self._output_dir / f"report_{timestamp}.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_attempted": len(self._generated),
            "total_success": sum(1 for g in self._generated if g["success"]),
            "total_failed": sum(1 for g in self._generated if not g["success"]),
            "generations": self._generated,
        }

        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        logger.info("Report saved to: %s", report_path)
        return report_path
