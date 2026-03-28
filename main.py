import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool, DirectoryReadTool

# 1. Khởi tạo Local LLM (Sử dụng Llama 3 - cực giỏi về code)
local_llm = LLM(
    model="ollama/llama3",
    base_url="http://ollama:11434"
)

# 2. Configuration
user_command = "Describe the relation between stimulus controller name with the current path of each page"
# Thêm timestamp vào tên file để không bao giờ bị trùng hoặc bị khóa file cũ
timestamp = datetime.now().strftime("%H%M%S") 
date_prefix = datetime.now().strftime("%Y%m%d")
output_path = f"outputs/{date_prefix}-{timestamp}-analysis.md"

# Đảm bảo folder outputs sạch sẽ và có quyền ghi
if not os.path.exists("outputs"):
    os.makedirs("outputs", exist_ok=True)

# 3. Tools (Chỉ quét folder cần thiết để tiết kiệm RAM/CPU)
dir_app_tool = DirectoryReadTool(directory='./skycom/app')
file_read_tool = FileReadTool()

local_llm = LLM(
    model="ollama/llama3.1", # Thêm :latest cho khớp với 'ollama list'
    base_url="http://ollama:11434",
)

# Trong phần Agent, đảm bảo dùng đúng object local_llm này
analyst = Agent(
    role='Skycom System Analyst',
    goal='Analyze Rails structure using local resources.',
    backstory='Senior Rails Developer running on local hardware.',
    llm=local_llm, 
    tools=[dir_app_tool, file_read_tool],
    verbose=True,
    allow_delegation=False # Tắt cái này để đỡ tốn thêm request nội bộ
)

analysis_task = Task(
    description=f"Task: {user_command}. Focus on app/javascript/controllers and app/views.",
    expected_output="Technical report on Stimulus mapping.",
    agent=analyst,
    output_file=output_path
)

skycom_crew = Crew(
    agents=[analyst],
    tasks=[analysis_task],
    verbose=True
)

if __name__ == "__main__":
    skycom_crew.kickoff()