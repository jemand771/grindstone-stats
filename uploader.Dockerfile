FROM python:3.10

WORKDIR /app
COPY graceful_exit.py uploader.py ./

CMD ["python", "uploader.py"]
