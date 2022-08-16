FROM python:3.10

WORKDIR /app
COPY graceful_exit.py uplader.py ./

CMD ["python", "uploader.py"]
