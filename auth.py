from fastapi import Request, HTTPException

AUTH_TOKEN = "secure_591_token"
ENABLE_AUTH = False

def check_auth(request: Request):
    token = request.headers.get("X-Auth-Token") or request.query_params.get("token")
    if ENABLE_AUTH and token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")
