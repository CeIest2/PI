from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry



if __name__ == "__main__":
    load_dotenv()

    req = process_user_request_with_retry("Donne-moi la liste des ASNs brésiliens (BR) qui ont plus de 10% de blocage TCP et qui n'utilisent aucun serveur DNS sécurisé (DNSSEC).")

    print(f"{req=}")