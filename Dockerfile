FROM python:3.11-slim

WORKDIR /app

# Chỉ cài 2 thư viện chính, bỏ pydantic vì crewai sẽ tự kéo bản phù hợp
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir crewai langchain-google-genai

COPY . .

CMD ["python", "main.py"]