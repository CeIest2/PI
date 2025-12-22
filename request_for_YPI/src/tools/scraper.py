import requests
import trafilatura
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm

# Import your existing PDF tools
from src.utils.pdf_extractor import is_pdf_url, extract_text_from_pdf_url

def summarize_raw_content(text: str) -> str:
    """
    Condenses raw text to keep only the structure and facts.
    Uses the 'fast' model to avoid timeouts on large documents.
    """
    llm = get_llm(mode_or_model="fast")
    
    # --- NEUTRAL CONDENSATION PROMPT (ENGLISH) ---
    template = """
    ROLE: You are a text data compression algorithm.
    TASK: Reduce the text below to its absolute technical essence, keeping a structured format.

    STRICT GUIDELINES:
    1. NO COMPLEX SENTENCES: Use a telegraphic style (bullet points, short phrases).
    2. FORBIDDEN: Do NOT write introductions, conclusions, "In summary", or "Here is the key info".
    3. CONTENT: You MUST preserve Dates, Proper Names (Laws, Companies, People), Numbers, Protocols, and Technical Facts.
    4. STRUCTURE: Respect the original document hierarchy (Headers > Bullet points).
    5. NEUTRALITY: Do NOT add analysis, opinions, or external information. Only compress what is written.

    TEXT TO COMPRESS:
    {text}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        # Limit to first 50k chars to prevent context overflow/timeouts
        result = chain.invoke({"text": text[:50000]})
        return result.content
    except Exception as e:
        return f"[Synthesis Error]: {str(e)}\n(Returning truncated raw text)\n{text[:2000]}..."

@tool
def read_web_page(url: str) -> str:
    """
    Use this tool to scrape and read the MAIN CONTENT of a specific URL.
    
    WHEN TO USE:
    - Use this for Web Pages AND PDF files found via Google.
    - The tool automatically detects if the URL is a PDF and extracts text accordingly.
    """
    print(f"👀 [Scraper] Reading & Condensing: {url}")
    
    text = None
    source_type = "WEB"

    try:
        # 1. Immediate PDF check (via extension)
        if is_pdf_url(url):
            print("   ↳ 📄 PDF detected (via URL). Extracting with PyMuPDF...")
            text = extract_text_from_pdf_url(url)
            source_type = "PDF"
        
        # 2. If not an obvious PDF, try standard Web download
        if not text:
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded is None:
                return f"Error: Could not fetch URL {url} (403 Forbidden or timeout)."
            
            # 3. Content Check (Hidden PDF?)
            # Check if start bytes look like '%PDF'
            is_hidden_pdf = False
            if isinstance(downloaded, bytes) and downloaded.startswith(b'%PDF'):
                is_hidden_pdf = True
            elif isinstance(downloaded, str) and downloaded.startswith('%PDF'):
                is_hidden_pdf = True
                
            if is_hidden_pdf:
                print("   ↳ 📄 PDF detected (Binary Signature). Extracting with PyMuPDF...")
                text = extract_text_from_pdf_url(url)
                source_type = "PDF"
            else:
                # It is standard HTML
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)

        # Final Validation
        if text is None or not text.strip():
            return "Error: No main content found (page might be empty or unreadable)."

        # Summarization Step
        final_text = text
        if len(text) > 1000:
            print(f"   ↳ 🧠 Compressing content {source_type} ({len(text)} chars)...")
            final_text = summarize_raw_content(text)

        # --- OUTPUT FORMAT FIX ---
        # Using XML tags prevents the LLM from confusing text with function calls
        return f"""
<DOCUMENT_CONTENT>
<URL>{url}</URL>
<TYPE>{source_type}</TYPE>
<CONTENT>
{final_text}
</CONTENT>
</DOCUMENT_CONTENT>
"""

    except Exception as e:
        return f"Error scraping page: {str(e)}"