"""Timestamp fallback for posts without a matching logged post operation."""
import pytest

from commsfail.annotators.standard.bundle import seen_table
from commsfail.trace import Trace


@pytest.mark.parametrize("posted,ended,matched", [
    ("09:59:59", "10:00:10", False),
    ("10:00:00", "10:00:10", True),
    ("10:00:10", "10:00:10", True),
    ("10:00:11", "10:00:10", True),
    ("10:00:11.001", "10:00:10", False),
    ("11:00:00", None, True),
    ("09:59:59", None, False),
])
def test_unlinked_post_uses_turn_time_window(posted, ended, matched):
    def ts(time):
        return f"2026-10-08T{time}Z" if time else None

    trace = Trace(room={}, seats=[], posts=[{
        "seq": 4, "who": "codex-1", "role": "agent", "created_at": ts(posted),
    }], wakes=[{
        "seat": "codex-1", "turn": 1, "through": 3,
        "started_at": ts("10:00:00"), "ended_at": ts(ended),
    }])
    row = seen_table(trace)[4]
    assert row["turn"] == (1 if matched else None)
    assert row["seen"] == (3 if matched else None)
