import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database

# Configuration du journal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_catalogues(update, context):
    query = update.callback_query
    if query:
        logging.info("Affichage des catalogues pour l'utilisateur.")
        catalogues = database.get_catalogues()
        if catalogues:
            keyboard = [[InlineKeyboardButton(cat[1], callback_data=f"catalogue_{cat[0]}")] for cat in catalogues]
            keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
            query.edit_message_text(
                text="🔱 Sélectionnez un catalogue :",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            logging.info("Catalogues affichés avec succès.")
        else:
            query.edit_message_text("Aucun catalogue disponible.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]))
            logging.info("Aucun catalogue trouvé pour l'affichage.")
    else:
        logging.error("Erreur: CallbackQuery manquant lors de l'affichage des catalogues.")

def show_subcatalogues(update, context):
    query = update.callback_query
    catalogue_id = query.data.split('_')[1]
    logging.info(f"Affichage des sous-catalogues pour le catalogue ID: {catalogue_id}")
    subcatalogues = database.get_subcatalogues(catalogue_id)

    if subcatalogues:
        keyboard = [[InlineKeyboardButton(subcat[1], callback_data=f"subcatalogue_{subcat[0]}")] for subcat in subcatalogues]
        keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='catalogues')])
        query.edit_message_text(
            text="🔱 Sélectionnez un sous-catalogue :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logging.info("Sous-catalogues affichés avec succès.")
    else:
        query.edit_message_text("Aucun sous-catalogue disponible.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data='catalogues')]]))
        logging.info("Aucun sous-catalogue trouvé pour l'affichage.")

def show_products(update, context):
    query = update.callback_query
    subcatalogue_id = query.data.split('_')[1]
    logging.info(f"Affichage des produits pour le sous-catalogue ID: {subcatalogue_id}")
    products = database.get_products_by_subcatalogue(subcatalogue_id)

    if products:
        keyboard = [[InlineKeyboardButton(f"{prod[1]} (Prix: {prod[2]}€)", callback_data=f"product_{prod[0]}")] for prod in products]
        keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data=f"subcatalogue_{subcatalogue_id}")])
        query.edit_message_text(
            text="🔱 Sélectionnez un produit :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logging.info("Produits affichés avec succès.")
    else:
        query.edit_message_text("Aucun produit disponible.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data=f"subcatalogue_{subcatalogue_id}")]]))
        logging.info("Aucun produit trouvé pour l'affichage.")

def select_quantity(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    context.user_data['product_id'] = product_id
    logging.info(f"Sélection de la quantité pour le produit ID: {product_id}")

    keyboard = [
        [InlineKeyboardButton("+1", callback_data='quantity_1')],
        [InlineKeyboardButton("+5", callback_data='quantity_5')],
        [InlineKeyboardButton("+10", callback_data='quantity_10')],
        [InlineKeyboardButton("Confirmer", callback_data='confirm')],
        [InlineKeyboardButton("Reset", callback_data='reset')],
        [InlineKeyboardButton("Retour", callback_data=f"product_{product_id}")]
    ]

    query.edit_message_text("Sélectionnez le nombre de cartes que vous souhaitez acheter :", reply_markup=InlineKeyboardMarkup(keyboard))

def handle_quantity_selection(update, context):
    query = update.callback_query
    data = query.data.split('_')

    if data[0] == 'quantity':
        quantity = int(data[1])
        if 'selected_quantity' not in context.user_data:
            context.user_data['selected_quantity'] = 0
        context.user_data['selected_quantity'] += quantity
        query.edit_message_text(f"Quantité sélectionnée : {context.user_data['selected_quantity']}")
        logging.info(f"Quantité actuelle sélectionnée : {context.user_data['selected_quantity']}")

    elif data[0] == 'confirm':
        product_id = context.user_data['product_id']
        product = database.get_product(product_id)
        total_cost = context.user_data['selected_quantity'] * product[2]
        user_id = query.from_user.id
        user_credit = database.get_user_credit(user_id)

        if user_credit >= total_cost:
            database.update_user_balance(user_id, user_credit - total_cost)
            database.update_product_stock(product_id, product[3] - context.user_data['selected_quantity'])
            database.record_transaction(user_id, product_id, context.user_data['selected_quantity'], total_cost)
            send_cc_to_user(update, product)
            query.edit_message_text("✅ Achat réussi ! Les détails de la carte vous ont été envoyés.")
            logging.info(f"Utilisateur {user_id} a acheté {context.user_data['selected_quantity']} cartes de niveau {product[1]}")
        else:
            query.edit_message_text("Solde insuffisant. Veuillez recharger votre compte.")
            logging.warning(f"Solde insuffisant pour l'utilisateur {user_id}.")

    elif data[0] == 'reset':
        context.user_data['selected_quantity'] = 0
        query.edit_message_text("Sélection réinitialisée. Veuillez sélectionner de nouveau la quantité.")
        logging.info("Sélection de quantité réinitialisée par l'utilisateur.")

def send_cc_to_user(update, cc_info):
    logging.info(f"Envoi des détails de la carte à l'utilisateur : {update.callback_query.from_user.id}")
    update.callback_query.message.reply_text(
        f"✅ Voici les détails de votre carte :\n"
        f"Nom : {cc_info['holder_name']} {cc_info['holder_surname']}\n"
        f"Numéro : {cc_info['card_number']}\n"
        f"Date d'expiration : {cc_info['expiration_date']}\n"
        f"CVV : {cc_info['cvv']}\n"
        f"Banque : {cc_info['bank']}\n"
        f"Niveau : {cc_info['card_level']}\n"
        f"Type : {cc_info['card_type']}\n"
        f"Adresse : {cc_info['holder_address']}\n"
        f"Ville : {cc_info['city']}, {cc_info['postal_code']}\n"
        f"Téléphone : {cc_info['phone_number']}\n"
        f"IP : {cc_info['ip_address']}"
    )
