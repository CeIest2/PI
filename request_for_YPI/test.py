from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry



if __name__ == "__main__":
    load_dotenv()

    req = process_user_request_with_retry("Liste des entreprises technologiques basées en Allemagne ayant plus de 500 employés.")

    print(f"{req=}")