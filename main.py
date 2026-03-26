import os
from crewai import Agent, Task, Crew

# Lưu ý: Không cần khởi tạo gemini_llm kiểu cũ
# Chỉ cần đảm bảo biến môi trường GOOGLE_API_KEY đã có

# 1. Định nghĩa Agent dùng string cho llm
news_agent = Agent(
    role='News Scout',
    goal='Tìm và tóm tắt 3 tin mới nhất về {topic}',
    backstory='Bạn là một chuyên gia săn tin công nghệ.',
    # THỬ PHƯƠNG ÁN NÀY TRƯỚC:
    llm="gemini/gemini-flash-latest", 
    verbose=True,
    allow_delegation=False
)

# 2. Định nghĩa Task
news_task = Task(
    description='Tìm hiểu về {topic} trong 24h qua và liệt kê 3 gạch đầu dòng.',
    expected_output='Một bản tóm tắt 3 tin tức mới nhất.',
    agent=news_agent,
    output_file='news_report.md'
)

# 3. Khởi tạo Crew
crew = Crew(
    agents=[news_agent],
    tasks=[news_task],
    verbose=True
)

if __name__ == "__main__":
    print("### ĐANG CHẠY CREWAI VỚI STRING LLM... ###")
    crew.kickoff(inputs={'topic': 'Ruby on Rails 8 and Kamal 2'})