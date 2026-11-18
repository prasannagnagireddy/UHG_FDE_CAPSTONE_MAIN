from agents.supervisor import process_claim

def run_workflow(case:dict,documents:list[dict])->dict:
    # A dependency-light orchestration entrypoint. LangGraph graph wiring is an extension point.
    return process_claim(case,documents)
