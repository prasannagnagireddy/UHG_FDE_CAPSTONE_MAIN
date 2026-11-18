import json

from apscheduler.schedulers.background import BackgroundScheduler

from database.connection import connection
from claims_governance.monitoring import log_event


def check_sla_breaches():
    breached = []

    with connection() as conn:
        rows = conn.execute(
            """
            UPDATE workflow_tasks
            SET status = 'breached'
            WHERE status = 'open'
              AND due_at IS NOT NULL
              AND due_at < NOW()
            RETURNING task_id, case_id, task_type, due_at
            """
        ).fetchall()

        for row in rows:
            task = dict(row)
            breached.append(task)

            conn.execute(
                """
                INSERT INTO audit_log
                (case_id, actor, action, reason, after_state)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                """,
                (
                    str(task["case_id"]),
                    "sla_scheduler",
                    "sla_breach_detected",
                    "Workflow task deadline exceeded",
                    json.dumps(task, default=str),
                ),
            )

    for task in breached:
        log_event(
            "sla_breach_detected",
            case_id=str(task["case_id"]),
            actor="sla_scheduler",
            details=task,
        )

    return len(breached)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        check_sla_breaches,
        trigger="interval",
        minutes=5,
        id="claims_sla_monitor",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()
    return scheduler