from agents.supervisor import process_claim

def supervisor_node(state:dict)->dict:
    return {'next_step':'intake_agent','agent_hops':state.get('agent_hops',0)+1}
def intake_node(state:dict)->dict: return {'stage_results':{**state.get('stage_results',{}),'intake':'complete'}}
def document_node(state:dict)->dict: return {'stage_results':{**state.get('stage_results',{}),'documents':'complete'}}
def summary_node(state:dict)->dict: return {'stage_results':{**state.get('stage_results',{}),'summary':'complete'}}
def routing_node(state:dict)->dict: return {'stage_results':{**state.get('stage_results',{}),'routing':'complete'}}
def sla_comms_node(state:dict)->dict: return {'stage_results':{**state.get('stage_results',{}),'sla_comms':'complete'}}
def await_documents_node(state:dict)->dict: return {'case_status':'awaiting_documents'}
def human_review_node(state:dict)->dict: return {'case_status':'awaiting_human_approval'}
def manual_review_node(state:dict)->dict: return {'case_status':'manual_review'}
def finalize_node(state:dict)->dict:
    if not state.get('decision'): return {'case_status':'awaiting_human_approval'}
    return {'case_status':'decision_received'}
