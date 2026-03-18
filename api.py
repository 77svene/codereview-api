from fastapi import FastAPI, HTTPException, Header
    from pydantic import BaseModel
    import httpx
    import os
    from datetime import datetime, timedelta
    
    app = FastAPI(title="CodeReview AI API")
    
    # Simple rate limiting store (use Redis in production)
    usage_store = {}
    
    class ReviewRequest(BaseModel):
        code: str
        language: str = "python"
        options: dict = {}
    
    class ReviewResponse(BaseModel):
        id: str
        status: str
        issues: list
        metrics: dict
        summary: str
    
    API_KEYS = {
        "free_trial": {"plan": "trial", "monthly_limit": 10, "used": 0},
    }
    
    async def check_api_key(x_api_key: str = Header(None)):
        if not x_api_key:
            raise HTTPException(status_code=401, detail="API key required")
        
        if x_api_key not in API_KEYS:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        key_data = API_KEYS[x_api_key]
        if key_data["used"] >= key_data["monthly_limit"]:
            raise HTTPException(status_code=429, detail="Monthly limit reached. Upgrade to Pro.")
        
        return x_api_key
    
    @app.post("/v1/review", response_model=ReviewResponse)
    async def review_code(request: ReviewRequest, api_key: str = Depends(check_api_key)):
        """Submit code for AI-powered review."""
        
        # Track usage
        API_KEYS[api_key]["used"] += 1
        
        # In production, call actual AI model
        issues = []
        metrics = {
            "complexity": 5,
            "maintainability": 8.5,
            "lines": len(request.code.split("\n"))
        }
        
        # Simple static analysis
        if "eval(" in request.code:
            issues.append({"severity": "high", "type": "security", "message": "Avoid using eval()"})
        if "TODO" in request.code or "FIXME" in request.code:
            issues.append({"severity": "low", "type": "maintainability", "message": "Unfinished TODO/FIXME found"})
        
        return ReviewResponse(
            id=f"review_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="completed",
            issues=issues,
            metrics=metrics,
            summary=f"Code looks good! Found {len(issues)} issue(s)."
        )
    
    @app.get("/v1/usage")
    async def get_usage(api_key: str = Depends(check_api_key)):
        """Get current usage statistics."""
        key_data = API_KEYS[api_key]
        return {
            "plan": key_data["plan"],
            "used": key_data["used"],
            "limit": key_data["monthly_limit"],
            "remaining": key_data["monthly_limit"] - key_data["used"]
        }
    