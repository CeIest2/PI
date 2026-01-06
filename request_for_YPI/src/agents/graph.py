# src/agents/graph.py
import os
from typing import TypedDict, Annotated 
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages # <--- IMPORT CRUCIAL

from src.utils.llm import get_llm
from src.utils.loaders import load_text_file

# Import de vos outils
from src.tools.google import search_google
from src.tools.scraper import read_web_page
from src.tools.neo4j import run_infrastructure_query

def get_system_prompt():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    prompt_path = os.path.join(project_root, "prompt", "render_document_thinking.txt")
    
    try:
        print(f"📄 Chargement du System Prompt depuis : {prompt_path}")
        content = load_text_file(prompt_path)
        return content
    except Exception as e:
        print(f"⚠️ Warning: Impossible de charger le fichier prompt ({e}). Utilisation du défaut.")
        return "You are an expert strategic intelligence analyst for Internet infrastructure."

# --- DEFINITION DU GRAPHE ---

class AgentState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

tools = [search_google, read_web_page, run_infrastructure_query]

def agent_node(state: AgentState, config: RunnableConfig):
    mode = config.get("configurable", {}).get("mode", "smart")
    llm = get_llm(mode_or_model=mode)
    
    system_prompt_content = get_system_prompt()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_content),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm.bind_tools(tools)
    
    response = chain.invoke({"messages": state["messages"]})
    return {"messages": [response]}

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")

def should_continue(state):
    # On regarde le dernier message de la liste
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

graph = workflow.compile()