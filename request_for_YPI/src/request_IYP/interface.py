# src/request_IYP/interface.py
import json
import os
from pathlib import Path
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.llm import get_llm
from src.utils.logger import logger
from langchain_core.prompts import ChatPromptTemplate
from src.utils.loaders import load_text_file

def generate_response_with_IYP(query_intent: str, logger_active: bool = False) -> dict:
    """Generates a response for a given user intent using the IYP system.
    Returns:
        dict: {
            'status': 'valide'|'invalide',
            'request': str|None,
            'results': str|None
        }
    """
    if logger_active :logger.section("IYP INTERFACE")
    if logger_active :logger.info(f"Processing intent: {query_intent}")
    
    pipeline_result = process_user_request_with_retry(query_intent, logger_active=logger_active)
    
    if pipeline_result.get("status") == "SUCCESS":
        final_query = pipeline_result.get("final_query")
        raw_data = pipeline_result.get("data")
        
        interpretation = _interpret_results(query_intent, raw_data, logger_active=logger_active)
        
        formatted_output = f"""### RAW DATABASE FINDINGS
    {json.dumps(raw_data, indent=2, ensure_ascii=False)}
    ### ANALYSIS AND ANSWER
    {interpretation}"""
        
        return {
            'status': 'valide',
            'request': final_query,
            'results': formatted_output
        }
    else:
        # Handle failure cases
        error_msg = pipeline_result.get("message") or pipeline_result.get("reason", "Unknown pipeline error")
        if logger_active :logger.error(f"Interface failed to retrieve valid data: {error_msg}")
        
        return {
            'status': 'invalide',
            'request': None,
            'results': None
        }

def _interpret_results(intent: str, data: list, logger_active: bool = False) -> str:

    llm = get_llm("smart")
    
    current_dir = Path(__file__).parent.parent.parent
    system_prompt = load_text_file(os.path.join(current_dir, "prompt", "IYP", "cypher_request_research_generation.txt"))

    human_prompt = """User Intent: {intent}
Extracted Data:
{data_json}
Please provide a detailed interpretation and answer the original question:"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "intent": intent,
            "data_json": json.dumps(data, indent=2, ensure_ascii=False)
        })
        return response.content.strip()
    except Exception as e:
        if logger_active :logger.error(f"Error during result interpretation: {e}")
        return "Désolé, une erreur est survenue lors de l'interprétation des données."
    

