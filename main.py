import os
from datetime import datetime
from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool

# 1. Xử lý logic tên file động
user_command = "Vào Gamek.vn để xem trang đang đăng những tin tức gì"

# Tạo prefix YYYYMMDD
date_prefix = datetime.now().strftime("%Y%m%d")

# Tạo slug từ câu lệnh (lấy 3-4 chữ đầu, bỏ dấu/khoảng trắng để làm tên file)
# Ví dụ: "Vào Gamek.vn..." -> "vao-gamek-vn"
clean_name = user_command.lower().split()[:3]
slug = "-".join(clean_name).replace(".", "-")

# Đường dẫn cuối cùng: output/20260327-vao-gamek-vn.md
output_path = f"outputs/{date_prefix}-{slug}.md"

# Đảm bảo thư mục output tồn tại để không bị crash
os.makedirs("output", exist_ok=True)

# --- PHẦN BOT GIỮ NGUYÊN ---

scrape_tool = ScrapeWebsiteTool()

news_agent = Agent(
    role='Omni-Scout Specialist',
    goal='Thực hiện chính xác yêu cầu: {request}',
    backstory='''Bạn là một chuyên gia duyệt web. 
    Bạn có khả năng phân tích câu lệnh, xác định website cần vào 
    và trích xuất dữ liệu chính xác.''',
    llm="gemini/gemini-flash-latest", 
    tools=[scrape_tool], 
    verbose=True,
    allow_delegation=False
)

news_task = Task(
    description='''Phân tích yêu cầu: "{request}". 
    Hãy sử dụng ScrapeWebsiteTool để truy cập vào trang web liên quan 
    và trả về thông tin chi tiết nhất.''',
    expected_output='Kết quả xử lý hoàn chỉnh cho yêu cầu: "{request}".',
    agent=news_agent,
    output_file=output_path # DÙNG ĐƯỜNG DẪN ĐỘNG Ở ĐÂY
)

crew = Crew(
    agents=[news_agent],
    tasks=[news_task],
    verbose=True
)

if __name__ == "__main__":
    print(f"### SKYCOM BOT READY (SINGLE INPUT MODE) ###")
    print(f"### OUTPUT WILL BE SAVED TO: {output_path} ###")

    crew.kickoff(inputs={'request': user_command})

