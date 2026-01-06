# src/tools/scraper.py
import requests
import trafilatura
from langchain_core.tools import tool

@tool
def read_web_page(url: str) -> str:
    """
    Use this tool to scrape and read the MAIN CONTENT of a specific web URL.
    It removes ads, menus, and sidebars automatically to save tokens.
    """
    print(f"👀 [Scraper] Reading (Smart Mode): {url}")
    
    try:
        # 1. Téléchargement intelligent (gère déjà les User-Agents et timeouts)
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            return "Error: Could not fetch URL (403 Forbidden or timeout)."

        # 2. Extraction du texte principal (c'est là que la magie opère)
        # include_comments=False pour économiser des tokens
        # include_tables=True car les tableaux sont souvent importants
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
        
        if text is None:
            return "Error: No main content found (page might be empty or pure Javascript)."

        if len(text) > 100000:
            return f"Warning: Text is very long ({len(text)} chars). Here is the beginning:\n\n" + text[:100000]
            
        return text

    except Exception as e:
        return f"Error scraping page: {str(e)}"