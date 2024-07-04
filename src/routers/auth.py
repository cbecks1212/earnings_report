from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..models.auth import CreateUserRequest, Token
from ..database.tables import Users
from ..database.utils import get_db
from ..auth.utils import authenticate_user, create_access_token, create_confirmation_token, get_token_type, send_email

router = APIRouter(tags=['auth'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,create_user_request: CreateUserRequest, request: Request):
    create_user_model = Users(
        email = create_user_request.email,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        confirmed = False,
        is_active = True
    )

    db.add(create_user_model)
    db.commit()
    request_url = request.url_for(
                "confirm_email", token=create_confirmation_token(create_user_model.email, create_user_model.id, timedelta(minutes=1440))
            )
    await send_email(create_user_model.email, "Please Confirm Your Email", f"Thank you for registering for the Earnings API. To complete the registration, please confirm your email by clicking the link below:\n\n{request_url}")
    return {"message" : f"User created. A verification email has been sent to {create_user_model.email}. To complete your registration, please click the link in the email."}

@router.get("/confirm/{token}")
async def confirm_email(token: str, db: db_dependency):
    email = get_token_type(token, "confirmation")
    result = db.query(Users).filter(Users.email == email).first()
    if result is not None:
        result.confirmed = True
        db.commit()

        return {"message": "Your account has now been successfully verified!"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify account.")


@router.post("/token", response_model=Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.email, user.id, timedelta(minutes=20))
    return {"access_token" : token, "token_type" : "bearer"}
