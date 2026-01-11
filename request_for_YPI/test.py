from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry



if __name__ == "__main__":
    load_dotenv()
    request = """
Dans combien de pays des server youtube sont ils hébergés?
    """
    req = process_user_request_with_retry(request)

    print(f"{req=}")