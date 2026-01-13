from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.logger import logger
import json
from src.request_IYP.interface import generate_response_with_IYP


if __name__ == "__main__":
    load_dotenv()
    
    print(generate_response_with_IYP("""Combine il y a de IXP en france
    """,logger_active=False))
 