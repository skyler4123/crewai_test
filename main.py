import os
from datetime import datetime
from crewai import Agent, Task, Crew, LLM
from crewai_tools import FileReadTool, DirectoryReadTool, FileWriterTool

# 1. Khởi tạo LLM - Chế độ "Switch" linh hoạt giữa các anh tài
local_llm = LLM(
    # --- Chọn 1 model để chạy, các model còn lại để dấu # phía trước ---
    model="ollama/llama3.1",                     # Lễ tân điều phối
    # model="ollama/qwen2.5-coder:14b",          # Thợ code Rails thực chiến
    # model="ollama/gemma2:27b",                 # Kiến trúc sư phân tích (Khuyên dùng cho Task này)
    # model="ollama/command-r",                  # Vua thực thi Tool & Write file
    # model="ollama/deepseek-r1:32b",            # Trùm cuối suy luận logic & fix bug
    # model="ollama/deepseek-coder-v2:16b-lite-instruct-q8_0", # Từ điển code
    
    base_url="http://192.168.0.100:11434",
    temperature=0,
)

# 2. Configuration & Output Path
# Request mới của Skyler rất phức tạp (Controller + Routes + Form), đòi hỏi AI phải đọc nhiều file.
user_command = "In User model, write a method named 'can_manage_billing?' that returns true if the user is a super_admin or a company_owner. Ensure it uses the existing 'system_role' enum."
# user_command = "Modify 'app/models/user.rb' by appending '# Skycom AI was here' at the very bottom. You MUST use FileWriterTool to save the change. Do not provide a summary, just execute the tool call."
# user_command = "How to use fetchJson method, I saw it used a lot at some stimulus controllers"

user_command = "Companies_Employees_NewModalController is controller that render a modal, I need to transfer this content into a form that will create a new employee, I also need a new action for that purpose at Companies::EmployeesController, update the routes.rb also"

timestamp = datetime.now().strftime("%H%M%S") 
date_prefix = datetime.now().strftime("%Y%m%d")
output_path = f"outputs/{date_prefix}-{timestamp}-analysis.md"

if not os.path.exists("outputs"):
    os.makedirs("outputs", exist_ok=True)

# 3. Tools
project_tool = DirectoryReadTool(directory='./skycom') # Quét toàn bộ project để thấy config/routes.rb
file_read_tool = FileReadTool()
write_tool = FileWriterTool()

# 4. Agent
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
    tools=[project_tool, file_read_tool, write_tool],
    verbose=True
)

# 5. Task
analysis_task = Task(
    description=(
        f"User Request: '{user_command}'\n\n"
        "INSTRUCTIONS FOR AGENT:\n"
        "1. **Analyze Intent**: This is a complex ACTION request involving multiple files.\n"
        "2. **Execution Steps**:\n"
        "   - Find and read the Stimulus controller or Rails controller for the modal.\n"
        "   - Locate 'app/controllers/companies/employees_controller.rb' and add the necessary action.\n"
        "   - Locate 'config/routes.rb' and update the routing.\n"
        "   - Use 'FileWriterTool' to apply these changes. DO NOT JUST EXPLAIN, DO IT.\n"
        "3. **Safety**: Preserve existing logic. Only add/modify the parts related to creating a new employee."
    ),
    expected_output="A summary of the modified files (EmployeesController, routes.rb, and the new form/modal logic).",
    agent=analyst,
    output_file=output_path
)

# 6. Crew
skycom_crew = Crew(
    agents=[analyst],
    tasks=[analysis_task],
    verbose=True,
    share_crew=False,
    memory=False
)

if __name__ == "__main__":
    print(f"🚀 Skycom Crew is active on http://192.168.0.100:11434...")
    print(f"📂 Project Path: ./skycom")
    skycom_crew.kickoff()