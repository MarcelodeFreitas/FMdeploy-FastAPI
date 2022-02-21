from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

router = APIRouter(
    prefix="/jwtauth",
    tags=['JWT Authentication (FUTURE WORK)']
)

# __________________________CONSTANTS______________________

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# __________________________PYDANTIC SCHEMAS______________________


class User(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    
#__________________________FUNCTIONS_______________________



# __________________________ROUTERS________________________


""" @router.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    ) """
    
# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()

# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@router.post('/login')
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
@router.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}


#FUTURE DEVELOPMENT IDEAS
#JWT tokens
#refresh tokens
#revoke tokens
#JWT in cookies