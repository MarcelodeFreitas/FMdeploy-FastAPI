import os

if __name__ == "__main__":
    os.makedirs("modelfiles", exist_ok=True)
    os.makedirs("inputfiles", exist_ok=True)
    os.makedirs("outputfiles", exist_ok=True)
    os.system(
        "uvicorn app.main:app --reload --port 9000 --reload-dir app/repository --reload-dir app/schemas --reload-dir app/routers --reload-dir app/main --reload-dir app/database --reload-dir app --reload-dir app/models --reload-dir app/dep"
    )
    # how to choose host and port
    # os.system('uvicorn ai.main:app --reload --host 0.0.0.0 --port 8000 ')
    # for production
    # os.system('gunicorn -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port 8000 ')
    # os.system('gunicorn -w 4 -k uvicorn.workers.UvicornH11Worker')
    pass
