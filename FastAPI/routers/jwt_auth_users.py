# autenticación con encriptación

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "592a959a27f3d086ce82cb8ca051d18d2921d6acff47e1a47f55288233359c50"

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str

users_db = {
    "yisuslalala": {
        "username": "yisuslalala",
        "full_name": "Jesús Quiñones",
        "email": "yisuslalala1.00@gmail.com",
        "disabled": False,
        "password": "$2a$12$zBSMoBI5L/9OJJg.cEipuOh7Oxbfqsdah9ALLgSAa2VdtW3apZ6yi"
    },
    "Wardo": {
        "username": "Wardo",
        "full_name": "Eduardo Mata",
        "email": "wardo1.00@gmail.com",
        "disabled": False,
        "password": "$2a$12$8cTOxMHap5xEFlzQb3Gh3ulZM1qnMZNui00QWDzNE/cgdU5pvXZgS"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

async def auth_user(token: str = Depends(oauth2)):
    
    exception = HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED, 
            detail = "Credenciales de autenticación inválidas", 
            headers = {"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception
    
    return search_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST, 
            detail = "Usuario inactivo")
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm= Depends()):
    user_db = users_db.get(form.username)
    if not users_db:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST, detail= "El usuario no es correcto")
    
    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST, detail= "La contraseña no es correcta")
    
    access_token = {"sub":user.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user