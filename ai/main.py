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
from .routers import user, ai, userai, authentication
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


app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(ai.router)
app.include_router(userai.router)

@app.get("/")
async def main():
    content = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            a.button{background-color: #2ABF9F;
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
            .button:hover, .button:focus {
                color: #2ABF9F;
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
                    <h1 style="color: #2ABF9F; margin-bottom: 10%; font-size: 2.6vw">Welcome to FMdeploy API !</h1>
                    <p style="color:white; font-size: 16px">Developed with <a href="https://fastapi.tiangolo.com/" target="_blank" style="color: #2ABF9F">Fast API</a>. To check the documentation please use one of the links bellow:</p>
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
            background-color: #2ABF9F;
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