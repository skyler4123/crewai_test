FROM python:3.11-slim

WORKDIR /app

# Cài đặt crewai[tools] để có FileReadTool, FileWriterTool, v.v.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "crewai[tools]" langchain-google-genai

COPY . .

CMD ["python", "main.py"]