FROM python:3.11-slim-buster

ENV PORT=8000

COPY . /app/
WORKDIR /app/
RUN pip install -r requirements.txt

WORKDIR /app/web/
CMD flask run -h 0.0.0.0 -p $PORT
