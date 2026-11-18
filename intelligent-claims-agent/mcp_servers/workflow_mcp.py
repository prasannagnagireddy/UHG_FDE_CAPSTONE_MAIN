from mcp_servers._compat import FastMCP
mcp=FastMCP('workflow-mcp')
@mcp.tool()
def get_workload()->dict:
    """Return demo adjuster workload counts."""
    return {"adjusters":[{"id":"ADJ-01","open_cases":8,"capacity":15},{"id":"ADJ-02","open_cases":11,"capacity":15}],"note":"Synthetic workload data"}
@mcp.tool()
def assign_case(case_id:str, adjuster_id:str)->dict:
    """Suggest an assignment; persist integration should be added for production."""
    return {"case_id":case_id,"adjuster_id":adjuster_id,"assignment_status":"suggested","human_confirmation_required":True}
@mcp.tool()
def request_approval(case_id:str, approval_brief:str)->dict:
    """Create a human approval request payload; never make the decision."""
    return {"case_id":case_id,"approval_status":"awaiting_human","brief":approval_brief}
@mcp.tool()
def schedule_sla(case_id:str, due_hours:int=48)->dict:
    """Return an SLA due-time suggestion (scheduling persistence is a TODO integration)."""
    return {"case_id":case_id,"due_hours":max(1,due_hours),"scheduled":False,"status":"suggested"}
@mcp.tool()
def send_notification(recipient:str, subject:str, body:str)->dict:
    """Report email delivery as queued only in demo; connect SMTP/Mailpit for sending."""
    return {"queued":False,"mailpit_available_at":"http://localhost:8025","recipient":recipient,"subject":subject,"reason":"SMTP integration not configured"}
@mcp.tool()
def request_documents(case_id:str, missing_documents:list)->dict:
    """Build a missing-document request draft."""
    return {"case_id":case_id,"requested":missing_documents,"draft":"Please provide the requested supporting documents."}
if __name__=='__main__': mcp.run(transport='stdio')
