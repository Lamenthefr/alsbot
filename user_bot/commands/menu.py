import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext  # Ajout de CommandHandler et CallbackQueryHandler
import database

# Configuration du journal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def start(update, context):
    logging.info("Commande /start reçue.")

    if update.message:
        user_id = update.message.chat_id
        username = update.message.from_user.username
    else:
        user_id = update.callback_query.message.chat_id
        username = update.callback_query.from_user.username

    logging.info(f"Récupération de l'utilisateur {user_id}.")
    user = database.get_user(user_id)

    if not user:
        logging.error(f"Utilisateur {user_id} introuvable.")
        logging.info(f"Création de l'utilisateur {user_id} avec le nom d'utilisateur {username}.")
        database.create_user_if_not_exists(user_id, username)
        user = database.get_user(user_id)

    if not user:
        if update.message:
            update.message.reply_text("Erreur : impossible de créer ou récupérer l'utilisateur.")
        else:
            update.callback_query.edit_message_text("Erreur : impossible de créer ou récupérer l'utilisateur.")
        return

    if update.message:
        update.message.reply_text(
            text="🔱 Bienvenue dans le bot. Que souhaitez-vous faire ?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔱 Magasin 🔱", callback_data='shop')],
                [InlineKeyboardButton("🔱 Mon Profil 🔱", callback_data='profile')],
                [InlineKeyboardButton("🔱 Dépôt Crypto 🔱", callback_data='deposit_crypto')]
            ])
        )
    else:
        update.callback_query.edit_message_text(
            text="🔱 Bienvenue dans le bot. Que souhaitez-vous faire ?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔱 Magasin 🔱", callback_data='shop')],
                [InlineKeyboardButton("🔱 Mon Profil 🔱", callback_data='profile')],
                [InlineKeyboardButton("🔱 Dépôt Crypto 🔱", callback_data='deposit_crypto')]
            ])
        )
    logging.info("Menu principal affiché.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'profile':
        show_profile(query)
    elif query.data == 'shop':
        show_shop(query)
    elif query.data == 'deposit_crypto':
        show_deposit_options(query)
    elif query.data == 'start':
        start(update, context)
    elif query.data.startswith('catalogue_'):
        catalogue_id = int(query.data.split('_')[1])
        show_catalogue(query, catalogue_id)
    elif query.data.startswith('sub_catalogue_'):
        sub_catalogue_id = int(query.data.split('_')[1])
        show_sub_catalogue(query, sub_catalogue_id)
    elif query.data.startswith('product_'):
        product_id = int(query.data.split('_')[1])
        process_purchase(query, product_id)

def show_profile(query):
    user = database.get_user(query.from_user.id)
    if user is None:
        text = "🔱 Aucun profil utilisateur trouvé. Veuillez effectuer un dépôt pour activer votre profil. 🔱"
    else:
        text = f"🔱 Nom d'utilisateur: @{user[1]}\n" \
               f"🔱 Votre ID: {user[0]}\n" \
               f"🔱 Solde: {user[2]:.2f}€\n" \
               f"🔱 Dépôts Total: {user[3]:.2f}€"
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')]]))

def show_shop(query):
    catalogues = database.get_catalogues()
    keyboard = [[InlineKeyboardButton(c[1], callback_data=f"catalogue_{c[0]}")] for c in catalogues]
    keyboard.append([InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')])
    query.edit_message_text(
        text="🔱 HORUS 🔱 Shop, choisissez une option ci-dessous.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def show_catalogue(query, catalogue_id):
    sub_catalogues = database.get_sub_catalogues(catalogue_id)
    if sub_catalogues:
        keyboard = [[InlineKeyboardButton(sc[1], callback_data=f"sub_catalogue_{sc[0]}")] for sc in sub_catalogues]
        keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='shop')])
        query.edit_message_text(
            text="🔱 Sélectionnez un sous-catalogue :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        query.edit_message_text(
            text="Aucun sous-catalogue trouvé pour ce catalogue.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data='shop')]])
        )

def show_sub_catalogue(query, sub_catalogue_id):
    products = database.get_products_by_sub_catalogue(sub_catalogue_id)
    if products:
        keyboard = [[InlineKeyboardButton(f"{p[1]} (Prix: {p[2]}€, Stock: {p[3]})", callback_data=f"product_{p[0]}")] for p in products]
        keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data=f"catalogue_{query.data.split('_')[1]}")])
        query.edit_message_text(
            text="🔱 Sélectionnez un produit :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        query.edit_message_text(
            text="Aucun produit trouvé pour ce sous-catalogue.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data=f"catalogue_{query.data.split('_')[1]}")]])
        )

def process_purchase(query, product_id):
    user_id = query.from_user.id
    user = database.get_user(user_id)

    if not user:
        query.edit_message_text("🔱 Utilisateur non trouvé. 🔱")
        return

    product = database.get_product(product_id)
    if not product:
        query.edit_message_text("🔱 Produit non trouvé. 🔱")
        return

    product_id, product_name, product_price, product_stock, file_name = product

    if product_stock <= 0:
        query.edit_message_text(f"🔱 Le produit {product_name} est en rupture de stock. 🔱")
        return

    user_balance = user[2]

    if user_balance < product_price:
        query.edit_message_text("🔱 Solde insuffisant. Veuillez déposer des fonds. 🔱")
        return

    database.deduct_user_credit(user_id, product_price)
    database.update_product_stock(product_id, product_stock - 1)
    database.create_transaction(user_id, product_id, 1, product_price)

    if file_name is not None:
        file_path = f"/root/als_bot/scama_files/{file_name}"
        if os.path.exists(file_path):
            query.message.reply_document(open(file_path, 'rb'), filename=file_name)
            query.edit_message_text(f"🔱 Merci pour votre achat ! Vous avez reçu le fichier {product_name}. 🔱")
        else:
            query.edit_message_text(f"🔱 Erreur : le fichier {file_name} est introuvable. 🔱")
    else:
        query.edit_message_text(f"🔱 Aucun fichier associé au produit {product_name}. 🔱")

# Fonction pour ajouter les handlers au dispatcher
def add_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
def show_deposit_options(query):
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

# Fonction pour gérer les actions de dépôt
def handle_deposit_action(query, currency):
    query.edit_message_text(
        text=f"🔱 Vous avez sélectionné {currency}. Combien souhaitez-vous déposer ? (Minimum 10€)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')]])
    )

# Ajoutez ces fonctions pour gérer chaque type de dépôt
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'deposit_btc':
        handle_deposit_action(query, 'BTC')
    elif query.data == 'deposit_eth':
        handle_deposit_action(query, 'ETH')
    elif query.data == 'deposit_ltc':
        handle_deposit_action(query, 'LTC')
    # ... continuez avec les autres actions ...

    # Appel à la fonction 'start' si 'start' est pressé
    elif query.data == 'start':
        start(update, context)
    # Autres logiques...
