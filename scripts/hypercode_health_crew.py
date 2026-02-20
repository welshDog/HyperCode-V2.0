"""
HyperCode Health Check Crew
Autonomous multi-agent system for comprehensive project health analysis
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("C:/Users/Lyndz/Downloads/HyperCode-V2.0/.env")

# Set dummy OpenAI key if missing to bypass CrewAI validation
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-proj-dummy-key-for-crewai-validation"

from crewai import Agent, Task, Crew, Process
from crewai import LLM
from crewai_tools import (
    FileReadTool,
    DirectoryReadTool,
    CodeInterpreterTool
)

# Initialize project path
PROJECT_ROOT = "C:/Users/Lyndz/Downloads/HyperCode-V2.0"

# --- Tools ---
file_tool = FileReadTool()
directory_tool = DirectoryReadTool(directory=PROJECT_ROOT)

# --- LLM Configuration (Perplexity) ---
# Using Perplexity Sonar Small for cost efficiency
perplexity_llm = LLM(
    model="perplexity/sonar-reasoning-pro",
    base_url="https://api.perplexity.ai",
    api_key=os.environ.get("PERPLEXITY_API_KEY")
)

# --- Agents ---

system_architect = Agent(
    role='System Architect',
    goal='Analyze and validate the project directory structure and architectural patterns',
    backstory='Expert software architect who ensures code organization follows best practices and scalability standards.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

backend_specialist = Agent(
    role='Backend Specialist',
    goal='Audit Python backend code (FastAPI) for configuration, CORS, and API best practices',
    backstory='Senior Python developer specializing in FastAPI, middleware configuration, and REST API standards.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

frontend_specialist = Agent(
    role='Frontend Specialist',
    goal='Review React/TypeScript frontend code for component patterns and UI library usage',
    backstory='Frontend expert focusing on React, Vite, and component library integration (Recharts, etc.).',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

devops_engineer = Agent(
    role='DevOps Engineer',
    goal='Inspect Docker configurations, CI/CD pipelines, and infrastructure setup',
    backstory='Infrastructure expert responsible for containerization (Docker), orchestration, and build pipelines.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

qa_engineer = Agent(
    role='QA Engineer',
    goal='Evaluate testing coverage, test file existence, and quality assurance processes',
    backstory='Quality assurance lead focused on unit testing, integration testing, and test coverage metrics.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

security_engineer = Agent(
    role='Security Engineer',
    goal='Scan for security vulnerabilities, hardcoded secrets, and unsafe configurations',
    backstory='Cybersecurity expert dedicated to finding vulnerabilities like missing headers, exposed secrets, or injection risks.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

documentation_writer = Agent(
    role='Documentation Writer',
    goal='Assess the quality, completeness, and freshness of project documentation',
    backstory='Technical writer ensuring that all systems have clear, up-to-date, and accessible documentation.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

performance_optimizer = Agent(
    role='Performance Optimizer',
    goal='Identify potential performance bottlenecks in code and configuration',
    backstory='Performance engineer focused on optimizing resource usage, load times, and efficient algorithms.',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

integration_specialist = Agent(
    role='Integration Specialist',
    goal='Verify connections between services (Frontend <-> Backend <-> DB)',
    backstory='Integration expert checking that all parts of the system communicate correctly (API calls, WebSockets, DB connections).',
    tools=[directory_tool, file_tool],
    verbose=True,
    llm=perplexity_llm
)

project_manager = Agent(
    role='Project Manager',
    goal='Synthesize all findings into a comprehensive, structured health report',
    backstory='Technical Project Manager who aggregates technical feedback into actionable executive reports.',
    verbose=True,
    llm=perplexity_llm
)

# --- Tasks ---

task_structure = Task(
    description=f"Scan the root directory {PROJECT_ROOT}. Analyze the folder structure. Verify if it follows a standard microservices or modular monolith layout. Report on key directories found.",
    agent=system_architect,
    expected_output="A summary of the project structure and architectural compliance."
)

task_backend = Task(
    description=f"Check `hypercode-core/main.py` and other backend files. Specifically look for CORSMiddleware configuration. Verify if origins, methods, and headers are properly set. Check `requirements.txt` for necessary dependencies.",
    agent=backend_specialist,
    expected_output="Analysis of backend configuration, specifically reporting on CORS status (CORS-001) and dependency completeness."
)

task_frontend = Task(
    description=f"Analyze `hyperflow-editor/src` and other frontend directories. Look for usage of 'Recharts'. Check if `ResponsiveContainer` is used correctly to avoid sizing issues (CHART-001).",
    agent=frontend_specialist,
    expected_output="Frontend component analysis, focusing on Recharts implementation and potential UI bugs."
)

task_devops = Task(
    description=f"Inspect `docker-compose.yml` and `Dockerfile`s. Check for service definitions, port mappings, and health checks. Verify if services like 'hypercode-core', 'postgres', and 'redis' are defined.",
    agent=devops_engineer,
    expected_output="DevOps configuration review, noting any missing services or unsafe container settings."
)

task_testing = Task(
    description=f"Look for `tests/` directories and test files (e.g., `test_*.py`). Estimate rough test coverage based on file existence. Check for CI workflows in `.github/workflows`.",
    agent=qa_engineer,
    expected_output="Testing maturity assessment, listing found test suites and CI pipelines."
)

task_security = Task(
    description=f"Scan for hardcoded API keys or secrets in `.env.example` or code files. Verify if security headers are configured in backend.",
    agent=security_engineer,
    expected_output="Security audit report highlighting vulnerabilities or exposed secrets."
)

task_documentation = Task(
    description=f"Check for `README.md`, `docs/` folder, and API documentation. Evaluate if instructions for setup and running are clear.",
    agent=documentation_writer,
    expected_output="Documentation quality score and list of missing key docs."
)

task_performance = Task(
    description=f"Look for potential performance issues like synchronous blocking calls in async endpoints, or heavy frontend bundles. Check docker resource limits if defined.",
    agent=performance_optimizer,
    expected_output="Performance review identifying potential bottlenecks."
)

task_integration = Task(
    description=f"Check frontend code for API base URLs. Verify if WebSocket connections (ws://) are handled correctly (WS-001). Check if backend has corresponding websocket endpoints.",
    agent=integration_specialist,
    expected_output="Integration status report, specifically on API and WebSocket connectivity."
)

task_synthesis = Task(
    description="Collect all findings from previous tasks. Create a JSON report following the structure: {executive_summary, component_scores, detailed_findings, action_plan}. Calculate an overall health score (0-100).",
    agent=project_manager,
    context=[task_structure, task_backend, task_frontend, task_devops, task_testing, task_security, task_documentation, task_performance, task_integration],
    expected_output="A complete JSON health check report."
)

# Create Crew
health_check_crew = Crew(
    agents=[
        system_architect,
        backend_specialist,
        frontend_specialist,
        devops_engineer,
        qa_engineer,
        security_engineer,
        documentation_writer,
        performance_optimizer,
        integration_specialist,
        project_manager
    ],
    tasks=[
        task_structure,
        task_backend,
        task_frontend,
        task_devops,
        task_testing,
        task_security,
        task_documentation,
        task_performance,
        task_integration,
        task_synthesis
    ],
    process=Process.sequential,
    planning=True,
    planning_llm=perplexity_llm,
    verbose=True
)

# Execute
def run_health_check():
    print("🚀 Starting HyperCode Health Check Crew...")
    print(f"📁 Scanning: {PROJECT_ROOT}")
    print(f"👥 Agents: 10")
    print(f"📋 Tasks: 10\n")
    
    result = health_check_crew.kickoff()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"health_check_report_{timestamp}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        # If result is not string (older crewai versions), handle it
        if not isinstance(result, str):
            try:
                # Try to extract output or convert to string
                final_output = str(result)
                # Try parsing if it looks like JSON
                try:
                    json_res = json.loads(final_output)
                    json.dump(json_res, f, indent=2)
                except:
                    f.write(final_output)
            except:
                f.write(str(result))
        else:
            try:
                 json_res = json.loads(result)
                 json.dump(json_res, f, indent=2)
            except:
                 f.write(result)
    
    print(f"\n✅ Health check complete!")
    print(f"📄 Report saved to: {report_path}")
    
    return result

if __name__ == "__main__":
    run_health_check()
