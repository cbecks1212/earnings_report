from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from ..database.tables import Users
import httpx
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
project_id = "orbital-kit-400022"
mailgun_api_key = "MAILGUN_API_KEY"
mailgun_name = f"projects/{project_id}/secrets/{mailgun_api_key}/versions/latest"
mailgun_api_encoded_value = client.access_secret_version(request={"name" : mailgun_name})
mailgun_api_value = mailgun_api_encoded_value.payload.data.decode("UTF-8")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')

SECRET_KEY = 'jfdfjfdjffuefufhfdjf3mmvfhnjhffj39jf'
ALGORITHM = 'HS256'

def authenticate_user(email: str, password:str, db):
    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not has confirmed email")
    
    return user

def create_access_token(email: str, user_id: int, expiry_time: timedelta):
    encode = {"sub" : email, "id" : user_id}
    expires = datetime.now(timezone.utc) + expiry_time
    encode.update({"exp": expires, "type" : "bearer"})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def create_confirmation_token(email: str, user_id: int, expiry_time: timedelta):
    encode = {"sub" : email, "id" : user_id}
    expires = datetime.now(timezone.utc) + expiry_time
    encode.update({"exp": expires, "type" : "confirmation"})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_type(token: str, token_type: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    return email

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        type = payload.get("type")
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        
        if type is None or type != 'bearer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token Type")

        return {"email" : email, "id" : user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
async def send_email(to: str, subject: str, body: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/sandboxffc385fec1b247799626c6b28a81f2c3.mailgun.org/messages",
                auth=("api", mailgun_api_value),
                data={
                    "from": f"Curt Beck <mailgun@sandboxffc385fec1b247799626c6b28a81f2c3.mailgun.org>",
                    "to": [to],
                    "subject": subject,
                    "text": body
                }
            )
            response.raise_for_status()
            return response
        except:
            httpx.HTTPStatusError


        
