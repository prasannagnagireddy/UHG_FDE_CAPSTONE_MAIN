
"""Governance and observability helpers for the claims capstone."""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from contextlib import contextmanager

LOG_DIR = Path(os.getenv("CLAIMS_LOG_DIR", "logs"))
EVENT_LOG = LOG_DIR / "governance_events.jsonl"
METRICS_LOG = LOG_DIR / "agent_metrics.jsonl"


def _utcnow():
    return datetime.now(timezone.utc)


def log_event(event_type: str, *, case_id: str | None = None,
              actor: str = "system", details=None):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": _utcnow().isoformat(),
        "event_type": event_type,
        "case_id": case_id,
        "actor": actor,
        "details": details or {},
    }
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    return row


def log_agent_metric(agent_name: str, *, duration_seconds: float,
                     success: bool, case_id=None, error=None):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp_utc": _utcnow().isoformat(),
        "agent": agent_name,
        "duration_seconds": round(float(duration_seconds), 4),
        "success": bool(success),
        "case_id": case_id,
        "error": str(error) if error else None,
    }
    with METRICS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

    log_event(
        "agent_execution",
        case_id=case_id,
        actor=agent_name,
        details={
            "success": row["success"],
            "duration_seconds": row["duration_seconds"],
            "error": row["error"],
        },
    )
    return row


@contextmanager
def monitor_agent(agent_name: str, case_id=None):
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        log_agent_metric(
            agent_name,
            duration_seconds=time.perf_counter() - start,
            success=False,
            case_id=case_id,
            error=exc,
        )
        raise
    else:
        log_agent_metric(
            agent_name,
            duration_seconds=time.perf_counter() - start,
            success=True,
            case_id=case_id,
        )


def calculate_sla_deadline(created_at=None, hours: int = 72):
    created = created_at or _utcnow()
    if isinstance(created, str):
        created = datetime.fromisoformat(created.replace("Z", "+00:00"))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return (created + timedelta(hours=hours)).isoformat()


def sla_status(deadline_iso: str, now=None):
    now = now or _utcnow()
    deadline = datetime.fromisoformat(deadline_iso.replace("Z", "+00:00"))
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    remaining = (deadline - now).total_seconds()
    return {
        "deadline": deadline.isoformat(),
        "seconds_remaining": int(remaining),
        "status": (
            "breached" if remaining < 0
            else "due_soon" if remaining <= 6 * 3600
            else "on_track"
        ),
    }


def build_notification_draft(case_id: str, recipient_name: str,
                            message_type="status_update"):
    if message_type == "missing_documents":
        subject = f"Additional documents requested - claim {case_id}"
        body = (
            f"Hello {recipient_name},\n\n"
            f"We are reviewing your claim ({case_id}) and need additional "
            "documents. Please contact your claims representative for the "
            "required items.\n\n"
            "This is a draft for human review; it has not been sent."
        )
    else:
        subject = f"Claim status update - {case_id}"
        body = (
            f"Hello {recipient_name},\n\n"
            f"Your claim ({case_id}) is under review. A claims representative "
            "will review the submitted information and contact you if further "
            "details are needed.\n\n"
            "This is a draft for human review; it has not been sent."
        )

    log_event(
        "communication_draft_created",
        case_id=case_id,
        actor="communication_helper",
        details={"type": message_type},
    )
    return {
        "subject": subject,
        "body": body,
        "sent": False,
        "requires_human_review": True,
    }


def phoenix_available():
    try:
        import phoenix  # noqa: F401
        return True
    except Exception:
        return False
