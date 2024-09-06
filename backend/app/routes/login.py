from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from app.methods.auth import authenticate_user, create_access_token, validate_token

router = APIRouter()


@router.post("/login", tags=["login"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"], "level": user["level"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify_token", tags=["login"])
async def verify_token(request: dict):
    if validate_token(request):
        return {"status": True}
    else:
        print("Token is invalid")
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )