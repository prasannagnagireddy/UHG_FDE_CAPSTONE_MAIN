CREATE TABLE IF NOT EXISTS claims (
 case_id TEXT PRIMARY KEY, claimant_name TEXT NOT NULL, policy_number TEXT,
 claim_type TEXT NOT NULL, claim_amount NUMERIC NOT NULL, description TEXT DEFAULT '',
 status TEXT NOT NULL DEFAULT 'submitted', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS claim_documents (
 document_id BIGSERIAL PRIMARY KEY, case_id TEXT REFERENCES claims(case_id), filename TEXT NOT NULL,
 content_text TEXT DEFAULT '', doc_type TEXT DEFAULT 'unknown', confidence NUMERIC DEFAULT 0.0,
 created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS claim_summaries (
 summary_id BIGSERIAL PRIMARY KEY, case_id TEXT REFERENCES claims(case_id), summary_json JSONB NOT NULL,
 created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS workflow_tasks (
 task_id BIGSERIAL PRIMARY KEY, case_id TEXT REFERENCES claims(case_id), task_type TEXT,
 status TEXT DEFAULT 'open', assigned_to TEXT, due_at TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS approval_requests (
 approval_id BIGSERIAL PRIMARY KEY, case_id TEXT REFERENCES claims(case_id), request_json JSONB,
 decision TEXT, approver TEXT, rationale TEXT, created_at TIMESTAMPTZ DEFAULT NOW(), decided_at TIMESTAMPTZ);
CREATE TABLE IF NOT EXISTS audit_log (
 audit_id BIGSERIAL PRIMARY KEY, case_id TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
 before_state JSONB, after_state JSONB, reason TEXT, trace_id TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS agent_runs (
 run_id BIGSERIAL PRIMARY KEY, case_id TEXT, agent_name TEXT, outcome JSONB, duration_ms INTEGER,
 created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS evaluation_results (
 result_id BIGSERIAL PRIMARY KEY, run_label TEXT, metrics_json JSONB, passed BOOLEAN,
 created_at TIMESTAMPTZ DEFAULT NOW());
