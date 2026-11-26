import copy
import json
import pytest
from pipeline.core import cache, config, storyboard
from pipeline.core.retry import retry
from pipeline.core.stage import Job, execute
from pipeline.core import runlog


def test_cache_key_is_stable_and_sensitive():
    a = {"prompt": "x", "seed": 1}
    assert cache.key(a) == cache.key({"seed": 1, "prompt": "x"})
    assert cache.key(a) != cache.key({"prompt": "x", "seed": 2})


def test_storyboard_valid():
    sb = storyboard.load()
    assert 8 <= len(sb.shots) <= 12
    assert 60 <= sb.runtime_estimate() <= 90


def test_schema_rejects_shot_without_reason():
    sb = storyboard.load()
    bad = copy.deepcopy(sb.data)
    del bad["shots"][0]["reason"]
    with pytest.raises(storyboard.StoryboardError, match="reason"):
        storyboard.check(storyboard.Storyboard(bad))


def test_unknown_character_rejected():
    bad = copy.deepcopy(storyboard.load().data)
    bad["shots"][0]["characters"] = ["nobody"]
    with pytest.raises(storyboard.StoryboardError, match="unknown character"):
        storyboard.check(storyboard.Storyboard(bad))


def test_retry_then_succeed():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise IOError("boom")
        return "ok"

    assert retry(flaky, sleep=lambda s: None) == "ok" and calls["n"] == 3


def test_execute_caches_logs_and_falls_back(env):
    made = []

    def produce(out):
        made.append(1)
        raise RuntimeError("quota")

    def fallback(out):
        out.write_text("x")
        return {"model": "fallback-model"}

    job = Job("t", "a", {"i": 1}, "txt", produce, fallback=fallback, sleep=lambda s: None)
    execute([job])
    assert len(made) == 3 and job.path.exists()          # 3 attempts, then fallback
    execute([job])                                        # second run = cache hit, no produce
    assert len(made) == 3
    rows = runlog.read_all()
    assert rows[0]["fallback_used"] == "fallback-model" and "quota" in rows[0]["error"]
    assert rows[1]["cache_hit"] is True
