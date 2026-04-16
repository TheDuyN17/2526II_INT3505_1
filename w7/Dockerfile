FROM python:3.11-slim

WORKDIR /app

# Cài dependencies trước để tận dụng Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Chạy bằng python -m openapi_server (gọi __main__.py)
CMD ["python", "-m", "openapi_server"]
