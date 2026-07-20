import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import youtube_media
from lib.subproc import SubprocResult


class TestYouTubeMediaDoctor(unittest.TestCase):
    def test_reports_ready_only_when_ytdlp_executes_and_js_runtime_exists(self):
        def which(name):
            return f"/usr/bin/{name}" if name in {"yt-dlp", "ffmpeg", "node", "agent-browser"} else None

        with mock.patch.object(youtube_media.shutil, "which", side_effect=which):
            report = youtube_media.doctor(
                config={"LAST30DAYS_TRANSCRIBE_AUDIO_DIR": "/missing"},
                runner=lambda *_args, **_kwargs: SubprocResult(0, "2026.07.04\n", ""),
            )

        self.assertEqual("ready", report["youtube"]["state"])
        self.assertEqual("2026.07.04", report["youtube"]["yt_dlp_version"])
        self.assertEqual("node", report["youtube"]["js_runtime"])
        self.assertFalse(report["transcribe_audio"]["available"])

    def test_reports_missing_broken_and_js_runtime_warning_states(self):
        with mock.patch.object(youtube_media.shutil, "which", return_value=None):
            missing = youtube_media.doctor(config={})
        self.assertEqual("missing", missing["youtube"]["state"])
        self.assertFalse(missing["ok"])

        with mock.patch.object(
            youtube_media.shutil,
            "which",
            side_effect=lambda name: "/usr/bin/yt-dlp" if name == "yt-dlp" else None,
        ):
            broken = youtube_media.doctor(
                config={},
                runner=lambda *_args, **_kwargs: SubprocResult(1, "", "failed"),
            )
            warning = youtube_media.doctor(
                config={},
                runner=lambda *_args, **_kwargs: SubprocResult(0, "2026.07.04\n", ""),
            )

        self.assertEqual("broken", broken["youtube"]["state"])
        self.assertEqual("warning", warning["youtube"]["state"])
        self.assertIn("JavaScript runtime", warning["youtube"]["reason"])


class TestYouTubeMediaDownload(unittest.TestCase):
    def test_download_is_single_video_and_resolution_bounded(self):
        with tempfile.TemporaryDirectory() as output_dir:
            artifact = Path(output_dir) / "video [abc123].mp4"

            def runner(command, timeout):
                artifact.write_bytes(b"video")
                return SubprocResult(0, f"{artifact}\n", "")

            result = youtube_media.download(
                "https://www.youtube.com/watch?v=abc123",
                output_dir,
                max_height=720,
                runner=runner,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(str(artifact), result["path"])
        command = result["command"]
        self.assertIn("--no-playlist", command)
        self.assertIn("height<=720", " ".join(command))
        self.assertIn("--merge-output-format", command)
        self.assertEqual("--", command[-2])

    def test_download_failure_is_structured_and_leaves_no_claimed_artifact(self):
        with tempfile.TemporaryDirectory() as output_dir:
            result = youtube_media.download(
                "https://www.youtube.com/watch?v=abc123",
                output_dir,
                runner=lambda *_args, **_kwargs: SubprocResult(1, "", "blocked"),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("video_download_failed", result["error"])
        self.assertNotIn("path", result)


class TestYouTubeMediaTranscript(unittest.TestCase):
    def test_caption_success_never_invokes_local_asr(self):
        with tempfile.TemporaryDirectory() as output_dir:
            asr = mock.Mock()
            result = youtube_media.transcript(
                "https://youtu.be/abc123",
                output_dir,
                config={},
                caption_fetcher=lambda *_args, **_kwargs: "caption words",
                asr_fetcher=asr,
            )
            text = Path(result["path"]).read_text(encoding="utf-8").strip()

        self.assertEqual("captions", result["provider"])
        self.assertEqual("caption words", text)
        asr.assert_not_called()

    def test_caption_absence_invokes_local_transcribe_audio(self):
        with tempfile.TemporaryDirectory() as output_dir:
            result = youtube_media.transcript(
                "https://www.youtube.com/watch?v=abc123",
                output_dir,
                config={},
                caption_fetcher=lambda *_args, **_kwargs: None,
                asr_fetcher=lambda *_args, **_kwargs: {
                    "text": "locally transcribed words",
                    "provider": "transcribe-audio",
                },
            )
            text = Path(result["path"]).read_text(encoding="utf-8").strip()

        self.assertEqual("transcribe-audio", result["provider"])
        self.assertEqual("locally transcribed words", text)


class TestYouTubeSubscriptions(unittest.TestCase):
    class FakeClient:
        def __init__(self, result):
            self.result = result
            self.requests = []

        def acquire_workspace(self, request):
            self.requests.append(request)
            return mock.Mock(operator_visible_state="ready")

        def prepare_site_tab(self, *_args, **_kwargs):
            return True

        def act(self, *_args, **_kwargs):
            return None

        def evaluate(self, *_args, **_kwargs):
            return self.result

    def test_returns_normalized_authenticated_subscription_videos(self):
        client = self.FakeClient({
            "state": "ok",
            "items": [{
                "video_id": "abc123",
                "title": "A useful video",
                "channel": "Subscribed Channel",
                "url": "https://www.youtube.com/watch?v=abc123",
                "published": "3 hours ago",
                "duration": "3:17",
            }],
        })
        result = youtube_media.subscriptions(limit=10, config={}, client=client)

        self.assertTrue(result["ok"])
        self.assertEqual("abc123", result["items"][0]["video_id"])
        request = client.requests[0]
        self.assertEqual("stealthcdp-default", request.profile_id)
        self.assertEqual("remote_headed", request.browser_host)
        self.assertEqual("rdp_gateway", request.view_provider)

    def test_signed_out_is_a_clear_failure(self):
        client = self.FakeClient({"state": "signed_out", "items": []})
        result = youtube_media.subscriptions(config={}, client=client)
        self.assertFalse(result["ok"])
        self.assertEqual("youtube_sign_in_required", result["error"])


class TestYouTubeMediaCli(unittest.TestCase):
    def test_json_failure_uses_nonzero_exit_and_structured_output(self):
        script = Path(__file__).parents[1] / "skills" / "last30days" / "scripts" / "youtube_media.py"
        result = subprocess.run(
            [sys.executable, str(script), "--json", "download", "https://example.com/video"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )

        self.assertEqual(1, result.returncode)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual("ValueError", payload["error"])


if __name__ == "__main__":
    unittest.main()
