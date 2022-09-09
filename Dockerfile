FROM python:3.10

WORKDIR /tmp
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

WORKDIR /app
COPY server.py model.py security.py ./
COPY templates ./templates

# TODO wsgi
CMD ["gunicorn", "--bind", ":80", "server:app"]
