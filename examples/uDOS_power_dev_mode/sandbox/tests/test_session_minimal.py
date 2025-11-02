
import glob, re

def test_last_session_has_core_events():
    paths = sorted(glob.glob("sandbox/logs/session-*.log"))
    assert paths, "No session logs found"
    last = paths[-1]
    text = open(last, "r", encoding="utf-8", errors="ignore").read()
    assert "STATUS" in text
    assert re.search(r"REPAIR\\s+(auto|check)", text)
    assert "TREE" in text
