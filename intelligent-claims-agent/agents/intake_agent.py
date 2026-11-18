from mcp_servers.case_mcp import find_similar_cases

def run_intake(claim:dict)->dict:
    duplicate_hint=[]
    # Database duplicate check is available via MCP tool; gracefully skip if DB is not ready.
    try: duplicate_hint=find_similar_cases(claim.get('claim_type',''),float(claim.get('claim_amount',0)),claim.get('policy_number',''))
    except Exception: pass
    return {'agent':'intake','registered':bool(claim.get('case_id')),'duplicate_candidates':duplicate_hint,'flags':['possible_duplicate'] if duplicate_hint else []}
