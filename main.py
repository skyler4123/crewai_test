import os
from datetime import datetime
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool, DirectoryReadTool, FileWriterTool # Thêm cái này

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
# user_command = "In User model, write a method named 'can_manage_billing?' that returns true if the user is a super_admin or a company_owner. Ensure it uses the existing 'system_role' enum."
# user_command = "Modify 'app/models/user.rb' by appending '# Skycom AI was here' at the very bottom. You MUST use FileWriterTool to save the change. Do not provide a summary, just execute the tool call."
user_command = "How to use fetchJson method, I saw it used a lot at some stimulus controllers"
timestamp = datetime.now().strftime("%H%M%S") 
date_prefix = datetime.now().strftime("%Y%m%d")
output_path = f"outputs/{date_prefix}-{timestamp}-analysis.md"

if not os.path.exists("outputs"):
    os.makedirs("outputs", exist_ok=True)

# 3. Tools (Chỉ quét folder cần thiết để tiết kiệm tài nguyên)
dir_app_tool = DirectoryReadTool(directory='./skycom/app')
file_read_tool = FileReadTool()
write_tool = FileWriterTool()

# 4. Agent - Nâng cấp vai trò cho xứng tầm 20 Cores
project_tool = DirectoryReadTool(directory='./skycom')
file_tool = FileReadTool()
analyst = Agent(
    role='Expert Rails Developer',
    goal='Execute the user request by exploring the codebase and providing a detailed answer.',
    backstory=(
        "You are a master of Ruby on Rails. You have full access to the project directory. "
        "Your workflow: 1. Explore the directory to find relevant files. 2. Read those files. "
        "3. **Action Request**: If the user asks to modify code, you MUST:"
        "   - Use the 'FileWriterTool' (NOT just writing JSON) to save changes."
    ),
    llm=local_llm, 
    tools=[project_tool, file_tool, write_tool],
    verbose=True
)

# 5. Task - Yêu cầu cụ thể để AI không "chém gió"
analysis_task = Task(
    description=(
        f"User Request: '{user_command}'\n\n"
        "INSTRUCTIONS FOR AGENT:\n"
        "1. **Analyze Intent**: Determine if the user wants an INFORMATION (explanation/analysis) or an ACTION (writing/modifying code).\n"
        "2. **Information Request**: If it is an analysis, browse the files, read them, and provide a detailed Markdown response. DO NOT modify any files.\n"
        "3. **Action Request**: If the user explicitly asks to 'add', 'create', 'update', or 'modify' code, you MUST:\n"
        "   - Read the target file.\n"
        "   - Use 'FileWriteTool' to apply the changes directly to the codebase.\n"
        "   - Ensure you keep all existing logic and only add/modify what is necessary.\n"
        "4. **Final Step**: Always summarize what you did or what you found."
    ),
    expected_output="Either a comprehensive Markdown report OR a confirmation of the code changes performed.",
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