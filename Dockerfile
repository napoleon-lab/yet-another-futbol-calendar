FROM python:3.9-slim as builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.9-slim

COPY --from=builder /install /usr/local
WORKDIR /app
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]