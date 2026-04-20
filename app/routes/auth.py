from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import authenticate_user, create_access_token, get_current_user
from app.schemas import LoginRequest, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
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


@router.get("/me")
def read_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}