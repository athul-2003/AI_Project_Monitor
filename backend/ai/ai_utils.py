# backend/ai/ai_utils.py
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from django.conf import settings

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
)

# Define prompt template for summaries and suggestions
prompt_template = PromptTemplate(
    input_variables=["title", "description", "status", "deadline", "assigned_developers","tasks", "comments"],
    template="""
    You are an expert AI project management assistant with deep knowledge of project lifecycle, risk assessment, and team coordination. Analyze the following project details thoroughly and provide a detailed, insightful response in the exact format specified below. Focus on actionable insights and practical solutions tailored to the project's current state.

    Project Details:
    Title: {title}
    Description: {description}
    Status: {status}
    Deadline: {deadline}
    Assigned Developers: {assigned_developers}
    Tasks: {tasks}
    comments : {comments}
    

    Provide:
    1. A detailed summary of the project's current state (50-100 words), highlighting key aspects such as task progress, challenges, team involvement, and timeline adherence. Assess the overall health of the project.
    2. Three specific, prioritized suggestions to improve the project or get it back on track. Each suggestion should be practical, detailed, and tailored to the project's context (e.g., address specific issues, resource constraints, or team dynamics).

    Output Format (follow exactly, no additional text or deviations):
    Summary: [Your detailed summary here, assessing the project's health and key points.]
    Suggestions:
    - [Priority 1: A detailed, actionable suggestion addressing a core issue or opportunity.]
    - [Priority 2: Another specific suggestion to enhance progress or mitigate risks.]
    - [Priority 3: A final targeted recommendation to support project success.]
    """
)
# Create chain for processing input
chain = prompt_template | llm

def get_project_insights(project_data):
    """
    Generate summary and suggestions for a given project using LangChain and Groq.
    Returns a dictionary with summary and suggestions.
    """
    # Ensure project_data is already a dictionary
    response = chain.invoke(project_data)
    # print(response)
    
    # Extract content from response if it's a structured object (e.g., AIMessage)
    if hasattr(response, 'content'):
        response_content = response.content
    else:
        response_content = str(response)
    
    # Parse response into structured output
    lines = response_content.splitlines()
    summary = ""
    suggestions = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("Summary:"):
            current_section = "summary"
            summary = line.replace("Summary:", "").strip()
        elif line.startswith("Suggestions:"):
            current_section = "suggestions"
        elif line.startswith("-") and current_section == "suggestions":
            suggestions.append(line.replace("-", "").strip())
    
    return {
        "summary": summary if summary else "No summary provided.",
        "suggestions": suggestions if suggestions else ["No suggestions available."]
    }