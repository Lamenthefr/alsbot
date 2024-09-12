import os
import requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from dotenv import load_dotenv
import utils
import database

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

NOWPAYMENTS_API_KEY = os.getenv('NOWPAYMENTS_API_KEY')

# Vérifiez si la clé API est chargée correctement
if not NOWPAYMENTS_API_KEY:
    logging.error("Erreur : la clé API NowPayments n'a pas été trouvée. Assurez-vous que le fichier .env contient la clé API.")

def show_deposit_options(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    user = database.get_user(user_id)
    if not user:
        database.create_user_if_not_exists(user_id, username)
        user = database.get_user(user_id)

    if not user:
        query.edit_message_text(text="Erreur lors de la création du profil utilisateur.")
        return

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')],
        [InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')]
    ]
    text = f"🔱 Salut, @{user[1]} !🔱\n" \
           "🔱 Vous êtes actuellement sur la première version de notre autoshop...\n" \
           f"💰 Solde: {user[2]:.2f}€"
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

def ask_deposit_amount(update, context):
    query = update.callback_query
    currency = query.data.split('_')[1]  # Extraction de la monnaie à partir du callback_data
    context.user_data['currency'] = currency
    query.edit_message_text(
        text="🔱 Combien voulez-vous déposer ? (Minimum 10€) 🔱",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')]])
    )
    context.user_data['state'] = 'ASK_AMOUNT'

def handle_message(update: Update, context: CallbackContext):
    state = context.user_data.get('state')
    if state == "ASK_AMOUNT":
        try:
            amount = float(update.message.text)
            if amount >= 10:
                currency = context.user_data['currency']
                handle_crypto_deposit(update.message.chat_id, currency, amount, context)
            else:
                update.message.reply_text("🔱 Le montant minimum pour un dépôt est de 10€. Veuillez réessayer. 🔱")
        except ValueError:
            update.message.reply_text("🔱 Veuillez entrer un montant valide. 🔱")
    else:
        update.message.reply_text("🔱 Commande non reconnue. 🔱")

def handle_crypto_deposit(chat_id, currency, amount, context):
    user_id = chat_id
    response = create_payment_request(amount, currency, user_id)
    if response is None:
        context.bot.send_message(chat_id=chat_id, text="🔱 Erreur lors de la création de la demande de paiement. Veuillez réessayer plus tard. 🔱")
        return
    if response.get('payment_status') == 'waiting':
        address = response['pay_address']

        # Générer le QR code pour l'adresse
        qr_code_path = utils.generate_qr_code(address)

        # Envoyer le message avec le QR code et l'adresse
        context.bot.send_photo(
            chat_id=chat_id,
            photo=open(qr_code_path, 'rb'),
            caption=f"🔱 Veuillez envoyer {response['pay_amount']} {currency.upper()} à l'adresse suivante pour créditer votre compte :\n`{address}`\n\n"
                    f"🔱 Temps restant pour effectuer le paiement : 19:00",
            parse_mode='Markdown'
        )
    else:
        context.bot.send_message(chat_id=chat_id, text="🔱 Erreur lors de la création de la demande de paiement. Veuillez réessayer plus tard. 🔱")

def create_payment_request(amount, currency, user_id):
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'price_amount': amount,
        'price_currency': 'EUR',
        'pay_currency': currency.upper(),
        'order_description': f"Deposit by user {user_id}"
    }
    try:
        response = requests.post('https://api.nowpayments.io/v1/payment', headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to create payment request: {e}")
        return None
