"""Authentication endpoints for login, OAuth2 token issue, and profile check."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import authenticate_user, create_access_token, get_current_user
from app.schemas import LoginRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    # JSON login endpoint used by the frontend dashboard.
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Incorrect username or password.",
                "code": "AUTH_INVALID_CREDENTIALS",
            },
        )

    token = create_access_token(data={"sub": payload.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
def issue_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2-compatible token endpoint used by Swagger "Authorize" flow.
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": "Incorrect username or password.",
                "code": "AUTH_INVALID_CREDENTIALS",
            },
        )

    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_me(current_user: str = Depends(get_current_user)):
    # Lightweight endpoint to validate bearer tokens.
    return {"username": current_user}