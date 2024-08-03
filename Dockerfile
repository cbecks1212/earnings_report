FROM python:3.11-bullseye

COPY . /src

WORKDIR /src

RUN pip install -r requirements.txt

EXPOSE 8080

#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

CMD exec gunicorn --bind :8080 --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 src.main:app