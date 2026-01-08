# src/utils/logger.py
import threading
from datetime import datetime

class ConsoleLogger:
    _lock = threading.Lock()
    
    # Codes couleurs ANSI
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    # Mettre à False pour masquer les détails techniques (LLM load, paths, etc.)
    VERBOSE = False 

    @staticmethod
    def _print(text):
        """Impression thread-safe pour éviter le mélange des lignes"""
        with ConsoleLogger._lock:
            print(text)

    @staticmethod
    def info(msg):
        """Information générale (ex: Étape en cours)"""
        ConsoleLogger._print(f"{ConsoleLogger.CYAN}ℹ️  {msg}{ConsoleLogger.ENDC}")

    @staticmethod
    def success(msg):
        """Succès (ex: Document trouvé)"""
        ConsoleLogger._print(f"{ConsoleLogger.GREEN}✅ {msg}{ConsoleLogger.ENDC}")

    @staticmethod
    def warning(msg):
        """Attention (ex: PDF vide, rejeté)"""
        ConsoleLogger._print(f"{ConsoleLogger.WARNING}⚠️  {msg}{ConsoleLogger.ENDC}")

    @staticmethod
    def error(msg):
        """Erreur critique"""
        ConsoleLogger._print(f"{ConsoleLogger.FAIL}❌ {msg}{ConsoleLogger.ENDC}")

    @staticmethod
    def section(msg):
        """Grands titres de sections"""
        ConsoleLogger._print(f"\n{ConsoleLogger.HEADER}{ConsoleLogger.BOLD}=== {msg.upper()} ==={ConsoleLogger.ENDC}")

    @staticmethod
    def debug(msg):
        """Détails techniques (affichés seulement si VERBOSE = True)"""
        if ConsoleLogger.VERBOSE:
            ConsoleLogger._print(f"\033[90m⚙️  [DEBUG] {msg}{ConsoleLogger.ENDC}")

# Instance globale facile à importer
logger = ConsoleLogger()