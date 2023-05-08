from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import schemas

SECRET_KEY = "4usBQ5fRiHr7gbcpPVUcoHwIcGL8mSDv"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    email: str = payload.get("sub")
    role: str = payload.get("role")

    if email is None or role is None:
        raise credentials_exception

    return schemas.TokenData(email=email, role=role)
