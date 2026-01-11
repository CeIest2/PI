import json
import re
import os
from typing import Dict, Any, List
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.utils.country_utils import load_country_mapping, apply_country_mapping


def clean_json_string(content: str) -> str:
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def analyze_and_correct_query(execution_report: Dict[str, Any], mode: str = "smart") -> Dict[str, Any]:
    llm = get_llm(mode)
    
    user_intent = execution_report.get("user_intent", "")
    results = execution_report.get("results", [])
    
    if not results:
        return {"status": "ERROR", "message": "Aucun résultat à analyser", "corrected_query": None}

    first_res = results[0]
    failed_query = first_res.get("cypher", "N/A")
    
    if not first_res.get("success", False):
        execution_context = f"Neo4j Technical Error: {first_res.get('error')}"
        data_sample = "None (Error)"
    else:
        count = first_res.get("count", 0)
        data_sample = json.dumps(first_res.get("data", [])[:5], indent=2)
        execution_context = f"Query ran successfully and returned {count} rows."

    current_dir = Path(__file__).parent.parent.parent
    schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP_documentation.txt"))

    # 1. On définit les règles générales dans le système
    system_prompt = """You are a Senior Neo4j Expert & Data Analyst for the YPI project.
    
    STRICT SCHEMA:
    {schema}
    
    TASK:
    Evaluate if the Cypher query and the resulting data correctly and fully answer the User Intent.
    
    CRITERIA FOR VALIDATION:
    1. Technical: No syntax errors.
    2. Logic: Follow the Schema relations.
    3. Sufficiency: Data must allow a human to answer the question (e.g., need names, not just IDs).
    
    OUTPUT FORMAT (JSON):
    {{
        "possible": true/false,
        "explanation": "Explain why it is sufficient or what is missing.",
        "correction": "A new Cypher query if 'possible' is false, otherwise null."
    }}
    """

    # 2. On passe les données de l'erreur dans le message "human"
    # Cela garantit que l'API reçoit du "content"
    human_prompt = """Please analyze the following execution report:
    - User Intent: {intent}
    - Executed Cypher: {failed_query}
    - Execution Status: {execution_context}
    - Data Returned (Sample): {data_sample}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    print(f"🧠 [Analyse] Le LLM évalue la pertinence de la réponse...")

    response = chain.invoke({
        "intent": user_intent,
        "failed_query": failed_query,
        "execution_context": execution_context,
        "data_sample": data_sample,
        "schema": schema_content
    })
    
    try:
        res_json = json.loads(clean_json_string(response.content))

        # Note: J'ai corrigé "analysis" en "explanation" pour correspondre au prompt
        if res_json.get("possible") is True:
            return {
                "status": "VALID",
                "message": res_json.get("explanation"),
                "corrected_query": None
            }
        else:
            raw_correction = res_json.get("correction")
            final_query = None
            if raw_correction:
                mapping = load_country_mapping()
                corrected_list = apply_country_mapping([raw_correction], mapping)
                final_query = corrected_list[0]

            return {
                "status": "CORRECTED",
                "message": res_json.get("explanation"),
                "corrected_query": final_query
            }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Echec de l'analyse LLM: {str(e)}",
            "corrected_query": None
        }

