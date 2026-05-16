FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY python ./python

RUN pip install --no-cache-dir .

ENV FEATURE_LLM_ANALYZER=false \
    FEATURE_FLAG_UI_ENABLED=true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
