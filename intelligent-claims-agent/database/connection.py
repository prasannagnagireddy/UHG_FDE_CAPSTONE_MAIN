from contextlib import contextmanager
from config.settings import settings
try:
    import psycopg
except ImportError:
    psycopg = None
@contextmanager
def connection():
    if psycopg is None:
        raise RuntimeError("Install psycopg with: pip install -r requirements.txt")
    conn = psycopg.connect(settings.database_url, row_factory=psycopg.rows.dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()
def audit(case_id, actor, action, reason='', before=None, after=None):
    import json
    with connection() as conn:
        conn.execute("INSERT INTO audit_log(case_id,actor,action,before_state,after_state,reason) VALUES (%s,%s,%s,%s,%s,%s)",
            (case_id, actor, action, json.dumps(before) if before else None, json.dumps(after) if after else None, reason))
