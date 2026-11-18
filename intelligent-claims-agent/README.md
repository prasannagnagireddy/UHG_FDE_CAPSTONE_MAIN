# Intelligent Claims Processing & Case Management Agent

Complete phased capstone starter (Phase 1–8) for local development in VS Code. It is an **engineering scaffold with working deterministic claim workflow, persistence, tool servers, UI, tests and evaluation**. AI calls are optional and local via Ollama; all claim decisions remain human-only.


## Included
- Four FastMCP servers: case, policy, documents, workflow
- Five specialist modules (intake, document, summary, routing, SLA/comms)
- Supervisor/workflow routing with safeguards and human-review statuses
- Streamlit workspace (submit claims, queue, case detail, approvals, audit)
- PostgreSQL + pgvector Compose, Keycloak, Mailpit, Ollama; Phoenix observability service is documented as optional
- Evaluation pack with 30 synthetic cases, metrics and release gate
- Tests and architecture documentation

> **Local resource note:** Ollama is optional and disabled from automatic startup/model pulling. Start it only after checking available RAM. The project works in deterministic mode without a model.


## Windows + VS Code setup
1. Install Python 3.11+, VS Code, Git and Docker Desktop. Install Ollama only if you want local LLM calls.
2. Extract this ZIP to `C:\Projects\intelligent-claims-agent` and open that folder in VS Code.
3. In VS Code Terminal (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If activation is blocked in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
4. Copy `.env.example` to `.env` and keep local credentials local. The example is for development only.
5. Start the database and supporting services:
```powershell
docker compose up -d postgres keycloak mailpit
```
6. Initialize tables:
```powershell
python -m database.init_db
```
7. Start the app:
```powershell
streamlit run ui/app.py
```
Open the Streamlit URL printed in the terminal (usually http://localhost:8501).

## Optional Ollama
Install Ollama separately, check system RAM, then choose a model appropriate for your machine. Example commands (only if hardware supports it):
```powershell
ollama --version
ollama pull llama3.1:8b
```
For low-memory machines, use a smaller model variant. Do not pull large models blindly. `.env` setting `LLM_ENABLED=false` keeps deterministic mode.

## MCP servers
Each server can be run independently for MCP Inspector or an MCP client:
```powershell
python -m mcp_servers.case_mcp
python -m mcp_servers.policy_mcp
python -m mcp_servers.documents_mcp
python -m mcp_servers.workflow_mcp
```
These are stdio servers and normally wait silently for client messages. Run one per terminal when testing.

## Tests and evaluation
```powershell
pytest -v
python -m evaluation.run_evaluation
```
The evaluation writes `evaluation/results/latest_report.json` and fails the release gate if mandatory thresholds are missed. The bundled dataset is synthetic and designed for development, not real insurance decisions.

## Useful Docker commands
```powershell
docker compose ps
docker compose logs -f postgres
docker compose down
# Preserve DB data by default. To delete local DB data too (destructive):
# docker compose down -v
```

## Phased implementation order
- Phase 1: foundation, config, database, case MCP
- Phase 2: policy/documents/workflow MCP services
- Phase 3: specialist agent modules and permitted tool boundaries
- Phase 4: graph-style supervisor and safeguards/human checkpoint state
- Phase 5: Streamlit workspace
- Phase 6: Docker services, auth/email/model integration points
- Phase 7: audit, tracing hooks, evaluation pack and release gate
- Phase 8: integration, tests, documentation and demo walkthrough

## Safety and scope
- Synthetic sample data only. Never use actual claimant PII in this demo.
- Agents may flag, summarize, extract, recommend routing and request human review; they **cannot approve, deny or settle** claims.
- Authentication and email delivery are development scaffolds. Do not expose services or use sample credentials in production.
- Document OCR via Docling is optional and may require additional system dependencies. Current extraction uses safe text-first fallback.
- MCP servers are local tool interfaces; run them only in trusted environments.

