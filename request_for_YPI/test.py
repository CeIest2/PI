from src.request_IYP.prompt_to_request import generate_cypher_for_request, main
from src.request_IYP.request_testing import execute_generated_queries
import langchain
import os
from dotenv import load_dotenv



if __name__ == "__main__":
    load_dotenv()

    req = main()

    print("Requête utilisateur :", req)

    sorite = execute_generated_queries(req)
    print("Requête Cypher générée :", sorite)