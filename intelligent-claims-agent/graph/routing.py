ALLOWED={'intake_agent','document_agent','summary_agent','routing_agent','sla_comms_agent','await_documents','human_review','finalize','manual_review'}
def route_guard(state:dict,next_step:str)->str:
    if next_step not in ALLOWED:
        return 'manual_review'
    if next_step in {'routing_agent','sla_comms_agent','human_review'} and state.get('missing_documents'):
        return 'await_documents'
    if next_step in {'routing_agent','sla_comms_agent','human_review','finalize'} and not state.get('case_summary'):
        return 'manual_review'
    if next_step=='finalize' and not state.get('decision'):
        return 'human_review'
    return next_step
