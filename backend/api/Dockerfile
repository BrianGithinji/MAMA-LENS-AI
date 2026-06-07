FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install model dependencies (only needed in HF Spaces Docker build)
RUN pip install --no-cache-dir torch==2.3.1 transformers==4.51.3 sentencepiece==0.2.0 protobuf>=3.20.0 accelerate>=0.30.0

COPY . .

# Pre-download the fine-tuned model into the image at build time
ARG HF_API_TOKEN
ENV HF_HOME=/tmp/hf_cache
RUN python scripts/download_model.py

RUN useradd -m -u 1000 mamalens && chown -R mamalens:mamalens /app
USER mamalens

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
