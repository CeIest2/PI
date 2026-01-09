from src.utils.logger import logger
from src.utils.llm import get_llm
from langchain_core.prompts import ChatPromptTemplate
from src.utils.loaders import load_text_file
import os





def summarize_raw_content(text: str, summarize_type='standard') -> str:
    """Génère un résumé du contenu brut (pour l'agent)."""
    llm = get_llm(mode_or_model="fast")

    if summarize_type == 'short':
        prompt_path = os.path.join("prompt", "summarize_text_for_rag_resume.txt")
    else:
        prompt_path = os.path.join("prompt", "summarize_raw_content.txt")

    text_prompt = load_text_file(prompt_path)


    prompt = ChatPromptTemplate.from_template(text_prompt)
    chain  = prompt | llm
    result = chain.invoke({"text": text[:50000]})
    return result.content
