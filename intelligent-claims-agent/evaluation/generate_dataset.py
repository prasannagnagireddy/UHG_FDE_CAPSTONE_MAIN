"""Generate 30 deterministic, fictional claim input records (no real personal data)."""
import json, random
from pathlib import Path

random.seed(26)
claim_types = ["collision", "property_damage", "theft", "medical"]
scenarios = [
    ("clean_complete", "complete documents and consistent fields", "normal_review"),
    ("policy_mismatch", "policy number differs across documents", "flag_mismatch"),
    ("missing_invoice", "repair invoice missing", "request_information"),
    ("low_confidence_docs", "low confidence document classification", "human_review"),
    ("duplicate_claim", "duplicate case reference", "flag_duplicate"),
    ("high_value_claim", "amount above demo threshold", "escalate_review"),
    ("date_inconsistency", "incident dates inconsistent", "flag_date_conflict"),
    ("suspicious_description", "suspicious or contradictory narrative", "human_review"),
]
first_names = ["Aarav", "Diya", "Ishaan", "Meera", "Kabir", "Anaya", "Rohan", "Tara", "Vivaan", "Nisha"]
last_names = ["Reddy", "Sharma", "Patel", "Khan", "Rao", "Das", "Gupta", "Singh", "Iyer", "Nair"]
records=[]
for i in range(1,31):
    scenario = scenarios[(i-1)%8]
    amount = random.choice([12000, 28500, 45000, 76000, 135000, 220000])
    record = {
      "synthetic_id": f"SYN-{i:04d}", "scenario": scenario[0], "scenario_description": scenario[1],
      "expected_handling": scenario[2], "claimant_name": f"{first_names[(i-1)%len(first_names)]} {last_names[(i*3)%len(last_names)]}",
      "policy_number": f"DEMO-POL-{10000+i}", "claim_type": claim_types[(i-1)%len(claim_types)],
      "claim_amount": amount, "incident_date": f"2026-{((i-1)%12)+1:02d}-{((i-1)%27)+1:02d}",
      "description": f"Fictional {claim_types[(i-1)%len(claim_types)]} claim test case {i}; synthetic scenario data only.",
      "documents": ["claim_form"] if i%3==0 else ["claim_form", "invoice"],
      "human_decision_required": True
    }
    if scenario[0]=="policy_mismatch": record["document_policy_number"] = "DEMO-POL-MISMATCH"
    if scenario[0]=="missing_invoice": record["documents"] = ["claim_form"]
    if scenario[0]=="low_confidence_docs": record["document_confidence"] = 0.32
    if scenario[0]=="duplicate_claim": record["duplicate_of"] = "SYN-0001"
    if scenario[0]=="high_value_claim": record["claim_amount"] = 450000
    if scenario[0]=="date_inconsistency": record["document_incident_date"] = "2026-01-01"
    if scenario[0]=="suspicious_description": record["description"] += " Conflicting test notes intentionally included."
    records.append(record)
out=Path(__file__).with_name("data")/"synthetic_claims_30.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {len(records)} synthetic claims to {out}")
