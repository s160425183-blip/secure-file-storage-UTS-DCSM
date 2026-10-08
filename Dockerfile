FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY proto ./proto
COPY server ./server

RUN mkdir -p storage logs certs

EXPOSE 50051

CMD ["python", "-m", "server.server"]
