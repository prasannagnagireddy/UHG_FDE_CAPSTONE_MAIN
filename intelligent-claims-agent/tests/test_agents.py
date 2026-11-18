from agents.routing_agent import suggest_route
def test_risky_claim_routes_manual():
    assert suggest_route({'claim_amount':1000},{'risks':['missing']})['route']=='manual_review'
def test_high_value_routes_senior():
    assert suggest_route({'claim_amount':300000},{'risks':[]})['route']=='senior_adjuster'
