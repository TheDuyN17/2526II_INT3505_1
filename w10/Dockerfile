FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py observability.py security.py ./

EXPOSE 5010

CMD ["gunicorn", "--bind", "0.0.0.0:5010", "--workers", "1", "--threads", "4", "--timeout", "30", "app:create_app()"]
