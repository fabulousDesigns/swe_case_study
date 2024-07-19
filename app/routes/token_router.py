import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import get_settings

router = APIRouter()
settings = get_settings()

class TokenRequest(BaseModel):
    grant_type: str = "client_credentials"
    client_id: str = settings.auth0_client_id
    client_secret: str = settings.auth0_client_secret
    audience: str = settings.auth0_api_audience

@router.post("/token")
async def get_token(request: TokenRequest):
    token_url = f"https://{settings.auth0_domain}/oauth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=request.dict())

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
