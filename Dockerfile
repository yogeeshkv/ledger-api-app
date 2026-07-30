FROM python:3.6-slim

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 8080

CMD ["python", "app.py"]
