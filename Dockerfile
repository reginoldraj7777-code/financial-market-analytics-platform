FROM python:3.12-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt
COPY src ./src
COPY evidence/full/metrics.json evidence/full/review_queue.json ./evidence/full/
RUN useradd --create-home appuser && mkdir -p data && chown appuser:appuser data
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
