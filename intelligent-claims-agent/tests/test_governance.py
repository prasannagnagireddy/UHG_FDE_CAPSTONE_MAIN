import json
from datetime import datetime, timedelta, timezone

import pytest

from claims_governance import monitoring


@pytest.fixture
def temp_logs(monkeypatch, tmp_path):
    monkeypatch.setattr(monitoring, "LOG_DIR", tmp_path)
    monkeypatch.setattr(monitoring, "EVENT_LOG", tmp_path / "events.jsonl")
    monkeypatch.setattr(monitoring, "METRICS_LOG", tmp_path / "metrics.jsonl")


def test_log_event_writes_json(temp_logs):
    row = monitoring.log_event(
        "claim_submitted",
        case_id="TEST-001",
        actor="tester",
        details={"amount": 5000},
    )

    assert row["event_type"] == "claim_submitted"
    assert row["case_id"] == "TEST-001"

    saved = json.loads(monitoring.EVENT_LOG.read_text().strip())
    assert saved["actor"] == "tester"
    assert saved["details"]["amount"] == 5000


def test_monitor_agent_success(temp_logs):
    with monitoring.monitor_agent("test_agent", "TEST-002"):
        result = 2 + 2

    assert result == 4
    metrics = json.loads(monitoring.METRICS_LOG.read_text().strip())
    assert metrics["agent"] == "test_agent"
    assert metrics["success"] is True


def test_monitor_agent_failure(temp_logs):
    with pytest.raises(ValueError):
        with monitoring.monitor_agent("failing_agent", "TEST-003"):
            raise ValueError("synthetic test error")

    metrics = json.loads(monitoring.METRICS_LOG.read_text().strip())
    assert metrics["success"] is False
    assert "synthetic test error" in metrics["error"]


def test_sla_status_on_track():
    deadline = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    result = monitoring.sla_status(deadline)

    assert result["status"] == "on_track"
    assert result["seconds_remaining"] > 0


def test_sla_status_breached():
    deadline = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    result = monitoring.sla_status(deadline)

    assert result["status"] == "breached"
    assert result["seconds_remaining"] < 0


def test_notification_is_draft_only(temp_logs):
    draft = monitoring.build_notification_draft(
        "TEST-004",
        "Synthetic Claimant",
        "missing_documents",
    )

    assert draft["sent"] is False
    assert draft["requires_human_review"] is True
    assert "TEST-004" in draft["subject"]
    assert "additional documents" in draft["body"].lower()