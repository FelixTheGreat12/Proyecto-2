from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import create_access_token, verify_password
from helpers.helpers import get_profesor_by_username
from schemas.token import Token
from core.mongo import get_db 
from helpers.helpers import get_alumno_by_username

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(db: AsyncIOMotorClient = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    usuario = await get_profesor_by_username(form_data.username, db)
    if not usuario or not verify_password(form_data.password, usuario['hashed_password']):
        print(verify_password(form_data.password, usuario['hashed_password']))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": usuario['username']}, expires_delta=timedelta(minutes=30)
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token)
async def login_for_access_token(db: AsyncIOMotorClient = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    profesor = await get_profesor_by_username(form_data.username, db)
    if not profesor:
        alumno = get_alumno_by_username(form_data.username, db)
        if not alumno:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username o password incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, alumno['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username o password incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": alumno['username']}, expires_delta=timedelta(minutes=30)
        )
        return Token(access_token=access_token, token_type="bearer")
    if not verify_password(form_data.password, profesor['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": profesor['username']}, expires_delta=timedelta(minutes=30)
    )
    return Token(access_token=access_token, token_type="bearer")