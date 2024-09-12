import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler
import os
import database
from dotenv import load_dotenv

# Configurer la journalisation
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

def add_handlers(dp):
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(manage_cc, pattern='^manage_cc$'))
    dp.add_handler(CallbackQueryHandler(request_cc_details, pattern='^add_cc$'))
    dp.add_handler(CallbackQueryHandler(check_existing_cc, pattern='^check_cc$'))


def handle_message(update: Update, context: CallbackContext):
    logger.info("Handling message")
    state = context.user_data.get('state')
    logger.info(f"Current state: {state}")

    try:
        if state == 'SEARCH_USER':
            query = update.message.text.strip()
            logger.info(f"Searching user with query: {query}")

            if query.isdigit():  # Recherche par ID
                user = database.get_user_by_id(int(query))
            else:  # Recherche par username
                user = database.get_user_by_username(query.lstrip('@'))

            if user:
                context.user_data['modify_user_id'] = user[0]
                logger.info(f"User found: {user}")
                ask_user_details(update, context)
            else:
                logger.warning(f"No user found with {'ID' if query.isdigit() else 'username'}: {query}")
                update.message.reply_text(f"Aucun utilisateur trouvé avec {'ID' if query.isdigit() else 'username'} : {query}. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Réessayer 🔱", callback_data='search_user')],
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                          ]))
            context.user_data['state'] = None

        elif state == 'SEARCH_PRODUCT':
            query = update.message.text.strip()
            logger.info(f"Searching product with query: {query}")

            if query.isdigit():  # Recherche par ID
                product = database.get_product_by_id(int(query))
            else:  # Recherche par nom
                product = database.get_product_by_name(query)

            if product:
                context.user_data['modify_product_id'] = product[0]
                logger.info(f"Product found: {product}")
                ask_product_details(update, context)
            else:
                logger.warning(f"No product found with {'ID' if query.isdigit() else 'name'}: {query}")
                update.message.reply_text(f"Aucun produit trouvé avec {'ID' if query.isdigit() else 'nom'} : {query}. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Réessayer 🔱", callback_data='search_product')],
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                          ]))
            context.user_data['state'] = None

        elif state == 'SEARCH_CATALOGUE':
            query = update.message.text.strip()
            logger.info(f"Searching catalogue with query: {query}")

            if query.isdigit():  # Recherche par ID
                catalogue = database.get_catalogue_by_id(int(query))
            else:  # Recherche par nom
                catalogue = database.get_catalogue_by_name(query)

            if catalogue:
                context.user_data['modify_catalogue_id'] = catalogue[0]
                logger.info(f"Catalogue found: {catalogue}")
                ask_catalogue_details(update, context)
            else:
                logger.warning(f"No catalogue found with {'ID' if query.isdigit() else 'name'}: {query}")
                update.message.reply_text(f"Aucun catalogue trouvé avec {'ID' if query.isdigit() else 'nom'} : {query}. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Réessayer 🔱", callback_data='search_catalogue')],
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                          ]))
            context.user_data['state'] = None

        elif state == 'SEARCH_SOUS_CATALOGUE':
            query = update.message.text.strip()
            logger.info(f"Searching sous-catalogue with query: {query}")

            if query.isdigit():  # Recherche par ID
                sous_catalogue = database.get_sous_catalogue_by_id(int(query))
            else:  # Recherche par nom
                sous_catalogue = database.get_sous_catalogue_by_name(query)

            if sous_catalogue:
                context.user_data['modify_sous_catalogue_id'] = sous_catalogue[0]
                logger.info(f"Sous-catalogue found: {sous_catalogue}")
                ask_sous_catalogue_details(update, context)
            else:
                logger.warning(f"No sous-catalogue found with {'ID' if query.isdigit() else 'name'}: {query}")
                update.message.reply_text(f"Aucun sous-catalogue trouvé avec {'ID' if query.isdigit() else 'nom'} : {query}. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Réessayer 🔱", callback_data='search_sous_catalogue')],
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                          ]))
            context.user_data['state'] = None

        elif state == 'ADD_PRODUCT_NAME':
            context.user_data['new_product_name'] = update.message.text.strip()
            logger.info(f"Adding new product with name: {context.user_data['new_product_name']}")
            update.message.reply_text("🔱 Entrez le prix du produit :")
            context.user_data['state'] = 'ADD_PRODUCT_PRICE'

        elif state == 'ADD_PRODUCT_PRICE':
            try:
                price = float(update.message.text.strip())
                context.user_data['new_product_price'] = price
                logger.info(f"Setting product price: {price}")
                update.message.reply_text("🔱 Entrez le stock du produit :")
                context.user_data['state'] = 'ADD_PRODUCT_STOCK'
            except ValueError:
                logger.error("Invalid price entered")
                update.message.reply_text("🔱 Le prix doit être un nombre. Veuillez réessayer.")

        elif state == 'ADD_PRODUCT_STOCK':
            try:
                stock = int(update.message.text.strip())
                context.user_data['new_product_stock'] = stock
                logger.info(f"Setting product stock: {stock}")
                update.message.reply_text("🔱 Entrez la catégorie du produit :")
                context.user_data['state'] = 'ADD_PRODUCT_CATEGORY'
            except ValueError:
                logger.error("Invalid stock entered")
                update.message.reply_text("🔱 Le stock doit être un nombre entier. Veuillez réessayer.")

        elif state == 'ADD_PRODUCT_CATEGORY':
            category = update.message.text.strip()
            context.user_data['new_product_category'] = category
            logger.info(f"Setting product category: {category}")
            update.message.reply_text("🔱 Entrez l'ID du sous-catalogue associé :")
            context.user_data['state'] = 'ADD_PRODUCT_SOUS_CATALOGUE_ID'

        elif state == 'ADD_PRODUCT_SOUS_CATALOGUE_ID':
            try:
                sous_catalogue_id = int(update.message.text.strip())
                context.user_data['new_product_sous_catalogue_id'] = sous_catalogue_id
                logger.info(f"Setting product sous-catalogue ID: {sous_catalogue_id}")
                update.message.reply_text("🔱 Entrez le nom du fichier ZIP associé (facultatif) :")
                context.user_data['state'] = 'ADD_PRODUCT_ZIP_FILE_NAME'
            except ValueError:
                logger.error("Invalid sous-catalogue ID entered")
                update.message.reply_text("🔱 L'ID du sous-catalogue doit être un nombre entier. Veuillez réessayer.")

        elif state == 'ADD_PRODUCT_ZIP_FILE_NAME':
            zip_file_name = update.message.text.strip()
            if zip_file_name == '':
                zip_file_name = None
            context.user_data['new_product_zip_file_name'] = zip_file_name
            logger.info(f"Setting product ZIP file name: {zip_file_name}")

            # Ajout du produit à la base de données
            database.add_product(
                name=context.user_data['new_product_name'],
                price=context.user_data['new_product_price'],
                stock=context.user_data['new_product_stock'],
                category=context.user_data['new_product_category'],
                sous_catalogue_id=context.user_data['new_product_sous_catalogue_id'],
                zip_file_name=context.user_data['new_product_zip_file_name']
            )

            logger.info("Product added successfully")
            update.message.reply_text("🔱 Le produit a été ajouté avec succès.")
            context.user_data['state'] = None

        elif state == 'ADD_CATALOGUE_NAME':
            name = update.message.text.strip()
            logger.info(f"Adding new catalogue with name: {name}")
            database.add_catalogue(name)
            update.message.reply_text(f"🔱 Le catalogue '{name}' a été ajouté avec succès.")
            context.user_data['state'] = None

        elif state == 'ADD_SOUS_CATALOGUE_NAME':
            name = update.message.text.strip()
            catalogue_id = context.user_data.get('catalogue_id')
            logger.info(f"Adding new sous-catalogue with name: {name}, catalogue ID: {catalogue_id}")
            database.add_sous_catalogue(name, catalogue_id)
            update.message.reply_text(f"🔱 Le sous-catalogue '{name}' a été ajouté avec succès.")
            context.user_data['state'] = None

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        update.message.reply_text("Une erreur est survenue. Veuillez réessayer.")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()

    try:
        logger.info(f"Button pressed: {query.data}")

        if query.data == 'manage_products':
            manage_products(update, context)
        elif query.data == 'manage_catalogues':
            manage_catalogues(update, context)
        elif query.data == 'manage_sous_catalogues':
            manage_sous_catalogues(update, context)
        elif query.data == 'manage_users':
            manage_users(update, context)
        elif query.data == 'search_user':
            search_user(update, context)
        elif query.data == 'search_product':
            search_product(update, context)
        elif query.data == 'search_catalogue':
            search_catalogue(update, context)
        elif query.data == 'search_sous_catalogue':
            search_sous_catalogue(update, context)
        elif query.data == 'list_all_users':
            list_all_users(update, context)
        elif query.data == 'list_all_products':
            list_all_products(update, context)
        elif query.data == 'list_all_catalogues':
            list_all_catalogues(update, context)
        elif query.data == 'list_all_sous_catalogues':
            list_all_sous_catalogues(update, context)
        elif query.data == 'add_product':
            add_product(update, context)
        elif query.data == 'add_catalogue':
            add_catalogue(update, context)
        elif query.data == 'add_sous_catalogue':
            add_sous_catalogue(update, context)
        elif query.data.startswith('modify_user'):
            ask_user_details(update, context)
        elif query.data.startswith('modify_product'):
            ask_product_details(update, context)
        elif query.data.startswith('modify_catalogue'):
            ask_catalogue_details(update, context)
        elif query.data.startswith('modify_sous_catalogue'):
            ask_sous_catalogue_details(update, context)
        elif query.data == 'start':
            start(update, context)

    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        query.message.reply_text("Une erreur est survenue. Veuillez réessayer.")

def start(update, context):
    try:
        logger.info("Starting bot")
        if update.message:
            update.message.reply_text(
                "🔱 Bienvenue dans le bot Admin 🔱\n"
                "Choisissez une option :",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔱 Gestion des Produits 🔱", callback_data='manage_products')],
                    [InlineKeyboardButton("🔱 Gestion des Catalogues 🔱", callback_data='manage_catalogues')],
                    [InlineKeyboardButton("🔱 Gestion des Sous-Catalogues 🔱", callback_data='manage_sous_catalogues')],
                    [InlineKeyboardButton("🔱 Gestion des Utilisateurs 🔱", callback_data='manage_users')],
                    [InlineKeyboardButton("🔱 Gestion des Cartes Bancaires 🔱", callback_data='manage_cc')],
                ])
            )
        elif update.callback_query:
            update.callback_query.message.reply_text(
                "🔱 Bienvenue dans le bot Admin 🔱\n"
                "Choisissez une option :",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔱 Gestion des Produits 🔱", callback_data='manage_products')],
                    [InlineKeyboardButton("🔱 Gestion des Catalogues 🔱", callback_data='manage_catalogues')],
                    [InlineKeyboardButton("🔱 Gestion des Sous-Catalogues 🔱", callback_data='manage_sous_catalogues')],
                    [InlineKeyboardButton("🔱 Gestion des Utilisateurs 🔱", callback_data='manage_users')],
                    [InlineKeyboardButton("🔱 Gestion des Cartes Bancaires 🔱", callback_data='manage_cc')],
                ])
            )
    except Exception as e:
        logger.error(f"Error in start function: {e}")
        update.message.reply_text("Une erreur est survenue lors du démarrage. Veuillez réessayer.")

def manage_products(update, context):
    try:
        logger.info("Managing products")
        products = database.get_recent_products(limit=5)
        logger.info(f"Products retrieved: {products}")
        if products:
            product_list = "\n".join([f"🔱 ID: {product[0]} | Nom: {product[1]} | Prix: {product[2]:.2f}€ | Stock: {product[3]}" for product in products])
            text = f"🔱 Liste des produits récents 🔱\n\n{product_list}\n\nSélectionnez un produit pour gérer ou recherchez par nom :"
            keyboard = [[InlineKeyboardButton(f"Modifier {product[1]} (ID: {product[0]})", callback_data=f'modify_product_{product[0]}')] for product in products]
            keyboard.append([InlineKeyboardButton("🔱 Rechercher par nom 🔱", callback_data='search_product')])
            keyboard.append([InlineKeyboardButton("🔱 Liste complète 🔱", callback_data='list_all_products')])
            keyboard.append([InlineKeyboardButton("🔱 Ajouter un produit 🔱", callback_data='add_product')])
            keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
        else:
            text = "🔱 Aucun produit trouvé."
            keyboard = [[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_products: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion des produits. Veuillez réessayer.")

def manage_catalogues(update, context):
    try:
        logger.info("Managing catalogues")
        catalogues = database.get_recent_catalogues(limit=5)
        logger.info(f"Catalogues retrieved: {catalogues}")
        if catalogues:
            catalogue_list = "\n".join([f"🔱 ID: {catalogue[0]} | Nom: {catalogue[1]}" for catalogue in catalogues])
            text = f"🔱 Liste des catalogues récents 🔱\n\n{catalogue_list}\n\nSélectionnez un catalogue pour gérer ou recherchez par nom :"
            keyboard = [[InlineKeyboardButton(f"Modifier {catalogue[1]} (ID: {catalogue[0]})", callback_data=f'modify_catalogue_{catalogue[0]}')] for catalogue in catalogues]
            keyboard.append([InlineKeyboardButton("🔱 Rechercher par nom 🔱", callback_data='search_catalogue')])
            keyboard.append([InlineKeyboardButton("🔱 Liste complète 🔱", callback_data='list_all_catalogues')])
            keyboard.append([InlineKeyboardButton("🔱 Ajouter un catalogue 🔱", callback_data='add_catalogue')])
            keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
        else:
            text = "🔱 Aucun catalogue trouvé."
            keyboard = [[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_catalogues: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion des catalogues. Veuillez réessayer.")

def manage_sous_catalogues(update, context):
    try:
        logger.info("Managing sous-catalogues")
        sous_catalogues = database.get_recent_sous_catalogues(limit=5)
        logger.info(f"Sous-catalogues retrieved: {sous_catalogues}")
        if sous_catalogues:
            sous_catalogue_list = "\n".join([f"🔱 ID: {sous_catalogue[0]} | Nom: {sous_catalogue[1]}" for sous_catalogue in sous_catalogues])
            text = f"🔱 Liste des sous-catalogues récents 🔱\n\n{sous_catalogue_list}\n\nSélectionnez un sous-catalogue pour gérer ou recherchez par nom :"
            keyboard = [[InlineKeyboardButton(f"Modifier {sous_catalogue[1]} (ID: {sous_catalogue[0]})", callback_data=f'modify_sous_catalogue_{sous_catalogue[0]}')] for sous_catalogue in sous_catalogues]
            keyboard.append([InlineKeyboardButton("🔱 Rechercher par nom 🔱", callback_data='search_sous_catalogue')])
            keyboard.append([InlineKeyboardButton("🔱 Liste complète 🔱", callback_data='list_all_sous_catalogues')])
            keyboard.append([InlineKeyboardButton("🔱 Ajouter un sous-catalogue 🔱", callback_data='add_sous_catalogue')])
            keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
        else:
            text = "🔱 Aucun sous-catalogue trouvé."
            keyboard = [[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_sous_catalogues: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion des sous-catalogues. Veuillez réessayer.")

def manage_users(update, context):
    try:
        logger.info("Managing users")
        users = database.get_recent_users(limit=5)
        logger.info(f"Users retrieved: {users}")
        if users:
            user_list = "\n".join([f"🔱 ID: {user[0]} | Username: @{user[1]} | Solde: {user[2]:.2f}€ | Dépôts Total: {user[3]:.2f}€" for user in users])
            text = f"🔱 Liste des utilisateurs récents 🔱\n\n{user_list}\n\nSélectionnez un utilisateur pour gérer ou recherchez par @username :"
            keyboard = [[InlineKeyboardButton(f"Modifier {user[1]} (ID: {user[0]})", callback_data=f'modify_user_{user[0]}')] for user in users]
            keyboard.append([InlineKeyboardButton("🔱 Rechercher par @username 🔱", callback_data='search_user')])
            keyboard.append([InlineKeyboardButton("🔱 Liste complète 🔱", callback_data='list_all_users')])
            keyboard.append([InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')])
        else:
            text = "🔱 Aucun utilisateur trouvé."
            keyboard = [[InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error in manage_users: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion des utilisateurs. Veuillez réessayer.")

def search_user(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez l'@username de l'utilisateur :",
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                                ]))
        context.user_data['state'] = 'SEARCH_USER'
    except Exception as e:
        logger.error(f"Error in search_user: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la recherche d'utilisateur. Veuillez réessayer.")

def search_product(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du produit :",
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                                ]))
        context.user_data['state'] = 'SEARCH_PRODUCT'
    except Exception as e:
        logger.error(f"Error in search_product: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la recherche de produit. Veuillez réessayer.")

def search_catalogue(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du catalogue :",
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                                ]))
        context.user_data['state'] = 'SEARCH_CATALOGUE'
    except Exception as e:
        logger.error(f"Error in search_catalogue: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la recherche de catalogue. Veuillez réessayer.")

def search_sous_catalogue(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du sous-catalogue :",
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                                ]))
        context.user_data['state'] = 'SEARCH_SOUS_CATALOGUE'
    except Exception as e:
        logger.error(f"Error in search_sous_catalogue: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la recherche de sous-catalogue. Veuillez réessayer.")

def list_all_users(update, context):
    try:
        users = database.get_all_users()
        logger.info(f"All users retrieved: {users}")
        if users:
            user_list = "\n".join([f"🔱 ID: {user[0]} | Username: @{user[1]} | Solde: {user[2]:.2f}€ | Dépôts Total: {user[3]:.2f}€" for user in users])
            update.callback_query.edit_message_text(text=f"🔱 Liste complète des utilisateurs 🔱\n\n{user_list}",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                                    ]))
        else:
            update.callback_query.edit_message_text(text="🔱 Aucun utilisateur trouvé.",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                                    ]))
    except Exception as e:
        logger.error(f"Error in list_all_users: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'affichage de la liste des utilisateurs. Veuillez réessayer.")

def list_all_products(update, context):
    try:
        products = database.get_all_products()
        logger.info(f"All products retrieved: {products}")
        if products:
            product_list = "\n".join([f"🔱 ID: {product[0]} | Nom: {product[1]} | Prix: {product[2]:.2f}€ | Stock: {product[3]}" for product in products])
            update.callback_query.edit_message_text(text=f"🔱 Liste complète des produits 🔱\n\n{product_list}",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                                    ]))
        else:
            update.callback_query.edit_message_text(text="🔱 Aucun produit trouvé.",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                                    ]))
    except Exception as e:
        logger.error(f"Error in list_all_products: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'affichage de la liste des produits. Veuillez réessayer.")

def list_all_catalogues(update, context):
    try:
        catalogues = database.get_all_catalogues()
        logger.info(f"All catalogues retrieved: {catalogues}")
        if catalogues:
            catalogue_list = "\n".join([f"🔱 ID: {catalogue[0]} | Nom: {catalogue[1]}" for catalogue in catalogues])
            update.callback_query.edit_message_text(text=f"🔱 Liste complète des catalogues 🔱\n\n{catalogue_list}",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                                    ]))
        else:
            update.callback_query.edit_message_text(text="🔱 Aucun catalogue trouvé.",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                                    ]))
    except Exception as e:
        logger.error(f"Error in list_all_catalogues: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'affichage de la liste des catalogues. Veuillez réessayer.")

def list_all_sous_catalogues(update, context):
    try:
        sous_catalogues = database.get_all_sous_catalogues()
        logger.info(f"All sous-catalogues retrieved: {sous_catalogues}")
        if sous_catalogues:
            sous_catalogue_list = "\n".join([f"🔱 ID: {sous_catalogue[0]} | Nom: {sous_catalogue[1]}" for sous_catalogue in sous_catalogues])
            update.callback_query.edit_message_text(text=f"🔱 Liste complète des sous-catalogues 🔱\n\n{sous_catalogue_list}",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                                    ]))
        else:
            update.callback_query.edit_message_text(text="🔱 Aucun sous-catalogue trouvé.",
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                                    ]))
    except Exception as e:
        logger.error(f"Error in list_all_sous_catalogues: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'affichage de la liste des sous-catalogues. Veuillez réessayer.")

def ask_user_details(update, context):
    try:
        if update.callback_query:
            user_id = context.user_data.get('modify_user_id')
            if not user_id:
                update.callback_query.message.reply_text("Aucune information d'utilisateur disponible. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                          ]))
                return

            text = f"Que voulez-vous faire avec l'utilisateur {user_id} ?\n\n" \
                   "Options:\n" \
                   "1. Modifier le solde (envoyez 'balance')\n" \
                   "2. Voir l'historique d'achat (envoyez 'history')\n" \
                   "3. Supprimer l'utilisateur (envoyez 'delete')"

            update.callback_query.edit_message_text(text=text,
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                                    ]))
            context.user_data['state'] = 'MODIFY_USER'
        else:
            update.message.reply_text("Une erreur est survenue. Veuillez réessayer.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_users')]
                                      ]))
    except Exception as e:
        logger.error(f"Error in ask_user_details: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion de l'utilisateur. Veuillez réessayer.")

def ask_product_details(update, context):
    try:
        if update.callback_query:
            product_id = context.user_data.get('modify_product_id')
            if not product_id:
                update.callback_query.message.reply_text("Aucune information de produit disponible. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                          ]))
                return

            text = f"Que voulez-vous faire avec le produit {product_id} ?\n\n" \
                   "Options:\n" \
                   "1. Modifier le prix (envoyez 'price')\n" \
                   "2. Modifier le stock (envoyez 'stock')\n" \
                   "3. Supprimer le produit (envoyez 'delete')"

            update.callback_query.edit_message_text(text=text,
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                                    ]))
            context.user_data['state'] = 'MODIFY_PRODUCT'
        else:
            update.message.reply_text("Une erreur est survenue. Veuillez réessayer.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_products')]
                                      ]))
    except Exception as e:
        logger.error(f"Error in ask_product_details: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion du produit. Veuillez réessayer.")

def ask_catalogue_details(update, context):
    try:
        if update.callback_query:
            catalogue_id = context.user_data.get('modify_catalogue_id')
            if not catalogue_id:
                update.callback_query.message.reply_text("Aucune information de catalogue disponible. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                          ]))
                return

            text = f"Que voulez-vous faire avec le catalogue {catalogue_id} ?\n\n" \
                   "Options:\n" \
                   "1. Modifier le nom (envoyez 'name')\n" \
                   "2. Supprimer le catalogue (envoyez 'delete')"

            update.callback_query.edit_message_text(text=text,
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                                    ]))
            context.user_data['state'] = 'MODIFY_CATALOGUE'
        else:
            update.message.reply_text("Une erreur est survenue. Veuillez réessayer.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_catalogues')]
                                      ]))
    except Exception as e:
        logger.error(f"Error in ask_catalogue_details: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion du catalogue. Veuillez réessayer.")

def ask_sous_catalogue_details(update, context):
    try:
        if update.callback_query:
            sous_catalogue_id = context.user_data.get('modify_sous_catalogue_id')
            if not sous_catalogue_id:
                update.callback_query.message.reply_text("Aucune information de sous-catalogue disponible. Veuillez réessayer.",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                          ]))
                return

            text = f"Que voulez-vous faire avec le sous-catalogue {sous_catalogue_id} ?\n\n" \
                   "Options:\n" \
                   "1. Modifier le nom (envoyez 'name')\n" \
                   "2. Supprimer le sous-catalogue (envoyez 'delete')"

            update.callback_query.edit_message_text(text=text,
                                                    reply_markup=InlineKeyboardMarkup([
                                                        [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                                    ]))
            context.user_data['state'] = 'MODIFY_SOUS_CATALOGUE'
        else:
            update.message.reply_text("Une erreur est survenue. Veuillez réessayer.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("🔱 Retour 🔱", callback_data='manage_sous_catalogues')]
                                      ]))
    except Exception as e:
        logger.error(f"Error in ask_sous_catalogue_details: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion du sous-catalogue. Veuillez réessayer.")

def add_product(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du nouveau produit :")
        context.user_data['state'] = 'ADD_PRODUCT_NAME'
    except Exception as e:
        logger.error(f"Error in add_product: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'ajout du produit. Veuillez réessayer.")

def add_catalogue(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du nouveau catalogue :")
        context.user_data['state'] = 'ADD_CATALOGUE_NAME'
    except Exception as e:
        logger.error(f"Error in add_catalogue: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'ajout du catalogue. Veuillez réessayer.")

def add_sous_catalogue(update, context):
    try:
        update.callback_query.edit_message_text(text="🔱 Entrez le nom du nouveau sous-catalogue :")
        context.user_data['state'] = 'ADD_SOUS_CATALOGUE_NAME'
    except Exception as e:
        logger.error(f"Error in add_sous_catalogue: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de l'ajout du sous-catalogue. Veuillez réessayer.")
def manage_cc(update, context):
    try:
        logger.info("Managing credit cards")
        update.callback_query.message.reply_text(
            "🔱 Gestion des Cartes Bancaires 🔱\n"
            "Choisissez une option :",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Ajouter des CC", callback_data='add_cc')],
                [InlineKeyboardButton("Vérifier les CC existantes", callback_data='check_cc')],
                [InlineKeyboardButton("🔱 Retour 🔱", callback_data='start')],
            ])
        )
    except Exception as e:
        logger.error(f"Error in manage_cc: {e}")
        update.callback_query.message.reply_text("Une erreur est survenue lors de la gestion des cartes bancaires. Veuillez réessayer.")

def request_cc_details(update, context):
    update.callback_query.message.reply_text(
        "Veuillez envoyer les détails des CC dans le format suivant :\n"
        "[🔱] Num carte : 5130290856011274\n"
        "[🔱] Date expiration : 07 / 24\n"
        "... (et ainsi de suite)"
    )
    context.user_data['state'] = 'awaiting_cc_details'

def handle_cc_details(update, context):
    if context.user_data.get('state') == 'awaiting_cc_details':
        cc_details = update.message.text
        cc_info = parse_cc_message(cc_details)

        if is_duplicate_cc(cc_info):
            update.message.reply_text("Cette carte existe déjà dans la base de données.")
        else:
            add_cc_to_database(cc_info)
            update.message.reply_text("CC ajoutée avec succès.")
            context.user_data['state'] = None

def check_existing_cc(update, context):
    conn = sqlite3.connect('/root/als_bot/central_database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products WHERE type='cc'")
    total_cc = cursor.fetchone()[0]
    conn.close()
    
    update.callback_query.message.reply_text(f"Il y a actuellement {total_cc} CC dans la base de données.")

def is_duplicate_cc(cc_info):
    conn = sqlite3.connect('/root/als_bot/central_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE card_number=? AND expiration_date=?", (cc_info['card_number'], cc_info['expiration_date']))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def add_cc_to_database(cc_info):
    conn = sqlite3.connect('/root/als_bot/central_database.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (name, price, stock, type, bank, card_number, expiration_date, cvv, card_level, card_type, holder_name, holder_surname, holder_address, city, postal_code, phone_number, ip_address)
    VALUES (?, ?, ?, 'cc', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        f"{cc_info['name']} {cc_info['surname']}",
        0,
        1,
        cc_info['bank'],
        cc_info['card_number'],
        cc_info['expiration_date'],
        cc_info['cvv'],
        cc_info['card_level'],
        cc_info['card_type'],
        cc_info['name'],
        cc_info['surname'],
        cc_info['address'],
        cc_info['city'],
        cc_info['postal_code'],
        cc_info['phone_number'],
        cc_info['ip_address']
    ))

    conn.commit()
    conn.close()
    return cursor.lastrowid
