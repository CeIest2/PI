import json
import re
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file

def clean_json_string(content: str) -> str:
    """Nettoie la réponse du LLM pour extraire le JSON valide."""
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def generate_cypher_for_request(user_intent: str, mode: str = "smart") -> Dict[str, Any]:
    
    llm = get_llm(mode)
    
    current_dir = Path(__file__).parent.parent.parent
    # On charge le schéma mais on ne l'injecte pas tout de suite
    iy_schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP_documentation.txt")) # J'ai mis index_definition.txt qui est votre "Master v3.0"
    system_prompt = """You are a Neo4j Cypher Expert for the YPI (Your Perfect Internet) project.
    
    TYPE OF DATABASE:
    Graph Database containing ASNs, Countries, Prefixes, Domains, and IXPs.
    
    STRICT SCHEMA (THE LAW):
    {schema}
    
    TASK:
    Translate the user request into a JSON object containing Cypher queries.
    
    CONTEXT QUALITY RULES (CRITICAL FOR LLM):
    The results of your queries will be fed into another LLM to write a report. 
    **Raw IDs (like ASN 1234) or NULL values are USELESS.**
    
    1. **ALWAYS Fetch Readable Names (NO DUPLICATES):** - `org_name` on `:AS` is often NULL. You MUST join with `:Name`.
       - **CRITICAL:** An AS often has multiple names. You **MUST AGGREGATE** them to avoid duplicate rows.
       - **Pattern to use:**
         ```cypher
         MATCH ...
         OPTIONAL MATCH (a)-[:NAME]->(n:Name)
         WITH a, r, head(collect(n.name)) as unique_name // Keep only the first name found
         RETURN COALESCE(unique_name, a.org_name, toString(a.asn)) AS OperatorName
         ```
       
    2. **Self-Explanatory Column Names:**
       - Do NOT return `r.percent`. Return `r.percent AS MarketShare`.
       - Do NOT return `count(a)`. Return `count(a) AS IXP_Count`.
    
    CRITICAL RULES (DO NOT HALLUCINATE):
    1. **NO Imaginary Relations:** - Do NOT use `BELONGS_TO`, `OPERATES`.
       - Do NOT use `ANNOUNCES`. Use **`[:ORIGINATE]`** for Prefixes.
       - Use schema relations only.
    2. **NO Imaginary Nodes:** Do NOT use `:Operator`. Use `:AS`.
    3. **Correct Properties:** - `country_code` (not code).
       - `r.percent` (not population_percent).
       - `participant_count` (singular, not participants_count).
    
    4. **COUNTRY CODES (PLACEHOLDERS):**
       - **Do NOT guess** the ISO-2 code (e.g. do not guess 'IR' for Iran).
       - **Use this EXACT placeholder format:** `__COUNTRY_EnglishName__`
       - **CRITICAL:** Even if the user asks in French (e.g., "Chine", "Corée du Sud"), you MUST **translate the country name to English** inside the placeholder.
       - **Example:** User says "Chine" -> Write `MATCH (c:Country {{country_code: '__COUNTRY_China__' }})`
       - **Example:** User says "Iran" -> Write `MATCH (c:Country {{country_code: '__COUNTRY_Iran__' }})`
       - Our system will replace this English placeholder with the correct ISO code using a lookup file.
    
    PROXY LOGIC (Be Smart):
    - "Market Share" -> Use `(:AS)-[:POPULATION]->(:Country)` ordered by `r.percent`.
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "possible": true/false,
        "explanation": "Explain logic & proxy usage.",
        "queries": [
            "MATCH ... WITH ... RETURN ..."
        ]
    }}
    
    IMPORTANT FORMATTING RULE (SINGLE STRING):
    - **Each query must be a SINGLE string in the JSON array.**
    
    Do not add comments outside the JSON.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Request: {input}")
    ])
    
    chain = prompt | llm
    
    print(f"🤖 [CypherGen] Analyse : '{user_intent}'")
    
    # MODIFICATION 4 : On passe le schéma ici, comme une variable
    response_msg = chain.invoke({
        "input": user_intent,
        "schema": iy_schema_content 
    })
    
    content = response_msg.content
    country_map = load_country_mapping()

    json_str = clean_json_string(content)
    result = json.loads(json_str)
    
    if result.get("possible") and result.get("queries"):
        result["queries"] = apply_country_mapping(result["queries"], country_map)
        
    return result
        




def load_country_mapping() -> Dict[str, str]:
    """Charge le fichier 'Nom -> Code' dans un dictionnaire."""
    mapping = {}
    current_dir = Path(__file__).parent.parent.parent
    file_path = os.path.join(current_dir, "prompt", "country_code.txt")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "->" in line:
                name, code = line.split("->")
                # On nettoie : " France " -> "france", " FR \n" -> "FR"
                mapping[name.strip().lower()] = code.strip()
    return mapping


def apply_country_mapping(queries: List[str], mapping: Dict[str, str]) -> List[str]:
    """Remplace __COUNTRY_Nom__ par le code ISO correspondant."""
    processed_queries = []
    for query in queries:
        matches = re.findall(r"__COUNTRY_(.+?)__", query)
        for country_name in matches:
            code = mapping.get(country_name.lower())
            placeholder = f"__COUNTRY_{country_name}__"
            if code:
                print(f"🌍 [Mapping] Remplacement : {placeholder} -> '{code}'")
                query = query.replace(placeholder, code)
            else:
                print(f"❌ [Mapping] Pays introuvable dans le fichier : {country_name}")
        processed_queries.append(query)
    return processed_queries












def main():
    # Test 1: Demande valide
    req1 = " Quels sont les plus gros points d'échange internet (IXP) au Japon ?"
    res1 = generate_cypher_for_request(req1)
    print(f"\nResultat 1 ({req1}):\n", json.dumps(res1, indent=2))

    # Test 2: Demande impossible
    req2 = "Quels opérateurs aux États-Unis annoncent le plus de préfixes IPv6 ?"
    res2 = generate_cypher_for_request(req2)
    print(f"\nResultat 2 ({req2}):\n", json.dumps(res2, indent=2))

if __name__ == "__main__":
    main()