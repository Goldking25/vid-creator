"""Tests for VideoGenerator."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile

from generators.video_generator import VideoGenerator


class TestVideoGenerator:
    """Tests for the VideoGenerator class."""

    def test_init_raises_on_empty_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            VideoGenerator(api_key="")

    @patch("generators.video_generator.genai.Client")
    def test_generate_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Mock the operation (already done on first check)
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result.generated_videos = [MagicMock()]
        mock_client.models.generate_videos.return_value = mock_operation

        # Mock file download
        mock_client.files.download.return_value = b"fake video bytes"

        generator = VideoGenerator(api_key="fake-key", poll_interval=0, poll_timeout=10)

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test_video.mp4"
            result = generator.generate("A cinematic scene", output)

            assert result == output
            assert output.read_bytes() == b"fake video bytes"

    @patch("generators.video_generator.genai.Client")
    @patch("generators.video_generator.time.sleep")
    def test_generate_polls_until_done(self, mock_sleep, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Simulate polling: not done, not done, done
        mock_operation = MagicMock()
        type(mock_operation).done = PropertyMock(side_effect=[False, False, True])
        mock_operation.result.generated_videos = [MagicMock()]
        mock_client.models.generate_videos.return_value = mock_operation

        mock_client.files.download.return_value = b"video data"

        generator = VideoGenerator(api_key="fake-key", poll_interval=1, poll_timeout=30)

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.mp4"
            generator.generate("test prompt", output)

            # Should have slept twice (two False polls)
            assert mock_sleep.call_count == 2

    @patch("generators.video_generator.genai.Client")
    @patch("generators.video_generator.time.sleep")
    def test_generate_timeout(self, mock_sleep, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_operation = MagicMock()
        mock_operation.done = False  # Never completes
        mock_client.models.generate_videos.return_value = mock_operation

        generator = VideoGenerator(api_key="fake-key", poll_interval=5, poll_timeout=10)

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.mp4"
            with pytest.raises(TimeoutError):
                generator.generate("test prompt", output)

    @patch("generators.video_generator.genai.Client")
    def test_generate_no_result(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result = None
        mock_client.models.generate_videos.return_value = mock_operation

        generator = VideoGenerator(api_key="fake-key", poll_interval=0, poll_timeout=10)

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.mp4"
            with pytest.raises(RuntimeError, match="no result"):
                generator.generate("test prompt", output)
