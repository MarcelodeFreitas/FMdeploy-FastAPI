FROM python:3.7.7

COPY ./ai /app/src
COPY ./requirements.txt /app

WORKDIR /app/src

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker src.main:app"]