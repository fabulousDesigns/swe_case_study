from fastapi import Depends, FastAPI

from app.config import get_settings
from app.routes import customers, orders, token_router
from app.utils.utils import VerifyToken

app = FastAPI()

settings = get_settings()

if settings.env == "test":
    def get_test_token_verifier():
        async def mock_verify(*args, **kwargs):
            return {"sub": "test_user"}
        verifier = VerifyToken()
        verifier.verify = mock_verify
        return verifier

    app.dependency_overrides[VerifyToken] = get_test_token_verifier

app.include_router(token_router.router, tags=["token"], prefix="/api")
app.include_router(customers.router, tags=["customers"], prefix="/api")
app.include_router(orders.router, tags=["orders"], prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)