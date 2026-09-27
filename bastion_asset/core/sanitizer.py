import re

def sanitize_prompt(text: str) -> tuple[str, bool]:
    modified = False
    sk_pattern = r'sk-[a-zA-Z0-9-_]{20,}'
    if re.search(sk_pattern, text):
        text = re.sub(sk_pattern, "[REDACTED_API_KEY]", text)
        modified = True
        
    secret_pattern = r'(?i)(secret|password|api_key|token)\s*[:=]\s*\S+'
    if re.search(secret_pattern, text):
        text = re.sub(secret_pattern, r'\1=[REDACTED]', text)
        modified = True
        
    return text, modified
