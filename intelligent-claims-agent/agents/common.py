from config.settings import settings

def maybe_llm(prompt:str)->str|None:
    """Optional Ollama call; deterministic workflow is the fallback."""
    if not settings.llm_enabled: return None
    try:
        import httpx
        r=httpx.post(settings.ollama_base_url.rstrip('/')+'/api/generate',json={'model':settings.ollama_model,'prompt':prompt,'stream':False},timeout=90)
        r.raise_for_status(); return r.json().get('response','').strip()
    except Exception as e:
        return f"LLM unavailable; deterministic fallback used ({type(e).__name__})."
