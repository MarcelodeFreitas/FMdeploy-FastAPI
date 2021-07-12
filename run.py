import os

if __name__ == '__main__':
    os.makedirs("modelfiles", exist_ok=True)
    os.makedirs("inputfiles", exist_ok=True)
    os.makedirs("outputfiles", exist_ok=True)
    os.system('uvicorn ai.main:app --reload')
    #how to choose host and port
    #os.system('uvicorn ai.main:app --reload --host 0.0.0.0 --port 8000 )
    #for production
    #gunicorn -k uvicorn.workers.UvicornWorker
    pass