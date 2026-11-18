from agents.supervisor import process_claim
def test_missing_docs_pause():
    c={'case_id':'T1','claimant_name':'A','policy_number':'AUTO-DEMO','claim_type':'collision','claim_amount':1000}
    assert process_claim(c,[])['status']=='awaiting_documents'
def test_clean_pack_reaches_human_gate():
    c={'case_id':'T2','claimant_name':'A','policy_number':'AUTO-DEMO','claim_type':'collision','claim_amount':1000}
    d=[{'filename':'claim_form.txt','text':'claim form claimant A policy AUTO-DEMO amount 1000'},{'filename':'invoice.txt','text':'invoice total 1000'},{'filename':'photo.txt','text':'photo of damage'}]
    result=process_claim(c,d)
    assert result['status'] in ('awaiting_human_approval','manual_review')
    assert result['decision'] is None
