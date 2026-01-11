from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry



if __name__ == "__main__":
    load_dotenv()

    req = process_user_request_with_retry("Est-ce qu'il y a plus d'ASNs français présents sur des IXP aux États-Unis que d'ASNs américains présents sur des IXP en France ?")

    print(f"{req=}")