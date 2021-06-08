"""
Dependencies module includes:
- security oauth authentification on OC ressources
"""
import requests
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from app.core.db import mongodb
from app.schema.authentification import Token, UserAuth
from app.services.oc_api import login_oc

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="",
                   tags=["login"],
                   responses={404: {"description": "Not found"}})


async def get_me(token: str = Depends(oauth2_scheme), cookie: str = Depends(mongodb.get_cookies)) -> UserAuth:
    """
    Test the token from login on OC api
    :param token: token from oauth
    :param cookie: session cookie
    :return: UserAuth
    """
    headers = {'Authorization': 'Bearer ' + token}
    req = requests.get('https://api.openclassrooms.com/me', headers=headers)
    if req.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserAuth(**{"username": req.json()["email"],
                       "token": token,
                       "id": req.json()["id"],
                       "cookie": cookie})


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
    Login for Oauth2
    :param form_data:  OAuth2PasswordRequestForm
    :return: dict with token and token type
    """
    valid_auth = await login_oc(form_data.username, form_data.password)
    if not valid_auth:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": valid_auth["token"],
            "token_type": "bearer"}
