import os

if __name__ == '__main__':
    os.system('uvicorn blog.main:app --reload')
    pass