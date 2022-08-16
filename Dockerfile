FROM python:3.10

WORKDIR /tmp
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY acceptor.py ./

# TODO wsgi
CMD ["python", "acceptor.py"]
