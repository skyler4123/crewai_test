# Install Ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 1. Llama 3.1 (8B): "Lễ tân" điều hướng, phân loại request nhanh.
docker exec -it ollama ollama pull llama3.1 && \
docker exec -it ollama ollama pull llama3.1:70b && \

# 2. Qwen 2.5 Coder (14B): "Thợ code" chính, cực giỏi Ruby/Rails/Stimulus.
docker exec -it ollama ollama pull qwen2.5-coder:14b-instruct && \
docker exec -it ollama ollama pull qwen2.5:32b && \

# 3. Gemma 2 (27B): "Kiến trúc sư" phân tích hệ thống và lập kế hoạch.
docker exec -it ollama ollama pull gemma2:27b && \

# 4. Command R (35B): "Chuyên gia Tool" - con này bắt buộc phải có để ghi file.
docker exec -it ollama ollama pull command-r && \

# 5. DeepSeek-R1 (32B): "Cỗ máy tư duy" - dùng để fix bug khó và check logic.
docker exec -it ollama ollama pull deepseek-r1:32b && \

# 6. DeepSeek-Coder-V2 (16B): "Từ điển sống" - dự phòng khi Qwen bí bài.
docker exec -it ollama ollama pull deepseek-coder-v2:16b-lite-instruct-q8_0