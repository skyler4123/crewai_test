import os
from crewai import Agent, Task, Crew
# Import công cụ cào web
from crewai_tools import ScrapeWebsiteTool

# Khởi tạo công cụ (Để trống để Agent tự điền URL từ request của ông)
scrape_tool = ScrapeWebsiteTool()

# 1. Định nghĩa Agent
news_agent = Agent(
    role='Omni-Scout Specialist',
    goal='Thực hiện chính xác yêu cầu: {request}',
    backstory='''Bạn là một chuyên gia duyệt web. 
    Bạn có khả năng phân tích câu lệnh, xác định website cần vào 
    và trích xuất dữ liệu chính xác.''',
    # GIỮ NGUYÊN MODEL STRING CỦA ÔNG:
    llm="gemini/gemini-flash-latest", 
    tools=[scrape_tool], 
    verbose=True,
    allow_delegation=False
)

# 2. Định nghĩa Task
news_task = Task(
    description='''Phân tích yêu cầu: "{request}". 
    Hãy sử dụng ScrapeWebsiteTool để truy cập vào trang web liên quan 
    và trả về thông tin chi tiết nhất.''',
    expected_output='Kết quả xử lý hoàn chỉnh cho yêu cầu: "{request}".',
    agent=news_agent,
    output_file='result_report.md'
)

# 3. Khởi tạo Crew
crew = Crew(
    agents=[news_agent],
    tasks=[news_task],
    verbose=True
)

if __name__ == "__main__":
    print("### SKYCOM BOT READY (SINGLE INPUT MODE) ###")
    # Nhận 1 dòng text duy nhất từ ông
    user_command = "Vào Gamek.vn để xem trang đang đăng những tin tức gì"
    
    # Truyền vào biến {request}
    crew.kickoff(inputs={'request': user_command})