def summarize(case:dict,document_result:dict,policy_result:dict)->dict:
    risks=[]
    if document_result.get('missing_documents'): risks.append({'type':'missing_documents','items':document_result['missing_documents']})
    if document_result.get('low_confidence_documents'): risks.append({'type':'low_document_confidence','items':document_result['low_confidence_documents']})
    if policy_result.get('coverage')=='flagged': risks.append({'type':'coverage_flag','details':policy_result})
    return {'agent':'summary','case_facts':{k:case.get(k) for k in ('case_id','claimant_name','policy_number','claim_type','claim_amount')},'documents':document_result.get('classified',[]),'extracted_fields':document_result.get('extracted_fields',{}),'risks':risks,'policy_reference':policy_result.get('policy_reference'),'disclaimer':'AI-assisted summary only; verify evidence and policy wording.'}
