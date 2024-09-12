import sqlite3
import logging

# Configurer la journalisation
logger = logging.getLogger(__name__)

db_path = '/root/als_bot/central_database.db'

def init_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Création des tables si elles n'existent pas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL,
            total_deposits REAL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            stock INTEGER,
            category TEXT,
            sous_catalogue_id INTEGER,
            zip_file_name TEXT,
            zip_file_id INTEGER,
            FOREIGN KEY (sous_catalogue_id) REFERENCES sous_catalogues(id),
            FOREIGN KEY (zip_file_id) REFERENCES zip_files(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalogues (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sous_catalogues (
            id INTEGER PRIMARY KEY,
            name TEXT,
            catalogue_id INTEGER,
            FOREIGN KEY (catalogue_id) REFERENCES catalogues(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS zip_files (
            id INTEGER PRIMARY KEY,
            file_name TEXT
        )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def get_user_by_id(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, balance, total_deposits FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        logger.info(f"User retrieved by ID {user_id}: {user}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by ID {user_id}: {e}")
        return None

def get_product_by_id(product_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        logger.info(f"Product retrieved by ID {product_id}: {product}")
        return product
    except Exception as e:
        logger.error(f"Error retrieving product by ID {product_id}: {e}")
        return None

def get_catalogue_by_id(catalogue_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM catalogues WHERE id = ?", (catalogue_id,))
        catalogue = cursor.fetchone()
        conn.close()
        logger.info(f"Catalogue retrieved by ID {catalogue_id}: {catalogue}")
        return catalogue
    except Exception as e:
        logger.error(f"Error retrieving catalogue by ID {catalogue_id}: {e}")
        return None

def get_sous_catalogue_by_id(sous_catalogue_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM sous_catalogues WHERE id = ?", (sous_catalogue_id,))
        sous_catalogue = cursor.fetchone()
        conn.close()
        logger.info(f"Sous-catalogue retrieved by ID {sous_catalogue_id}: {sous_catalogue}")
        return sous_catalogue
    except Exception as e:
        logger.error(f"Error retrieving sous-catalogue by ID {sous_catalogue_id}: {e}")
        return None

def get_user_by_username(username):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, balance, total_deposits FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        logger.info(f"User retrieved by username {username}: {user}")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user by username {username}: {e}")
        return None

def get_product_by_name(name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products WHERE name = ?", (name,))
        product = cursor.fetchone()
        conn.close()
        logger.info(f"Product retrieved by name {name}: {product}")
        return product
    except Exception as e:
        logger.error(f"Error retrieving product by name {name}: {e}")
        return None

def get_catalogue_by_name(name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM catalogues WHERE name = ?", (name,))
        catalogue = cursor.fetchone()
        conn.close()
        logger.info(f"Catalogue retrieved by name {name}: {catalogue}")
        return catalogue
    except Exception as e:
        logger.error(f"Error retrieving catalogue by name {name}: {e}")
        return None

def get_sous_catalogue_by_name(name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM sous_catalogues WHERE name = ?", (name,))
        sous_catalogue = cursor.fetchone()
        conn.close()
        logger.info(f"Sous-catalogue retrieved by name {name}: {sous_catalogue}")
        return sous_catalogue
    except Exception as e:
        logger.error(f"Error retrieving sous-catalogue by name {name}: {e}")
        return None

def get_all_users():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, balance, total_deposits FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        conn.close()
        logger.info(f"All users retrieved: {users}")
        return users
    except Exception as e:
        logger.error(f"Error retrieving all users: {e}")
        return []

def get_all_products():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products ORDER BY id DESC")
        products = cursor.fetchall()
        conn.close()
        logger.info(f"All products retrieved: {products}")
        return products
    except Exception as e:
        logger.error(f"Error retrieving all products: {e}")
        return []

def get_all_catalogues():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM catalogues ORDER BY id DESC")
        catalogues = cursor.fetchall()
        conn.close()
        logger.info(f"All catalogues retrieved: {catalogues}")
        return catalogues
    except Exception as e:
        logger.error(f"Error retrieving all catalogues: {e}")
        return []

def get_all_sous_catalogues():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM sous_catalogues ORDER BY id DESC")
        sous_catalogues = cursor.fetchall()
        conn.close()
        logger.info(f"All sous-catalogues retrieved: {sous_catalogues}")
        return sous_catalogues
    except Exception as e:
        logger.error(f"Error retrieving all sous-catalogues: {e}")
        return []

def get_recent_users(limit=5):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, balance, total_deposits FROM users ORDER BY id DESC LIMIT ?", (limit,))
        users = cursor.fetchall()
        conn.close()
        logger.info(f"Recent users retrieved: {users}")
        return users
    except Exception as e:
        logger.error(f"Error retrieving recent users: {e}")
        return []

def get_recent_products(limit=5):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, stock FROM products ORDER BY id DESC LIMIT ?", (limit,))
        products = cursor.fetchall()
        conn.close()
        logger.info(f"Recent products retrieved: {products}")
        return products
    except Exception as e:
        logger.error(f"Error retrieving recent products: {e}")
        return []

def get_recent_catalogues(limit=5):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM catalogues ORDER BY id DESC LIMIT ?", (limit,))
        catalogues = cursor.fetchall()
        conn.close()
        logger.info(f"Recent catalogues retrieved: {catalogues}")
        return catalogues
    except Exception as e:
        logger.error(f"Error retrieving recent catalogues: {e}")
        return []

def get_recent_sous_catalogues(limit=5):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM sous_catalogues ORDER BY id DESC LIMIT ?", (limit,))
        sous_catalogues = cursor.fetchall()
        conn.close()
        logger.info(f"Recent sous-catalogues retrieved: {sous_catalogues}")
        return sous_catalogues
    except Exception as e:
        logger.error(f"Error retrieving recent sous-catalogues: {e}")
        return []

def delete_user(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"User deleted with ID: {user_id}")
    except Exception as e:
        logger.error(f"Error deleting user with ID {user_id}: {e}")

def update_user_balance(user_id, new_balance):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()
        logger.info(f"User balance updated for ID {user_id}: {new_balance}")
    except Exception as e:
        logger.error(f"Error updating user balance for ID {user_id}: {e}")

def update_catalogue_name(catalogue_id, new_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE catalogues SET name = ? WHERE id = ?", (new_name, catalogue_id))
        conn.commit()
        conn.close()
        logger.info(f"Catalogue name updated for ID {catalogue_id}: {new_name}")
    except Exception as e:
        logger.error(f"Error updating catalogue name for ID {catalogue_id}: {e}")

def update_sous_catalogue_name(sous_catalogue_id, new_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE sous_catalogues SET name = ? WHERE id = ?", (new_name, sous_catalogue_id))
        conn.commit()
        conn.close()
        logger.info(f"Sous-catalogue name updated for ID {sous_catalogue_id}: {new_name}")
    except Exception as e:
        logger.error(f"Error updating sous-catalogue name for ID {sous_catalogue_id}: {e}")

def delete_catalogue(catalogue_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM catalogues WHERE id = ?", (catalogue_id,))
        conn.commit()
        conn.close()
        logger.info(f"Catalogue deleted with ID: {catalogue_id}")
    except Exception as e:
        logger.error(f"Error deleting catalogue with ID {catalogue_id}: {e}")

def delete_sous_catalogue(sous_catalogue_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sous_catalogues WHERE id = ?", (sous_catalogue_id,))
        conn.commit()
        conn.close()
        logger.info(f"Sous-catalogue deleted with ID: {sous_catalogue_id}")
    except Exception as e:
        logger.error(f"Error deleting sous-catalogue with ID {sous_catalogue_id}: {e}")

def add_product(name, price, stock, category, sous_catalogue_id, zip_file_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO products (name, price, stock, category, sous_catalogue_id, zip_file_name) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, price, stock, category, sous_catalogue_id, zip_file_name))

        conn.commit()
        conn.close()
        logger.info(f"Product added: {name}, Price: {price}, Stock: {stock}, Category: {category}, Sous-catalogue ID: {sous_catalogue_id}, ZIP file name: {zip_file_name}")
    except Exception as e:
        logger.error(f"Error adding product {name}: {e}")

def add_catalogue(name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO catalogues (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        logger.info(f"Catalogue added: {name}")
    except Exception as e:
        logger.error(f"Error adding catalogue {name}: {e}")

def add_sous_catalogue(name, catalogue_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sous_catalogues (name, catalogue_id) VALUES (?, ?)", (name, catalogue_id))
        conn.commit()
        conn.close()
        logger.info(f"Sous-catalogue added: {name}, Catalogue ID: {catalogue_id}")
    except Exception as e:
        logger.error(f"Error adding sous_catalogue {name}: {e}")
