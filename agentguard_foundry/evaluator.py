import os
from schemas import EvaluationResponse

class GovernanceEvaluator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "mock-key")

    def evaluate(self, prompt: str) -> EvaluationResponse:
        # Core evaluation logic
        lower_prompt = prompt.lower()
        if "leak" in lower_prompt or "secret" in lower_prompt or "key" in lower_prompt:
            return EvaluationResponse(
                is_safe=False,
                risk_score=0.95,
                reason="Potential credential/secret exfiltration detected."
            )
        return EvaluationResponse(
            is_safe=True,
            risk_score=0.05,
            reason="Prompt complies with safety guidelines."
        )
