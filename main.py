import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, FileWriterTool, DirectoryReadTool

# 1. Input Configuration
# User intent: Understand how Stimulus controllers map to the current Rails paths
user_command = "Describe the relation between stimulus controller name with the current path of each page"

# Dynamic Output Path Logic
date_prefix = datetime.now().strftime("%Y%m%d")
slug = "-".join(user_command.lower().split()[:5]).replace(".", "-").replace("/", "-")
output_path = f"outputs/{date_prefix}-{slug}.md"
os.makedirs("outputs", exist_ok=True)

# 2. Tool Initialization (Scoping to Skycom functional directories)
# We avoid the root './skycom' to prevent scanning .git or tmp folders
dir_app_tool = DirectoryReadTool(directory='./skycom/app')
dir_config_tool = DirectoryReadTool(directory='./skycom/config')
file_read_tool = FileReadTool()
file_writer_tool = FileWriterTool()

# 3. Agent Definitions
analyst = Agent(
    role='Skycom System Analyst',
    goal='Analyze the Rails 8 codebase structure and architectural patterns.',
    backstory="""You are an expert in Ruby on Rails 8 and Hotwire. 
    You excel at mapping frontend Stimulus controllers to backend routes and views. 
    You provide the technical context needed for other developers to work.""",
    llm="gemini/gemini-flash-latest",
    tools=[dir_app_tool, dir_config_tool, file_read_tool],
    verbose=True,
    allow_delegation=False
)

backend_dev = Agent(
    role='Skycom Backend Engineer',
    goal='Identify and explain backend logic, routing, and controller associations.',
    backstory="""You are a Senior Rails Developer. You understand how Rails 
    routes map to controllers and how those controllers render specific views 
    that carry Stimulus data attributes.""",
    llm="gemini/gemini-flash-latest",
    tools=[file_read_tool],
    verbose=True,
    allow_delegation=False
)

frontend_dev = Agent(
    role='Skycom Frontend Engineer',
    goal='Map Stimulus JS controllers to HTML elements and Rails view paths.',
    backstory="""You are a Hotwire specialist. You know exactly how 
    'hello_controller.js' relates to 'data-controller="hello"' in your 
    Rails views and how folder structures affect naming conventions.""",
    llm="gemini/gemini-flash-latest",
    tools=[dir_app_tool, file_read_tool],
    verbose=True,
    allow_delegation=False
)

# 4. Task Definition
analysis_task = Task(
    description=f"""
    Objective: {user_command}
    
    Steps:
    1. Scan './skycom/app/javascript/controllers' to see naming conventions.
    2. Scan './skycom/config/routes.rb' and './skycom/app/views' to see how pages are served.
    3. Explain the naming convention (e.g., how 'users/profile_controller.js' maps to a specific view).
    4. Detail if there is a direct relationship between the URL path and the Stimulus controller naming in this specific project.
    """,
    expected_output="A technical documentation explaining the mapping between Stimulus controllers and page paths in Skycom.",
    agent=analyst,
    output_file=output_path
)

# 5. Crew Assembly
skycom_crew = Crew(
    agents=[analyst, backend_dev, frontend_dev],
    tasks=[analysis_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print(f"### SKYCOM AI CREW: INITIATING ANALYSIS ###")
    print(f"### TASK: {user_command} ###")
    
    skycom_crew.kickoff(inputs={'request': user_command})