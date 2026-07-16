import subprocess
from typing import cast, Any
from collections.abc import Iterator

import yt_dlp

YDL_OPTION = {
    "format": "bestaudio/best",
    "default_search": "ytsearch",
    "quiet": True,
}


class AudioExtractionError(RuntimeError): ...


class AudioStreamError(RuntimeError): ...


class PlayMusic:
    def __init__(self, query: str) -> None:
        self.query = query.strip()
        if not self.query:
            raise ValueError("La requête musicale ne peut pas être vide.")

        self.url: str | None = None

    def _extract_url(self) -> str:
        try:
            with yt_dlp.YoutubeDL(cast(Any, YDL_OPTION)) as ydl:
                info = cast(
                    dict[str, Any], ydl.extract_info(self.query, download=False)
                )
                if not info:
                    raise AudioExtractionError("Aucun résultat musical trouvé.")

                if info.get("entries"):
                    info = next((entry for entry in info["entries"] if entry), None)
                    if not info:
                        raise AudioExtractionError("Aucun résultat musical trouvé.")

                audio_formats = [
                    f
                    for f in info.get("formats", [])
                    if f.get("acodec") not in (None, "none")
                    and f.get("vcodec") == "none"
                ]

                if not audio_formats:
                    raise AudioExtractionError("Aucun format audio exploitable trouvé.")

                audio = max(audio_formats, key=lambda f: f.get("abr") or 0)
                url = audio.get("url")
                if not url:
                    raise AudioExtractionError("L'URL du flux audio est absente.")
                return url
        except AudioExtractionError:
            raise
        except Exception as error:
            raise AudioExtractionError(
                "Impossible de récupérer le flux audio."
            ) from error

    def prepare(self) -> None:
        self.url = self._extract_url()

    def stream(self) -> Iterator[bytes]:
        if self.url is None:
            self.prepare()

        ffmpeg_cmd = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-i",
            self.url,
            "-f",
            "mp3",
            "-ab",
            "128k",
            "-ac",
            "2",
            "-ar",
            "44100",
            "-vn",
            "-loglevel",
            "error",
            "pipe:1",
        ]
        try:
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except OSError as error:
            raise AudioStreamError("Impossible de démarrer FFmpeg.") from error

        try:
            stdout = process.stdout
            if stdout is None:
                raise AudioStreamError("FFmpeg n'a pas ouvert de sortie audio.")

            for chunk in iter(lambda: stdout.read(4096), b""):
                yield chunk

            if process.wait() != 0:
                raise AudioStreamError("FFmpeg n'a pas pu convertir le flux audio.")
        finally:
            if process.stdout is not None:
                process.stdout.close()
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
