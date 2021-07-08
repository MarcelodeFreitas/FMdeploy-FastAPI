import os
from main import app

if __name__ == '__main__':
    os.system('uvicorn ai.main:app --reload')
    #how to choose host and port
    #uvicorn.run(app,host="0.0.0.0", port=9000)
    pass