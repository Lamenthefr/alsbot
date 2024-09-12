from telegram.ext import Updater
import commands

def main():
    TOKEN = "7123801340:AAEo2apAvb4cS2na9_9FdNkaPLv2HuSrUxc"  # Votre token de bot admin
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    commands.add_handlers(dp)  # Ajoute les gestionnaires définis dans commands.py

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
