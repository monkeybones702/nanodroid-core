from pydantic import BaseModel, Field

class EvaluationRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt to evaluate")
    context: str = Field(default="", description="Additional context or system prompt")

class EvaluationResponse(BaseModel):
    is_safe: bool
    risk_score: float
    reason: str
