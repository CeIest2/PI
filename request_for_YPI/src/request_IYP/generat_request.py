import json
import re
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file
from src.request_IYP.analyse_results_request import analyze_and_correct_query
from src.request_IYP.request_testing import execute_cypher_test
from src.utils.country_utils import load_country_mapping, apply_country_mapping
from src.request_IYP.probes_execution import execute_multiple_probes


def clean_json_string(content: str) -> str:
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def generate_cypher_for_request(user_intent: str, mode: str = "smart", research: bool = False, additional_context: str = "") -> Dict[str, Any]:
    llm = get_llm(mode)
    
    current_dir = Path(__file__).parent.parent.parent
    iy_schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP_documentation.txt")) 
    
    if research:
        system_prompt_request_generation = load_text_file(os.path.join(current_dir, "prompt", "cypher_request_research_generation.txt"))
    else:
        system_prompt_request_generation = load_text_file(os.path.join(current_dir, "prompt", "cypher_request_generation.txt"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_request_generation),
        ("human", "Request: {input}")
    ])
    
    chain = prompt | llm
    response_msg = chain.invoke({
        "input": user_intent,
        "schema": iy_schema_content 
    })
    
    content     = response_msg.content
    country_map = load_country_mapping()
    json_str    = clean_json_string(content)
    result      = json.loads(json_str)
    result["user_intent"] = user_intent
    
    if result.get("possible") and result.get("queries"):
        result["queries"] = apply_country_mapping(result["queries"], country_map)

    print(f"{result=}\n####")
    return result
    
