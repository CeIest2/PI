from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.logger import logger
import json
from src.request_IYP.interface import generate_response_with_IYP


if __name__ == "__main__":
    load_dotenv()
    
    print(generate_response_with_IYP("""Quels opérateurs étrangers détiennent une position dominante sur le marché en France ?""",logger_active=True))
 