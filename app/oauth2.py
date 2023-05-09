from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token.verify_token(data, credentials_exception)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception_admin = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access Denied: This action can only be performed by an admin.",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception_guest = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Access Denied: This action cannot be performed by a guest account.",
    headers={"WWW-Authenticate": "Bearer"},
)


def this_admin(data: str = Depends(oauth2_scheme)):
    # Verify the token and extract the user's email and role
    token_data = token.verify_token(data, credentials_exception)
    # Raise an exception if the user is not an admin
    if token_data.role != "admin":
        raise credentials_exception_admin
    return token_data


def this_user_or_admin(data: str = Depends(oauth2_scheme)):
    # Verify the token and extract the user's email and role
    token_data = token.verify_token(data, credentials_exception)
    # Raise an exception if the user is not an "admin" or a "user"
    if token_data.role != "user" and token_data.role != "admin":
        raise credentials_exception_guest
    return token_data
