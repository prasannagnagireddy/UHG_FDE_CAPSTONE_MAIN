import agents.supervisor as supervisor


def setup_mock_agents(monkeypatch):
    monkeypatch.setattr(
        supervisor, "run_intake",
        lambda case: {"received": True}
    )

    monkeypatch.setattr(
        supervisor, "analyze_documents",
        lambda docs: {"missing_documents": [], "classified": []}
    )

    monkeypatch.setattr(
        supervisor, "check_coverage_logic",
        lambda policy, claim_type, amount: {"coverage": "potentially_covered"}
    )

    monkeypatch.setattr(
        supervisor, "summarize",
        lambda case, docs, policy: "Synthetic claim summary"
    )

    monkeypatch.setattr(
        supervisor, "suggest_route",
        lambda case, summary: {"route": "adjuster_queue"}
    )

    monkeypatch.setattr(
        supervisor, "plan_sla",
        lambda case_id, route: {"sla_status": "within_sla"}
    )


def test_graph_contains_required_nodes():
    graph_nodes = supervisor.claim_graph.get_graph().nodes

    expected = {
        "intake",
        "documents",
        "policy",
        "summary",
        "routing",
        "sla",
        "finalize",
    }

    assert expected.issubset(set(graph_nodes))


def test_graph_processes_claim_and_requires_human(monkeypatch):
    setup_mock_agents(monkeypatch)

    case = {
        "case_id": "TEST-GRAPH-001",
        "policy_number": "TEST-POLICY",
        "claim_type": "collision",
        "claim_amount": 25000,
    }

    result = supervisor.process_claim(case, [])

    assert result["status"] == "awaiting_human_approval"
    assert result["decision"] is None
    assert result["human_decision_required"] is True
    assert result["routing"]["route"] == "adjuster_queue"


def test_graph_missing_documents_status(monkeypatch):
    setup_mock_agents(monkeypatch)

    monkeypatch.setattr(
        supervisor,
        "analyze_documents",
        lambda docs: {"missing_documents": ["invoice"]}
    )

    case = {
        "case_id": "TEST-GRAPH-002",
        "policy_number": "TEST-POLICY",
        "claim_type": "collision",
        "claim_amount": 10000,
    }

    result = supervisor.process_claim(case, [])

    assert result["status"] == "awaiting_documents"
    assert result["human_decision_required"] is True
    assert result["decision"] is None