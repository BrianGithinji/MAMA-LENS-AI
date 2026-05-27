FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pre-download the fine-tuned MAMA model at build time so it's cached in the image.
# This avoids cold-start timeouts on Render's free tier.
ARG HF_MODEL_ID=BrianGithinji/mama-flan-t5
ARG HF_HOME=/tmp/hf_cache
RUN HF_HOME=${HF_HOME} python -c "
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import os
model_id = os.environ.get('HF_MODEL_ID', '${HF_MODEL_ID}')
cache = os.environ.get('HF_HOME', '${HF_HOME}')
print(f'Pre-downloading {model_id} -> {cache}')
AutoTokenizer.from_pretrained(model_id, cache_dir=cache)
AutoModelForSeq2SeqLM.from_pretrained(model_id, cache_dir=cache)
print('Model cached.')
"

# Create non-root user
RUN useradd -m -u 1000 mamalens && chown -R mamalens:mamalens /app
USER mamalens

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
