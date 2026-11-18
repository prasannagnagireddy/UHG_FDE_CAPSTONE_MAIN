from agents.supervisor import process_claim
from .metrics import score_cases
def run(dataset):
    results=[]
    for pack in dataset:
        outcome=process_claim(pack['claim'],pack['documents'])
        results.append({'case_id':pack['id'],'scenario':pack['scenario'],'actual_status':outcome['status'],'expected_status':pack['expected']['status']})
    report=score_cases(results); report['case_results']=results; return report
