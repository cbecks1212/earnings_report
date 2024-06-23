from fastapi import APIRouter, Depends
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..models.auth import CreateUserRequest, Token
from ..database.tables import Users
from ..database.utils import get_db
from ..auth.utils import authenticate_user, create_access_token

router = APIRouter(tags=['auth'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
    return "User added"

@router.post("/token", response_model=Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token" : token, "token_type" : "bearer"}
