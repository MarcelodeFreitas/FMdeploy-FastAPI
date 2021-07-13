from fastapi import FastAPI, Depends, File, UploadFile, status, Response, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from . import schemas, models
from .database import engine
from sqlalchemy.orm import Session
from .database import get_db
from typing import List
import shutil
import os
from .routers import user, ai, userai
from datetime import datetime
import json
import importlib
import sys


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

#when we run the server migrate all the models to the database
#if the table exists nothing happens
#if not, the table is created
models.Base.metadata.create_all(engine)

# # save documentation
# @app.on_event("startup")
# def save_openapi_json():
#     openapi_data = app.openapi()
#     # Change "openapi.json" to desired filename
#     with open("openapi.json", "w") as file:
#         json.dump(openapi_data, file)

app.include_router(user.router)
app.include_router(ai.router)
app.include_router(userai.router)

@app.get("/test")
async def test():
    sys.path.append('./modelfiles/app')
    script =  importlib.import_module("script")
    await script.hello()

@app.get("/")
async def main():
    content = """
        <body style="margin-left: 100px; background-color: #33363B; font-family: sans-serif;">
        <div style="display: flex;">
            <div style="flex: 50%;
            height: 95vh;">
                <div style="margin-bottom: 60px; margin-top: 300px">
                    <h1 style="color: #2ABF9F; margin-bottom: 60px; font-size: 49">Welcome to FMdeploy API !</h1>
                    <p style="color:white;">Developed with <a href="https://fastapi.tiangolo.com/" target="_blank" style="color: #2ABF9F">Fast API</a>. To check the documentation please use one of the links bellow:</p>
                </div>
                <a style = 
                    "background-color: #2ABF9F;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    cursor: pointer; 
                    margin-right: 100px;
                    margin-top: 30px;
                    font-weight: bold;
                    border-radius: 5px;
                    width: 200px"
                    href="/docs" target="_blank">
                    Docs Swagger UI
                </a>
                <a style = 
                    "background-color: #2ABF9F;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    cursor: pointer;
                    margin-top: 30px;
                    font-weight: bold;
                    border-radius: 5px;
                    width: 200px"
                    href="/redoc" target="_blank">
                    Docs ReDoc
                </a>
            </div>
            <div style="flex: 50%;
            height: 98vh;
            background-color: #2ABF9F">
                <center style="margin-top: 300px">
                    <img src="static/logo.png"/>
                    <p style="color: white; font-size: 45; text-align: center; font-weight: bold">
                        FMdeploy
                    </p>
                </center>
            </div>
        </div> 
        </body>
    """
    return HTMLResponse(content=content)