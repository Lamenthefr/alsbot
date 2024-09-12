import sqlite3
import logging

# Configuration du journal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_PATH = '/root/als_bot/central_database.db'

def connect_db():
    logging.info("Connexion à la base de données.")
    return sqlite3.connect(DATABASE_PATH)

def get_user(user_id):
    logging.info(f"Récupération des informations de l'utilisateur ID: {user_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user_if_not_exists(user_id, username):
    logging.info(f"Création d'un nouvel utilisateur si inexistant : ID {user_id}, Username {username}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, username, balance) VALUES (?, ?, ?)", (user_id, username, 0))
    conn.commit()
    conn.close()

def get_user_credit(user_id):
    logging.info(f"Récupération du crédit utilisateur pour l'ID: {user_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
    credit = cursor.fetchone()[0]
    conn.close()
    return credit

def update_user_balance(user_id, new_balance):
    logging.info(f"Mise à jour du solde utilisateur pour l'ID: {user_id}. Nouveau solde: {new_balance}€.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance=? WHERE id=?", (new_balance, user_id))
    conn.commit()
    conn.close()

def get_scam_catalogue():
    logging.info("Récupération du catalogue Scama.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM scama")
    scamas = cursor.fetchall()
    conn.close()
    return scamas

def get_scama(scama_id):
    logging.info(f"Récupération des détails du Scama ID: {scama_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scama WHERE id=?", (scama_id,))
    scama = cursor.fetchone()
    conn.close()
    return scama

def record_scama_purchase(user_id, scama_id):
    logging.info(f"Enregistrement de l'achat du Scama ID: {scama_id} par l'utilisateur ID: {user_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scama_purchases (user_id, scama_id) VALUES (?, ?)", (user_id, scama_id))
    conn.commit()
    conn.close()

# Fonctions pour les cartes bancaires (CC)
def get_catalogues():
    logging.info("Récupération des catalogues.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM catalogues")
    catalogues = cursor.fetchall()
    conn.close()
    return catalogues

def get_sub_catalogues(catalogue_id):
    logging.info(f"Récupération des sous-catalogues pour le catalogue ID: {catalogue_id}.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM sous_catalogues WHERE catalogue_id=?", (catalogue_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Erreur lors de la récupération des sous-catalogues : {e}")
        return []
    finally:
        conn.close()

def get_products_by_sub_catalogue(sub_catalogue_id):
    logging.info(f"Récupération des produits pour le sous-catalogue ID: {sub_catalogue_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products WHERE sub_catalogue_id=? AND type='cc'", (sub_catalogue_id,))
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    logging.info(f"Récupération du produit ID: {product_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product_stock(product_id, new_stock):
    logging.info(f"Mise à jour du stock du produit ID: {product_id} à {new_stock}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
    conn.commit()
    conn.close()

def create_transaction(user_id, product_id, quantity, total_price):
    logging.info(f"Enregistrement de la transaction : utilisateur ID {user_id}, produit ID {product_id}, quantité {quantity}, prix total {total_price}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)", (user_id, product_id, quantity, total_price))
    conn.commit()
    conn.close()

def deduct_user_credit(user_id, amount):
    logging.info(f"Déduction de {amount}€ du solde de l'utilisateur ID: {user_id}.")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()
