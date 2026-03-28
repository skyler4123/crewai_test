import os
from datetime import datetime
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool, DirectoryReadTool

# 1. Khởi tạo Qwen 2.5 Coder 14B - "Ông trùm" Code Local hiện tại
# Tận dụng 16k context window và 16/20 cores của ông
local_llm = LLM(
    model="ollama/llama3.1",
    # model="ollama/qwen2.5-coder:14b",
    base_url="http://ollama:11434",
    # Thay vì dùng config, ta dùng các tham số chuẩn của OpenAI 
    # litellm sẽ tự map sang Ollama options
    temperature=0,
    # timeout=300,
    # max_tokens=8192 # Giới hạn token output để tránh tràn RAM
)

# 2. Configuration & Output Path
user_command = "Table users will have a model name User, I want to know what fields that model/table have?"
timestamp = datetime.now().strftime("%H%M%S") 
date_prefix = datetime.now().strftime("%Y%m%d")
output_path = f"outputs/{date_prefix}-{timestamp}-analysis.md"

if not os.path.exists("outputs"):
    os.makedirs("outputs", exist_ok=True)

# 3. Tools (Chỉ quét folder cần thiết để tiết kiệm tài nguyên)
dir_app_tool = DirectoryReadTool(directory='./skycom/app')
file_read_tool = FileReadTool()

# 4. Agent - Nâng cấp vai trò cho xứng tầm 20 Cores
project_tool = DirectoryReadTool(directory='./skycom')
file_tool = FileReadTool()
analyst = Agent(
    role='Expert Rails Developer',
    goal='Execute the user request by exploring the codebase and providing a detailed answer.',
    backstory=(
        "You are a master of Ruby on Rails. You have full access to the project directory. "
        "Your workflow: 1. Explore the directory to find relevant files. 2. Read those files. "
        "3. Synthesize the information to answer the user. "
        "IMPORTANT: Always provide a human-readable final answer, never just JSON."
    ),
    llm=local_llm, 
    tools=[project_tool, file_tool],
    verbose=True
)

# 5. Task - Yêu cầu cụ thể để AI không "chém gió"
analysis_task = Task(
    description=(
        f"Process this user request: '{user_command}'.\n"
        "Follow these steps:\n"
        "- Step 1: Browse the directory to locate files related to the request.\n"
        "- Step 2: Read and analyze the content of those files.\n"
        "- Step 3: Provide a comprehensive answer based on your findings."
    ),
    expected_output="A complete and detailed response to the user's request based on the actual project code.",
    agent=analyst,
    output_file=output_path
)

# 6. Crew
skycom_crew = Crew(
    agents=[analyst],
    tasks=[analysis_task],
    verbose=True,
    # Thêm 2 dòng này để tắt các tính năng yêu cầu tương tác
    share_crew=False,
    memory=False
)

if __name__ == "__main__":
    print(f"🚀 Skycom Crew is starting analysis using Qwen 2.5 Coder 14B...")
    print(f"📂 Output will be saved to: {output_path}")
    skycom_crew.kickoff()