from datetime import datetime,timezone,timedelta

def plan_sla(case_id:str, route:str, hours:int=48)->dict:
    return {'case_id':case_id,'route':route,'deadline':(datetime.now(timezone.utc)+timedelta(hours=hours)).isoformat(),'notification_draft':'Claim received. We will review the information and contact you if more details are required.','status':'proposed'}
