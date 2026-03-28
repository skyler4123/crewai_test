# Script tải bộ "Hào Kiệt Local LLM" cho Skyler
# 20 Cores CPU | 40GB RAM | Ho Chi Minh City

echo "🚀 Bắt đầu nạp năng lượng cho dàn Model của Skyler..."

# NHÓM 1: AGENT & ĐIỀU PHỐI (Chạy mượt, ít lỗi logic)
echo "📦 Đang tải Llama 3.1 (8B) - Trùm Agent..."
docker exec -it ollama ollama pull llama3.1

echo "📦 Đang tải Mistral Nemo (12B) - Logic cực tốt..."
docker exec -it ollama ollama pull mistral-nemo

echo "📦 Đang tải Mixtral (8x7B) - Huyền thoại MoE..."
docker exec -it ollama ollama pull mixtral

# NHÓM 2: CHUYÊN GIA CODE & CÔNG VIỆC NẶNG
echo "📦 Đang tải Qwen 2.5 Coder (14B-Instruct) - Phù thủy Rails..."
docker exec -it ollama ollama pull qwen2.5-coder:14b-instruct

echo "📦 Đang tải Gemma 2 (27B) - Kiến trúc sư tối thượng..."
docker exec -it ollama ollama pull gemma2:27b

echo "📦 Đang tải Command R (35B) - Vua của RAG & Project lớn..."
docker exec -it ollama ollama pull command-r

# NHÓM 3: SIÊU SUY LUẬN (Reasoning)
echo "📦 Đang tải DeepSeek R1 (14B) - Tư duy logic nhanh..."
docker exec -it ollama ollama pull deepseek-r1:14b

echo "📦 Đang tải DeepSeek R1 (32B) - Cỗ máy giải quyết Bug khó..."
docker exec -it ollama ollama pull deepseek-r1:32b

echo "✅ TẤT CẢ ĐÃ XONG! Sáng mai tha hồ cho 20 nhân CPU 'quẩy' dự án Skycom nha Skyler!"
docker exec -it ollama ollama list