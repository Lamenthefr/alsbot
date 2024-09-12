import logging
import os
from telegram.ext import Updater
from commands.menu import add_handlers
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du journal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Démarrage du bot...")

# Récupérer le token depuis les variables d'environnement
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logging.error("Erreur : le token Telegram n'a pas été trouvé. Assurez-vous que le fichier .env contient la clé API sous la variable TELEGRAM_BOT_TOKEN.")
    exit(1)

# Initialisation du bot
updater = Updater(TOKEN, use_context=True)

# Ajouter les handlers
dp = updater.dispatcher
add_handlers(dp)

# Démarrer le bot
updater.start_polling()
logging.info("Le bot est en cours d'exécution...")
updater.idle()
