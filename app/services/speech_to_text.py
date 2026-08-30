"""
Speech-to-text service for converting audio to text.
Currently supports:
- OpenAI Whisper API
- Local whisper model (if available)
"""

import os
from io import BytesIO
import httpx
from typing import Optional


class SpeechToTextError(RuntimeError):
    """Raised when speech-to-text conversion fails."""
    pass


class SpeechToTextService:
    """Service for converting audio to text using various providers."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.provider = self._detect_provider()

    def _detect_provider(self) -> str:
        """Detect which speech-to-text provider to use."""
        if self.openai_api_key:
            return "openai"
        # Add more providers as needed
        raise SpeechToTextError(
            "No speech-to-text provider configured. "
            "Set OPENAI_API_KEY environment variable."
        )

    async def transcribe(self, audio_data: bytes, audio_format: str = "webm") -> str:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format (webm, mp3, ogg, etc.)

        Returns:
            Transcribed text

        Raises:
            SpeechToTextError: If transcription fails
        """
        if self.provider == "openai":
            return await self._transcribe_openai(audio_data, audio_format)
        else:
            raise SpeechToTextError(f"Unsupported provider: {self.provider}")

    async def _transcribe_openai(self, audio_data: bytes, audio_format: str) -> str:
        """Transcribe using OpenAI Whisper API."""
        try:
            # Map format to file extension
            format_map = {
                "webm": "webm",
                "ogg": "ogg",
                "mp3": "mp3",
                "wav": "wav",
                "m4a": "m4a",
            }
            file_ext = format_map.get(audio_format.lower().replace("audio/", ""), "webm")

            # Prepare multipart form data
            files = {
                "file": (f"audio.{file_ext}", BytesIO(audio_data), f"audio/{file_ext}"),
                "model": (None, "whisper-1"),
                "language": (None, "fr"),
            }

            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    files=files,
                    headers=headers,
                )

            if response.status_code != 200:
                error_detail = response.text
                raise SpeechToTextError(
                    f"OpenAI API error: {response.status_code} - {error_detail}"
                )

            result = response.json()
            if not isinstance(result, dict) or "text" not in result:
                raise SpeechToTextError("Invalid response from OpenAI API")

            return result["text"].strip()

        except httpx.RequestError as e:
            raise SpeechToTextError(f"Network error during transcription: {e}") from e
        except Exception as e:
            raise SpeechToTextError(f"Transcription failed: {e}") from e
