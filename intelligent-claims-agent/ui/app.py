
import streamlit as st
import pandas as pd
import uuid
import json
from decimal import Decimal
from datetime import date, datetime

from agents.supervisor import process_claim
from database.connection import connection
from claims_governance.scheduler import start_scheduler
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
@st.cache_resource
def get_scheduler():
    return start_scheduler()

scheduler = get_scheduler()
st.set_page_config(
    page_title="Intelligent Claims Workspace",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Intelligent Claims Processing & Case Management")
st.caption("Synthetic capstone workspace · AI-assisted only · Human decisions required")

menu = st.sidebar.radio(
    "Workspace",
    [
        "Dashboard",
        "Submit Claim",
        "Claims Queue",
        "Case Workspace",
        "Approvals",
        "Audit History"
    ]
)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def get_db():
    return connection()


def is_mapping_row(row):
    return hasattr(row, "keys")


def rows_df(rows, columns, rename=None):
    if not rows:
        return pd.DataFrame(
            columns=list(rename.values()) if rename else columns
        )

    if is_mapping_row(rows[0]):
        df = pd.DataFrame([dict(r) for r in rows])
        if rename:
            df = df.rename(columns=rename)
        return df

    df = pd.DataFrame(rows, columns=columns)

    if rename:
        df = df.rename(columns=rename)

    return df


def row_dict(row, columns=None):
    if row is None:
        return None

    if is_mapping_row(row):
        return dict(row)

    if columns:
        return dict(zip(columns, row))

    return {str(i): value for i, value in enumerate(row)}


def safe_json(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return str(value)


def parse_json(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value

    return value


def status_label(status):
    labels = {
        "awaiting_documents": "📄 Awaiting Documents",
        "awaiting_human_approval": "👤 Awaiting Human Approval",
        "manual_review": "👤 Manual Review",
        "adjuster_queue": "🧑‍💼 Adjuster Queue",
        "pending_review": "⏳ Pending Review",
        "approved": "✅ Approved (Human Decision)",
        "rejected": "❌ Rejected (Human Decision)",
        "registered": "📝 Registered",
    }

    return labels.get(status, status or "Unknown")


# --------------------------------------------------
# CLAIM RESULT DISPLAY
# --------------------------------------------------
def show_claim_result(result, case_id):

    st.success(f"Claim successfully registered — {case_id}")

    st.subheader("Claim Processing Overview")

    a, b, c = st.columns(3)

    a.metric(
        "Claim Status",
        status_label(result.get("status", "Unknown"))
    )

    b.metric("Human Decision", "Required")
    c.metric("AI Decision", "Not Final")

    st.info(
        "AI processing is complete. Human review is required. "
        "No automatic approval or rejection was performed."
    )

    # ---------------- SUMMARY ----------------
    summary = result.get("summary", {})

    st.subheader("📝 Claim Summary")

    if isinstance(summary, dict):
        for k, v in summary.items():

            label = k.replace("_", " ").title()

            if isinstance(v, (dict, list)):
                st.write(f"**{label}:**")
                st.json(v)
            else:
                st.write(f"**{label}:** {v}")
    else:
        st.write(summary)

    # ---------------- DOCUMENTS ----------------
    documents = result.get("documents", {}) or {}

    classified = documents.get("classified", []) or []
    missing = documents.get("missing_documents", []) or []
    extracted = documents.get("extracted_fields", {}) or {}
    valid = documents.get("valid", False)

    st.subheader("📎 Document Analysis")

    x, y, z = st.columns(3)

    x.metric("Documents Uploaded", len(classified))
    y.metric("Document Validation", "Valid" if valid else "Incomplete")
    z.metric("Missing Documents", len(missing))

    if classified:
        st.dataframe(
            pd.DataFrame(classified),
            use_container_width=True,
            hide_index=True
        )

    if missing:
        st.warning("Missing documents: " + ", ".join(map(str, missing)))
    else:
        st.success("No missing documents detected by the current checks.")

    if extracted:
        with st.expander("Extracted Information"):
            st.json(extracted)

    # ---------------- POLICY NUMBER CHECK ----------------
    entered_policy = result.get("policy_reference")

    if entered_policy and isinstance(extracted, dict):

        doc_policies = []

        for file_fields in extracted.values():
            if (
                isinstance(file_fields, dict)
                and file_fields.get("policy_number")
            ):
                doc_policies.append(
                    str(file_fields["policy_number"]).strip()
                )

        mismatches = sorted({
            p for p in doc_policies
            if p and p != str(entered_policy).strip()
        })

        if mismatches:
            st.warning(
                "Policy number mismatch: claim uses **"
                + str(entered_policy)
                + "**, while document(s) show **"
                + ", ".join(mismatches)
                + "**. Please verify manually."
            )

    # ---------------- POLICY ----------------
    policy = result.get("policy", {}) or {}

    st.subheader("📋 Policy Analysis")

    if isinstance(policy, dict):

        st.write(
            f"**Coverage Status:** {policy.get('coverage', 'Unknown')}"
        )

        if policy.get("covered_type") is not None:
            st.write(
                "**Claim Type Covered:** "
                + ("Yes" if policy.get("covered_type") else "No")
            )

        if policy.get("within_demo_limit") is not None:
            st.write(
                "**Within Demonstration Limit:** "
                + ("Yes" if policy.get("within_demo_limit") else "No")
            )

        if policy.get("reason"):
            st.write(f"**Reason:** {policy.get('reason')}")

        if policy.get("human_review_required", True):
            st.warning(
                "Policy analysis is advisory and requires human verification."
            )

    # ---------------- ROUTING ----------------
    routing = result.get("routing", {}) or {}

    st.subheader("🔀 Routing")

    if isinstance(routing, dict):
        st.write(
            f"**Recommended Route:** {routing.get('route', 'Not specified')}"
        )
        st.write(
            f"**Reason:** {routing.get('reason', 'Not specified')}"
        )

    # ---------------- SLA ----------------
    sla = result.get("sla", {}) or {}

    st.subheader("⏰ SLA & Communication")

    if isinstance(sla, dict):

        if sla.get("deadline"):
            st.write(f"**Proposed Deadline:** {sla.get('deadline')}")

        if sla.get("notification"):
            st.write("**Notification Draft:**")
            st.info(sla.get("notification"))

    # ---------------- DEBUG ----------------
    with st.expander("🔧 Technical Details (Developer Debug)"):
        st.json(result)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if menu == "Dashboard":

    st.header("📊 Claims Dashboard")

    try:
        with get_db() as conn:

            count_rows = conn.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM claims
                GROUP BY status
                ORDER BY status
                """
            ).fetchall()

            total_row = conn.execute(
                "SELECT COUNT(*) AS total FROM claims"
            ).fetchone()

        total_dict = row_dict(total_row, ["total"])

        total = (
            total_dict.get("total", next(iter(total_dict.values()), 0))
            if total_dict
            else 0
        )

        count_df = rows_df(
            count_rows,
            ["Status", "Count"],
            {
                "status": "Status",
                "count": "Count"
            }
        )

        c1, c2 = st.columns(2)

        c1.metric("Claims Submitted", int(total or 0))
        c2.metric("Statuses Tracked", len(count_df))

        st.subheader("Claims by Status")

        if not count_df.empty:
            st.dataframe(
                count_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No claims have been submitted yet.")

    except Exception as e:
        st.error(f"Dashboard database error: {repr(e)}")

    st.info("No automated approval or denial is performed.")


# --------------------------------------------------
# SUBMIT CLAIM
# --------------------------------------------------
elif menu == "Submit Claim":

    st.header("📝 Submit a Synthetic Claim")

    with st.form("claim_submit", clear_on_submit=False):

        name = st.text_input("Claimant Name")
        policy_no = st.text_input("Policy Number", value="AUTO-DEMO")

        claim_type = st.selectbox(
            "Claim Type",
            [
                "collision",
                "comprehensive",
                "glass",
                "medical",
                "property",
                "other"
            ]
        )

        amount = st.number_input(
            "Claim Amount (₹)",
            min_value=1.0,
            value=10000.0,
            step=500.0
        )

        description = st.text_area("Incident Description")

        uploaded = st.file_uploader(
            "Upload Evidence Documents",
            accept_multiple_files=True,
            help="Upload claim forms, invoices, reports or other evidence."
        )

        submit = st.form_submit_button("Register and Process Claim")

    if submit:

        if not name.strip():
            st.error("Claimant name is required.")

        else:

            case_id = "CLM-" + uuid.uuid4().hex[:10].upper()

            claim = {
                "case_id": case_id,
                "claimant_name": name.strip(),
                "policy_number": policy_no.strip(),
                "claim_type": claim_type,
                "claim_amount": amount,
                "description": description,
            }

            docs = []

            for f in (uploaded or []):

                file_text = f.getvalue().decode(
                    "utf-8",
                    errors="ignore"
                )

                docs.append({
                    "filename": f.name,
                    "text": file_text
                })

            try:

                with st.spinner("AI agents are processing your claim..."):
                    result = process_claim(claim, docs)

                with get_db() as conn:

                    # Save claim
                    conn.execute(
                        """
                        INSERT INTO claims
                        (
                            case_id,
                            claimant_name,
                            policy_number,
                            claim_type,
                            claim_amount,
                            description,
                            status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            case_id,
                            name.strip(),
                            policy_no.strip(),
                            claim_type,
                            amount,
                            description,
                            result.get(
                                "status",
                                "awaiting_human_approval"
                            ),
                        ),
                    )

                    # Audit submission
                    conn.execute(
                        """
                        INSERT INTO audit_log
                        (case_id, actor, action, reason, after_state)
                        VALUES (%s, %s, %s, %s, %s::jsonb)
                        """,
                        (
                            case_id,
                            "streamlit-user",
                            "claim_submitted",
                            "UI form",
                            json.dumps(
                                {"status": result.get("status")},
                                default=safe_json
                            ),
                        ),
                    )

                    # Save summary
                    conn.execute(
                        """
                        INSERT INTO claim_summaries
                        (case_id, summary_json)
                        VALUES (%s, %s::jsonb)
                        """,
                        (
                            case_id,
                            json.dumps(
                                result.get("summary", {}),
                                default=safe_json
                            ),
                        ),
                    )

                st.session_state["last_result"] = result
                st.session_state["last_case_id"] = case_id
                st.session_state["claim_submit_success"] = True

            except Exception as e:

                st.error(
                    f"Claim processing or persistence failed: {repr(e)}"
                )

                st.warning(
                    "No success confirmation is shown unless saving completes."
                )

    # Display previously processed claim
    if (
        "last_result" in st.session_state
        and "last_case_id" in st.session_state
    ):
        show_claim_result(
            st.session_state["last_result"],
            st.session_state["last_case_id"]
        )


# --------------------------------------------------
# CLAIMS QUEUE
# --------------------------------------------------
elif menu == "Claims Queue":

    st.header("📂 Claims Queue")

    try:

        with get_db() as conn:

            rows = conn.execute(
                """
                SELECT
                    case_id,
                    claimant_name,
                    claim_type,
                    claim_amount,
                    status,
                    created_at
                FROM claims
                ORDER BY created_at DESC
                """
            ).fetchall()

        queue_df = rows_df(
            rows,
            [
                "Case ID",
                "Claimant",
                "Type",
                "Amount (₹)",
                "Status",
                "Created"
            ],
            {
                "case_id": "Case ID",
                "claimant_name": "Claimant",
                "claim_type": "Type",
                "claim_amount": "Amount (₹)",
                "status": "Status",
                "created_at": "Created"
            }
        )

        if not queue_df.empty:

            if "Status" in queue_df:
                queue_df["Status"] = queue_df["Status"].map(status_label)

            st.dataframe(
                queue_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No claims found in database.")

    except Exception as e:
        st.error(f"Unable to load claims queue: {repr(e)}")


# --------------------------------------------------
# CASE WORKSPACE
# --------------------------------------------------
elif menu == "Case Workspace":

    st.header("🔍 Case Workspace")

    case_id = st.text_input(
        "Enter Case ID",
        value=st.session_state.get("workspace_case_id", "")
    )

    if st.button("Load Case", key="load_case") and case_id.strip():

        st.session_state["workspace_case_id"] = case_id.strip()

        try:

            with get_db() as conn:

                claim_row = conn.execute(
                    "SELECT * FROM claims WHERE case_id=%s",
                    (case_id.strip(),)
                ).fetchone()

                summary_row = conn.execute(
                    """
                    SELECT summary_json, created_at
                    FROM claim_summaries
                    WHERE case_id=%s
                    ORDER BY summary_id DESC
                    LIMIT 1
                    """,
                    (case_id.strip(),)
                ).fetchone()

                audit_rows = conn.execute(
                    """
                    SELECT actor, action, reason, created_at
                    FROM audit_log
                    WHERE case_id=%s
                    ORDER BY audit_id
                    """,
                    (case_id.strip(),)
                ).fetchall()

            claim = row_dict(claim_row)

            summary = row_dict(
                summary_row,
                ["summary_json", "created_at"]
            )

            st.session_state["workspace_claim"] = claim
            st.session_state["workspace_summary"] = summary
            st.session_state["workspace_audit"] = audit_rows

        except Exception as e:
            st.error(f"Unable to load case: {repr(e)}")

    if st.session_state.get("workspace_case_id"):

        claim = st.session_state.get("workspace_claim")
        summary = st.session_state.get("workspace_summary")
        audit_rows = st.session_state.get("workspace_audit", [])

        if claim:

            st.subheader("Claim Details")
            st.json(claim)

        else:
            st.warning("No matching case found for the entered Case ID.")

        if summary:

            st.subheader("Latest AI Summary")

            summary_value = parse_json(
                summary.get("summary_json")
            )

            st.json(summary_value)

            st.caption(
                f"Summary created: {summary.get('created_at', 'Unknown')}"
            )

        else:
            st.info("No AI summary available for this claim.")

        st.subheader("Audit Trail")

        if audit_rows:

            audit_df = rows_df(
                audit_rows,
                ["Actor", "Action", "Reason", "Time"],
                {
                    "actor": "Actor",
                    "action": "Action",
                    "reason": "Reason",
                    "created_at": "Time"
                }
            )

            st.dataframe(
                audit_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No audit events found for this case yet.")


# --------------------------------------------------
# APPROVALS
# --------------------------------------------------
elif menu == "Approvals":

    st.header("👤 Human Approval Center")

    st.warning(
        "AI cannot approve or reject claims. This demo records decisions "
        "entered by a human. Authentication and role enforcement are not yet implemented."
    )

    case_id = st.text_input("Case ID for Review")

    decision = st.selectbox(
        "Human Decision",
        [
            "approve",
            "reject",
            "request_more_information"
        ]
    )

    rationale = st.text_area("Decision Rationale (Required)")
    approver = st.text_input("Approver Identity")

    if st.button("Record Decision"):

        if not all([
            case_id.strip(),
            rationale.strip(),
            approver.strip()
        ]):
            st.error("Case ID, approver and rationale are required.")

        else:

            try:

                recorded = False

                with get_db() as conn:

                    exists = conn.execute(
                        "SELECT case_id FROM claims WHERE case_id=%s",
                        (case_id.strip(),)
                    ).fetchone()

                    if exists:

                        # Record human decision
                        conn.execute(
                            """
                            INSERT INTO approval_requests
                            (
                                case_id,
                                request_json,
                                decision,
                                approver,
                                rationale,
                                decided_at
                            )
                            VALUES (%s, %s::jsonb, %s, %s, %s, NOW())
                            """,
                            (
                                case_id.strip(),
                                json.dumps({
                                    "source": "Streamlit manual entry"
                                }),
                                decision,
                                approver.strip(),
                                rationale.strip()
                            )
                        )

                        # Audit decision
                        conn.execute(
                            """
                            INSERT INTO audit_log
                            (case_id, actor, action, reason)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                case_id.strip(),
                                approver.strip(),
                                "human_decision_recorded",
                                rationale.strip()
                            )
                        )

                        recorded = True

                if recorded:
                    st.success("Human decision recorded in audit history.")
                else:
                    st.error("Case ID was not found. Decision was not recorded.")

            except Exception as e:
                st.error(f"Unable to record decision: {repr(e)}")


# --------------------------------------------------
# AUDIT HISTORY
# --------------------------------------------------
elif menu == "Audit History":

    st.header("📜 Audit History")

    case_filter = st.text_input("Filter by Case ID (Optional)")

    try:

        with get_db() as conn:

            if case_filter.strip():

                rows = conn.execute(
                    """
                    SELECT
                        audit_id,
                        case_id,
                        actor,
                        action,
                        reason,
                        created_at
                    FROM audit_log
                    WHERE case_id=%s
                    ORDER BY audit_id DESC
                    """,
                    (case_filter.strip(),)
                ).fetchall()

            else:

                rows = conn.execute(
                    """
                    SELECT
                        audit_id,
                        case_id,
                        actor,
                        action,
                        reason,
                        created_at
                    FROM audit_log
                    ORDER BY audit_id DESC
                    LIMIT 300
                    """
                ).fetchall()

        audit_df = rows_df(
            rows,
            [
                "Audit ID",
                "Case ID",
                "Actor",
                "Action",
                "Reason",
                "Timestamp"
            ],
            {
                "audit_id": "Audit ID",
                "case_id": "Case ID",
                "actor": "Actor",
                "action": "Action",
                "reason": "Reason",
                "created_at": "Timestamp"
            }
        )

        if not audit_df.empty:

            st.dataframe(
                audit_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No audit records found.")

    except Exception as e:
        st.error(f"Audit database unavailable: {repr(e)}")
