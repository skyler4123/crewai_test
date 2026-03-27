FROM python:3.11-slim

WORKDIR /app

# Nâng cấp pip và cài bản có tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "crewai[tools]" langchain-google-genai

COPY . .

CMD ["python", "main.py"]