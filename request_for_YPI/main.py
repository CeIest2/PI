# main.py
import sys
from langchain_core.messages import HumanMessage
from src.agents.graph import graph
from dotenv import load_dotenv

def main():
    query = "Quelle est la situation de la fibre optique en France ?"
    
    mode_choisi = "smart" 
    
    # Exemple simple : si on lance "python main.py fast", on passe en mode rapide
    if len(sys.argv) > 1 and sys.argv[1] in ["fast", "smart"]:
        mode_choisi = sys.argv[1]
        print(f"⚡ Mode forcé : {mode_choisi.upper()}")

    initial_state = {"messages": [HumanMessage(content=query)]}

    # C'est ici que la magie opère : on passe le paramètre 'configurable'
    config = {"configurable": {"mode": mode_choisi}}

    print(f"🚀 Lancement de l'agent en mode {mode_choisi}...\n")
    
    # L'agent utilisera le modèle correspondant tout au long de cette exécution
    final_state = graph.invoke(initial_state, config=config)
    
    print("\n🏁 Réponse finale :")
    print(final_state["messages"][-1].content)

if __name__ == "__main__":
    load_dotenv()
    main()