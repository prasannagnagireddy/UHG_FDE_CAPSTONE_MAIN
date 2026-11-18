
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agents.intake_agent import run_intake
from agents.document_agent import analyze_documents
from agents.summary_agent import summarize
from agents.routing_agent import suggest_route
from agents.sla_comms_agent import plan_sla

# MCP client
from agents.mcp_client import call_tool

# Existing local policy function is retained as fallback
from mcp_servers.policy_mcp import check_coverage_logic


# =========================================================
# WORKFLOW STATE
# =========================================================

class ClaimState(TypedDict, total=False):
    case: dict
    documents_input: list[dict]

    intake: dict
    documents: dict
    policy: Any
    policy_source: str
    mcp_error: str

    summary: Any
    routing: dict
    sla: dict

    status: str
    decision: Any
    human_decision_required: bool
    error: str


# =========================================================
# GRAPH NODES
# =========================================================

def intake_node(state: ClaimState) -> dict:
    case = state.get("case", {})
    result = run_intake(case)
    return {"intake": result}


def document_node(state: ClaimState) -> dict:
    documents = state.get("documents_input", [])
    result = analyze_documents(documents)
    return {"documents": result}


def policy_node(state: ClaimState) -> dict:
    """
    Call the real Policy MCP tool first.
    If MCP is unavailable, fall back to existing local policy logic.
    """

    case = state.get("case", {})

    policy_id = case.get("policy_number", "AUTO-DEMO")
    claim_type = case.get("claim_type", "")
    claim_amount = float(case.get("claim_amount", 0) or 0)

    # -----------------------------
    # Primary: MCP policy tool
    # -----------------------------
    try:
        result = call_tool(
            "policy_check_coverage",
            {
                "policy_id": policy_id,
                "claim_type": claim_type,
                "claim_amount": claim_amount,
            },
        )

        return {
            "policy": result,
            "policy_source": "mcp",
        }

    except Exception as mcp_exception:
        # -----------------------------
        # Fallback: existing function
        # -----------------------------
        try:
            fallback_result = check_coverage_logic(
                policy_id,
                claim_type,
                claim_amount,
            )

            return {
                "policy": fallback_result,
                "policy_source": "local_fallback",
                "mcp_error": str(mcp_exception),
            }

        except Exception as fallback_exception:
            return {
                "policy": {
                    "status": "policy_check_failed",
                    "message": "Unable to complete policy verification.",
                },
                "policy_source": "failed",
                "mcp_error": str(mcp_exception),
                "error": str(fallback_exception),
            }


def summary_node(state: ClaimState) -> dict:
    case = state.get("case", {})
    documents = state.get("documents", {})
    policy = state.get("policy", {})

    result = summarize(case, documents, policy)
    return {"summary": result}


def routing_node(state: ClaimState) -> dict:
    case = state.get("case", {})
    summary = state.get("summary")

    result = suggest_route(case, summary)
    return {"routing": result}


def sla_node(state: ClaimState) -> dict:
    case = state.get("case", {})
    routing = state.get("routing", {})

    result = plan_sla(
        case.get("case_id", "unknown"),
        routing.get("route", "manual_review"),
    )

    return {"sla": result}


def finalize_node(state: ClaimState) -> dict:
    documents = state.get("documents", {})
    routing = state.get("routing", {})

    if documents.get("missing_documents"):
        status = "awaiting_documents"

    elif routing.get("route") == "manual_review":
        status = "manual_review"

    else:
        status = "awaiting_human_approval"

    # Safety: AI never makes final approval or denial.
    return {
        "status": status,
        "decision": None,
        "human_decision_required": True,
    }


# =========================================================
# GRAPH BUILD
# =========================================================

def build_claim_graph(checkpointer=None):
    workflow = StateGraph(ClaimState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("documents", document_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("routing", routing_node)
    workflow.add_node("sla", sla_node)
    workflow.add_node("finalize", finalize_node)

    workflow.add_edge(START, "intake")
    workflow.add_edge("intake", "documents")
    workflow.add_edge("documents", "policy")
    workflow.add_edge("policy", "summary")
    workflow.add_edge("summary", "routing")
    workflow.add_edge("routing", "sla")
    workflow.add_edge("sla", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile(checkpointer=checkpointer)


# =========================================================
# CHECKPOINT SUPPORT
# =========================================================

memory_checkpointer = MemorySaver()
claim_graph = build_claim_graph(memory_checkpointer)


# =========================================================
# PUBLIC API - STREAMLIT COMPATIBILITY
# =========================================================

def process_claim(case: dict, documents: list[dict]) -> dict:
    """
    Run the LangGraph claims workflow.

    Interface remains compatible with the existing Streamlit UI:
        process_claim(case, documents)

    AI-assisted processing only.
    Final approval or denial requires a human.
    """

    case_id = case.get("case_id", "unknown")

    initial_state: ClaimState = {
        "case": case,
        "documents_input": documents,
        "decision": None,
        "human_decision_required": True,
    }

    config = {
        "configurable": {
            "thread_id": str(case_id),
        }
    }

    result = claim_graph.invoke(
        initial_state,
        config=config,
    )

    return {
        "case": result.get("case", case),
        "intake": result.get("intake", {}),
        "documents": result.get("documents", {}),
        "policy": result.get("policy", {}),
        "policy_source": result.get("policy_source", "unknown"),
        "mcp_error": result.get("mcp_error"),
        "summary": result.get("summary", {}),
        "routing": result.get("routing", {}),
        "sla": result.get("sla", {}),
        "status": result.get("status", "manual_review"),
        "decision": None,
        "human_decision_required": True,
    }
