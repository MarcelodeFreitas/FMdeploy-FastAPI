import os

if __name__ == '__main__':
    os.system('uvicorn api.main:app --reload')
    pass