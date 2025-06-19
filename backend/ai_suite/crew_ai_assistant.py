from crewai import Crew, Agent, Task
from langchain_groq import ChatGroq


llm = ChatGroq(
    model="groq/llama-3.1-8b-instant",
    temperature=0.4,
)

def get_project_intelligence(project_data, task_data, developer_summary):

    # === Agents ===
    health_analyst = Agent(
        role="Project Health Analyst",
        goal="Assess project health including risks, delays, and budget issues.",
        backstory="You are a senior Agile auditor who reviews project progress and risk factors.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    workload_analyst = Agent(
        role="Developer Workload Analyst",
        goal="Evaluate developer workload and identify potential overwork or inefficiencies.",
        backstory="A technical lead with experience in balancing resources and preventing bottlenecks.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    # improvement_advisor = Agent(
    #     role="Execution Advisor",
    #     goal="Give execution improvement strategies and one AI automation suggestion.",
    #     backstory="You're a project strategist known for unlocking team efficiency with minimal changes.",
    #     verbose=True,
    #     allow_delegation=False,
    #     llm=llm,
    # )
    
    synthesizer_agent = Agent(
        role="AI Project Reporter",
        goal="Create a clear, strategic, and structured report for admin based on all prior evaluations.",
        backstory="You're a senior AI assistant experienced in project reporting, clarity, and executive summaries.",
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task1 = Task(
    description=(
        "You are analyzing the health of multiple software projects. "
        "Each project is listed by name along with its tasks and status.\n\n"
        f"{project_data}\n\n"
        "Analyze:\n"
        "- Give each project a health score (1–10)\n"
        "- List project-specific delays, blocked paths, or resource misalignments\n"
        "- Highlight projects at risk (budget, deadline, etc.)"
    ),
    expected_output="A Markdown summary listing each project with: health score, 1-2 issues (if any), and risk flag.",
    agent=health_analyst,
)


    task2 = Task(
    description=(
        "You are analyzing developer workload across multiple projects.\n\n"
        "Each developer may be assigned tasks from different projects. "
        "You will find imbalances in their task loads and recommend adjustments.\n\n"
        f"{task_data}\n\n"
        f"{developer_summary}\n\n"
        "Analyze:\n"
        "- Who is overloaded or underutilized\n"
        "- Which tasks are blocked or unassigned\n"
        "- Recommend task redistribution project-wise"
    ),
    expected_output="Developer-wise and project-wise workload analysis and redistribution plan.",
    agent=workload_analyst,
)


    # task3 = Task(
    # description=(
    #     f"Context:\n{project_data}\n\n"
    #     f"Developer Summary:\n{developer_summary}\n\n"
    #     f"Tasks:\n{task_data}\n\n"
    #     "Suggest:\n"
    #     "- 3 quick improvements to task execution or timelines\n"
    #     "- 1 AI-powered automation idea to speed up workflows"
    # ),
    # expected_output="Improvement suggestions and automation idea.",
    # agent=improvement_advisor,
    # )

    # === Final Report Task ===
    final_summary_task = Task(
    description=(
        "You are given detailed outputs from the following experts:\n"
        "1. Project Health Analyst\n"
        "2. Developer Workload Evaluator\n"
        "3. Productivity Advisor\n\n"
        "Your job is to consolidate all the insights into a clear, well-structured Markdown report with the following sections:\n"
        "## Executive Summary\n"
        "## Developer Workload Overview\n"
        "## Project Health Insights\n"
        "## Recommendations\n"
        "Ensure smooth narrative flow, avoid duplication, and present only the most relevant and actionable points."
    ),
    expected_output="A final report in clean, readable Markdown format as described.",
    agent=synthesizer_agent,
    context=[task1, task2],
)

    # === Crew Setup ===
    crew = Crew(
        agents=[health_analyst, workload_analyst, synthesizer_agent ],
        tasks=[task1, task2, final_summary_task],
        verbose=True,
    )

    try:
        return crew.kickoff()
    except RuntimeError as e:
        print(f"Crew execution error: {e}")
        return None

