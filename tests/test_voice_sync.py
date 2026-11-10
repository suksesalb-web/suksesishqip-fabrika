"""Narration split: cuts land on real pauses, in order, and a bad split is caught."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fabrika"))
import reel


def test_prefers_long_pauses_between_beats():
    texts = ["Një ditë do ta lësh. Me inat.", "Por pa kursime, inati mbaron.", "Ik me plan."]
    # short pauses inside beats (0.25 s), long ones between beats (0.6 s)
    pauses = [(1.2, 0.25), (2.4, 0.6), (3.6, 0.25), (4.9, 0.6)]
    assert reel.pick_cuts(pauses, [reel._speech_weight(t) for t in texts], 6.0) == [2.4, 4.9]


def test_not_enough_pauses():
    assert reel.pick_cuts([(1.0, 0.3)], [10, 10, 10], 5.0) is None


def test_sync_check_flags_wrong_split():
    texts = ["Tetë orë në një punë.", "Një ditë do ta lësh.", "Me plan, jo me inat."]
    good = [(None, 1.6), (None, 1.5), (None, 1.6)]
    bad = [(None, 0.6), (None, 3.0), (None, 1.6)]
    assert reel.sync_ok(good, texts)[0]
    assert not reel.sync_ok(bad, texts)[0]
