from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends
from pydantic import BaseModel
from jose import jwt

SECRET_KEY = "9599325038334df1f265be5a9fe59ebd1d5534d4bf8f4b2c3762bf8fb64b24a9"
ALGORITHMS = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/user/login_token")

class Token(BaseModel):
    access_token: str
    token_type: str

def get_current_user(token_user: str = Depends(oauth2_scheme)):
    unsuth_exp = HTTPException(status_code = 401, detail = "Unauthorized User")
    try:
        token_data = jwt.decode(token_user, SECRET_KEY, ALGORITHMS) 
        if token_data:
            phone_number = token_data.get('phone_number', None)
    except Exception as error:
        raise unsuth_exp

    if not phone_number:
        raise unsuth_exp

    return phone_number


