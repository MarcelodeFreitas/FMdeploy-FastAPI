import os

if __name__ == '__main__':
    os.makedirs("modelfiles", exist_ok=True)
    os.system('uvicorn ai.main:app')
    #how to choose host and port
    #uvicorn.run(app,host="0.0.0.0", port=9000)
    # Change "openapi.json" to desired filename
    pass