from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database

def show_profile(update, context):
    query = update.callback_query
    user = database.get_user(query.from_user.id)
    if user is None:
        text = "🔱 Aucun profil utilisateur trouvé. Veuillez effectuer un dépôt pour activer votre profil. 🔱"
    else:
        text = (f"🔱 Nom d'utilisateur: @{user[1]}\n"
                f"🔱 Votre ID: {user[0]}\n"
                f"🔱 Grade: Membre\n"
                f"🔱 Solde: {user[2]:.2f}€\n"
                f"🔱 Dépôts Total: {user[3]:.2f}$")
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔱 Accueil 🔱", callback_data='start')]]))
