from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from ..database.tables import Users

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = 'jfdfjfdjffuefufhfdjf3mmvfhnjhffj39jf'
ALGORITHM = 'HS256'

def authenticate_user(username: str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    return user

def create_access_token(username: str, user_id: int, expiry_time: timedelta):
    encode = {"sub" : username, "id" : user_id}
    expires = datetime.now(timezone.utc) + expiry_time
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        return {"username" : username, "id" : user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


        
