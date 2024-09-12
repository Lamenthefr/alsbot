from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database
import logging

def show_scama_catalogue(update, context):
    query = update.callback_query
    print("Le bouton 'Magasin' a été cliqué.")
    scamas = database.get_products_by_type('scama')

    if scamas:
        print("Produits Scama trouvés, affichage du catalogue.")
        keyboard = [[InlineKeyboardButton(f"{s[1]} (Prix: {s[2]}€, Stock: {s[3]})", callback_data=f"buy_scama_{s[0]}")] for s in scamas]
        keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
        query.edit_message_text(
            text="🔱 Sélectionnez un scama :",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        print("Aucun produit Scama trouvé.")
        query.edit_message_text("Aucun scama disponible actuellement.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]))

def process_scama_purchase(update, context):
    query = update.callback_query
    product_id = query.data.split('_')[1]
    product = database.get_product(product_id)
    user_id = query.from_user.id
    user_credit = database.get_user_credit(user_id)

    if user_credit >= product[2]:
        # Débit des crédits
        new_credit = user_credit - product[2]
        database.update_user_balance(user_id, new_credit)

        # Mise à jour du stock
        new_stock = product[3] - 1
        database.update_product_stock(product_id, new_stock)

        # Enregistrement de la transaction
        database.record_transaction(user_id, product_id, 1, product[2])

        query.edit_message_text(f"Votre achat de {product[1]} a été effectué avec succès !")
    else:
        query.edit_message_text("Vous n'avez pas assez de crédits pour effectuer cet achat.")
