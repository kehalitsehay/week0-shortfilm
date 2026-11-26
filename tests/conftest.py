import os
import shutil
import pytest


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("HS_OUT", str(tmp_path / "outputs"))
    monkeypatch.setenv("HS_RUNS", str(tmp_path / "runs.jsonl"))
    monkeypatch.setenv("OFFLINE", "1")
    return tmp_path


needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
