from mcp_servers._compat import FastMCP
from database.connection import connection
import uuid, json
mcp=FastMCP("case-mcp")
@mcp.tool()
def register_case(claimant_name:str, claim_type:str, claim_amount:float, policy_number:str='', description:str='') -> dict:
    """Register a synthetic claim and return its assigned case identifier."""
    if not claimant_name.strip() or claim_amount <= 0: return {"ok":False,"error":"Name and positive claim amount required"}
    case_id='CLM-'+uuid.uuid4().hex[:10].upper()
    with connection() as conn:
        conn.execute("INSERT INTO claims(case_id,claimant_name,policy_number,claim_type,claim_amount,description,status) VALUES(%s,%s,%s,%s,%s,%s,%s)", (case_id,claimant_name.strip(),policy_number,claim_type,float(claim_amount),description,'submitted'))
        conn.execute("INSERT INTO audit_log(case_id,actor,action,reason) VALUES(%s,%s,%s,%s)", (case_id,'intake-agent','claim_registered','New claim submitted'))
    return {"ok":True,"case_id":case_id,"status":"submitted"}
@mcp.tool()
def get_case(case_id:str)->dict:
    """Fetch a case record by case identifier."""
    with connection() as conn:
        row=conn.execute("SELECT case_id,claimant_name,policy_number,claim_type,claim_amount,description,status,created_at FROM claims WHERE case_id=%s",(case_id,)).fetchone()
    return dict(row) if row else {"ok":False,"error":"Case not found"}
@mcp.tool()
def find_similar_cases(claim_type:str, claim_amount:float, policy_number:str='')->list:
    """Find nearby claim amounts and matching policy numbers for duplicate review."""
    with connection() as conn:
        rows=conn.execute("SELECT case_id,claim_type,claim_amount,policy_number,status FROM claims WHERE claim_type=%s AND (ABS(claim_amount-%s) < %s OR (%s <> '' AND policy_number=%s)) ORDER BY created_at DESC LIMIT 10",(claim_type,claim_amount,max(100.0,claim_amount*0.05),policy_number,policy_number)).fetchall()
    return [dict(r) for r in rows]
@mcp.tool()
def save_summary(case_id:str, summary_json:str)->dict:
    """Store a JSON case summary version."""
    data=json.loads(summary_json)
    with connection() as conn:
        conn.execute("INSERT INTO claim_summaries(case_id,summary_json) VALUES(%s,%s)",(case_id,json.dumps(data)))
    return {"ok":True,"saved":True}
@mcp.tool()
def save_case_note(case_id:str, note:str, actor:str='reviewer')->dict:
    """Record an append-only note in audit history."""
    with connection() as conn:
        conn.execute("INSERT INTO audit_log(case_id,actor,action,reason) VALUES(%s,%s,%s,%s)",(case_id,actor,'case_note',note))
    return {"ok":True}
if __name__=='__main__': mcp.run(transport='stdio')
