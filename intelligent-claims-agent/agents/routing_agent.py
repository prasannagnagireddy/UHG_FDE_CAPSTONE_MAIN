def suggest_route(case:dict,summary:dict)->dict:
    amount=float(case.get('claim_amount') or 0)
    if summary.get('risks'): return {'route':'manual_review','reason':'Risk flags or document validation issues','human_review_required':True}
    if amount>=250000: return {'route':'senior_adjuster','reason':'High value claim amount','human_review_required':True}
    return {'route':'adjuster_queue','reason':'Routine initial routing suggestion','human_review_required':True}
