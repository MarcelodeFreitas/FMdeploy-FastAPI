from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import (
    project,
    user,
    authentication,
    files,
    auth,
    jwtauth,
    userproject,
    angelica,
    runhistory,
)
from fastapi.middleware.cors import CORSMiddleware

from fastapi_utils.tasks import repeat_every
import os
import time
import shutil

from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)

print(os.getcwd())

# mount the static folder to get the brain logo in html
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# when we run the server migrate all the models to the database
# if the table exists nothing happens
# if not, the table is created
models.Base.metadata.create_all(engine)

# # save documentation
# @app.on_event("startup")
# def save_openapi_json():
#     openapi_data = app.openapi()
#     # Change "openapi.json" to desired filename
#     with open("openapi.json", "w") as file:
#         json.dump(openapi_data, file)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(project.router)
app.include_router(files.router)
app.include_router(userproject.router)
app.include_router(runhistory.router)
app.include_router(angelica.router)
# commented to not interfere with current auth implementation
# app.include_router(auth.router)
# app.include_router(jwtauth.router)


# delete files that haven't been accessed in 24h, checked every 24h since server start
@app.on_event("startup")
@repeat_every(seconds=60 * 24 * 60)  # repeat every hour
async def file_cleanup():
    try:
        print("Cleaning old files...")
        path1 = ".\inputfiles"
        path2 = ".\outputfiles"
        max_access_time = 60 * 24 * 60
        present_time = time.time()
        if os.path.exists(path1):
            for roots, dirs, files in os.walk(path1):
                for f in files:
                    fil = os.path.join(roots, f)
                    fil_stat = os.stat(fil)
                    last_access_time = fil_stat.st_atime
                    if last_access_time < present_time - max_access_time:
                        print("here")
                        fil_split = fil.split("\\")
                        print(fil_split)
                        dir_path = (
                            fil_split[0] + "\\" + fil_split[1] + "\\" + fil_split[2]
                        )
                        print(dir_path)
                        print(
                            "FILE PATH: ",
                            fil,
                            "/ LAST ACCESS TIME: ",
                            time.ctime(last_access_time),
                            "/ DELETE TIME: ",
                            time.ctime(present_time),
                        )
                        print("DELETING DIRECTORY: ", dir_path)
                        shutil.rmtree(dir_path)
        if os.path.exists(path2):
            for roots, dirs, files in os.walk(path2):
                for f in files:
                    fil = os.path.join(roots, f)
                    fil_stat = os.stat(fil)
                    last_access_time = fil_stat.st_atime
                    if last_access_time < present_time - max_access_time:
                        fil_split = fil.split("\\")
                        dir_path = (
                            fil_split[0] + "\\" + fil_split[1] + "\\" + fil_split[2]
                        )
                        print(dir_path)
                        print(
                            "FILE PATH: ",
                            fil,
                            "/ LAST ACCESS TIME: ",
                            time.ctime(last_access_time),
                            "/ DELETE TIME: ",
                            time.ctime(present_time),
                        )
                        print("DELETING DIRECTORY: ", dir_path)
                        shutil.rmtree(dir_path)
    except:
        print("error")


@app.get("/")
def landing_page():
    content = """
        <head>
            <link rel="icon" href="static/favicon.ico" />
            <title>FMdeploy API</title>
        </head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            a.button{background-color: #0385B0;
                    border: none;
                    color: white;
                    padding: 1.1em 2.1em 1.1em;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: .85em;
                    cursor: pointer; 
                    margin-right: 100px;
                    margin-top: 30px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 5px;
                    width: 25%}
            .button:hover {
                color: #0385B0;
                background-color: white;
            }
        </style> 
        <body style="margin-left: 100px; background-color: #33363B; font-family: sans-serif; height: device-width">
        <div style="position: fixed;
        top: 0;
        left: 0;
        width: 50%;
        height: 100%;
        padding-top: 20vh">
            <div style="margin-right: 10%;
            margin-left: 10%;">
                <div style="margin-bottom: 10%; ">
                    <h1 style="color: #0385B0; margin-bottom: 10%; font-size: 2.6vw">Welcome to FMdeploy API !</h1>
                    <p style="color:white; font-size: 16px">Developed with <a href="https://fastapi.tiangolo.com/" target="_blank" style="color: #0385B0">Fast API</a>. To check the documentation please use one of the links bellow:</p>
                </div>
                <a class="button" href="/docs" target="_blank">
                    Docs Swagger UI
                </a>
                <a class="button" href="/redoc" target="_blank">
                    Docs ReDoc
                </a>
            </div>
            <div style="position: fixed;
            top: 0;
            right: 0;
            width: 50%;
            height: 100%;
            background-color: #0385B0;
            padding-top: 27vh
            ">
                <center>
                    <img src="static/logo2.png" style="max-width:100%; height:auto; margin-left: 10%; margin-right: 10%; margin-bottom: 4%;">
                    <p style="color: white; font-size: 3vw; text-align: center; font-weight: bold">
                        FMdeploy
                    </p>
                </center>
        </div> 
        </body>
    """
    return HTMLResponse(content=content)


# part of jwt authentication
""" @app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    ) """
