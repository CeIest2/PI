from src.utils.loaders import load_text_file
from pathlib import Path

def get_definition(indicator_name):
    """
    Retrieves the definition for a specific indicator from the text file.
    """
    current_dir = Path(__file__).parent.parent.parent
    print(current_dir)

    definition_path = current_dir / "prompt" / "index_definition.txt"

    if not definition_path.exists():
         return f"Error: Definition file not found at {definition_path}"

    try:
        text_content = load_text_file(str(definition_path))
        
        marker = f"**INDICATOR: {indicator_name}**"
        if marker in text_content:
            start = text_content.index(marker)
            snippet = text_content[start:].split("\n\n")[0] 
            return snippet.strip()
            
        return "Definition not found."
        
    except Exception as e:
        return f"Error reading definition file: {e}"