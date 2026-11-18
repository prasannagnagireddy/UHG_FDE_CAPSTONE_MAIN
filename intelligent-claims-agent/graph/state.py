from typing import TypedDict,Any
class ClaimState(TypedDict,total=False):
    case_id:str; messages:list; case_status:str; next_step:str; agent_hops:int
    stage_results:dict[str,Any]; documents:list; extracted_fields:dict; case_summary:dict
    risks:list; missing_documents:list; approval:dict; decision:str; errors:list; token_usage:dict
