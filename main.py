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

SKYCOM_ARCHITECTURE_MANIFESTO = """
# Project Context: Skycom (Hybrid SPA Architecture)
Skycom is a multi-tenant business management platform. It uses a non-traditional Rails architecture designed for speed and a desktop-app feel, bypassing heavy server-side HTML rendering.

## Core Principles:
1. **Shell-First Rendering**: Initial HTML returns an empty shell; Stimulus hydrates the page.
2. **JSON-Only Data Flow**: Rails Controllers handle `.json` requests for data.
3. **Client-Side Templating**: Rendering happens in `contentHTML()` via ES6 Template Literals.

## Stimulus Naming & Inheritance (CRITICAL):
1. **Class Naming**: Use **Pascal_Snake_Case** (e.g., `Companies_Branches_EmployeesController`).
2. **Identifier**: `Companies_LayoutController` -> `companies--layout`. Use `window.identifier(Class)` to generate.
3. **Inheritance**: Child controllers inherit all `static targets` from parents. Do not redefine them.

## Advanced Global Helpers (window.*):
AI MUST prioritize these over native implementations to ensure Rails compatibility:

1. **fetchJson(url|options, options)**:
   - **Smart Default**: If `url` is omitted, it fetches from the CURRENT `window.location.href`.
   - **Security**: Automatically injects `X-CSRF-Token` for internal requests.
   - **Auto-JSON**: Stringifies object bodies and sets `Content-Type: application/json` automatically.
   - *Usage*: `const data = await fetchJson({ params: { status: 'active' } })` (fetches from current path).

2. **form({ action, method, dataAction, className, html })**:
   - **Smart Default Action**: Defaults to `pathname()` (current URL).
   - **Rails Method Spoofing**: Since browsers only support GET/POST, this helper automatically adds `<input type="hidden" name="_method">` for PATCH and DELETE.
   - **Security**: Automatically injects CSRF `authenticity_token` via `formPostSecurityTags()`.
   - *Usage*: `form({ method: 'PATCH', html: fields })` generates a Rails-compatible update form.

3. **URL Helpers**:
   - `pathname()`: Returns `window.location.pathname`.
   - `href()`: Returns `window.location.href`.

4. **Security Helpers**:
   - `csrfToken()`: Fetches from meta tag.
   - `formPostSecurityTags()` / `formPatchSecurityTags()`: For manual form building.

## Coding Standards for AI:
- **Form Generation**: Always use the `form()` helper for creating new/edit forms to ensure CSRF and Method Spoofing are handled.
- **Data Ingestion**: Use `fetchJson()` inside `connect()` or event handlers. Remember it defaults to the current page's path.
- **Consistency**: When updating `Companies::EmployeesController`, ensure the `create` (POST) and `update` (PATCH) actions return appropriate JSON for these helpers to consume.
- **Paths**: When the user says "this page", use `pathname()` or `fetchJson()` with no URL.
"""

# 4. Agent
analyst = Agent(
    role='Expert Rails Developer',
    goal='Execute the user request by exploring the codebase and providing a detailed answer.',
    backstory=(
        f"{SKYCOM_ARCHITECTURE_MANIFESTO}\n"
        "--- \n"
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