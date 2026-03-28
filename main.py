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
user_command = "What is purpose of stimulus_controller helper, I see it in application.html.erb?"
timestamp = datetime.now().strftime("%H%M%S") 
date_prefix = datetime.now().strftime("%Y%m%d")
output_path = f"outputs/{date_prefix}-{timestamp}-analysis.md"

if not os.path.exists("outputs"):
    os.makedirs("outputs", exist_ok=True)

# 3. Tools (Chỉ quét folder cần thiết để tiết kiệm tài nguyên)
dir_app_tool = DirectoryReadTool(directory='./skycom/app')
file_read_tool = FileReadTool()

# 4. Agent - Nâng cấp vai trò cho xứng tầm 20 Cores
analyst = Agent(
    role='Senior Rails Architect',
    goal=f'Analyze the {user_command} in the Skycom project.',
    backstory=(
        'Expert in Ruby on Rails and StimulusJS. '
        'CRITICAL: When using a tool, you must wait for the tool output before giving a final answer. '
        'NEVER provide a JSON tool call as your Final Answer. '
        'Your final answer must be a clear, human-readable explanation in Markdown.'
    ),
    llm=local_llm, 
    tools=[dir_app_tool, file_read_tool],
    verbose=True,
    allow_delegation=False
)

# 5. Task - Yêu cầu cụ thể để AI không "chém gió"
analysis_task = Task(
    description=(
        f"Investigate the custom helper 'stimulus_controller' in the Skycom project.\n"
        "STEPS TO FOLLOW:\n"
        "- First, look into 'app/views/layouts/application.html.erb' to see how it is used.\n"
        "- Second, search for the helper definition in 'app/helpers/application_helper.rb' or other files in 'app/helpers/'.\n"
        "- Third, explain what this helper does (e.g., does it format controller names for Stimulus?)."
    ),
    expected_output="A detailed explanation of the stimulus_controller helper's purpose and its code implementation.",
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