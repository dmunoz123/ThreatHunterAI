FROM python:3.12-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libopenblas-dev \
  tshark \
  && rm -rf /var/lib/apt/lists/*

COPY ./backend /app

WORKDIR /app

COPY requirements1.txt /app

RUN pip install -r requirements1.txt

CMD ["python", "main.py"]
