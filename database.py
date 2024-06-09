import psycopg2

class Database:
    """Manages the database connection and table interactions with PostgreSQL.

    Attributes:
        conn (psycopg2.connect): The database connection.
    """

    def __init__(self, db_name, user, password, host="localhost", port=5432):
        """Initializes the connection to the PostgreSQL database.

        Args:
            db_name (str): The name of the database to connect to.
            user (str): The username for the database connection.
            password (str): The password for the database connection.
            host (str, optional): The hostname or IP address of the PostgreSQL server. Defaults to "localhost".
            port (int, optional): The port number of the PostgreSQL server. Defaults to 5432.
        """
        self.conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)

    def create_tables(self):
        """Creates the selection and products tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS selection (
                            selection_id SERIAL PRIMARY KEY,
                            selection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            num_products INTEGER NOT NULL
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            selection_id INTEGER NOT NULL,
                            product_name TEXT NOT NULL,
                            price TEXT,
                            FOREIGN KEY (selection_id) REFERENCES selection (selection_id)
                        )''')
        self.conn.commit()

    def add_selection_data(self, num_products):
        """Inserts a new selection record into the database.

        Args:
            num_products (int): The number of products found during scraping.

        Returns:
            int: The ID of the inserted selection.
        """
        cursor = self.conn.cursor()
        insert_query = "INSERT INTO selection (num_products) VALUES (%s) RETURNING selection_id"
        cursor.execute(insert_query, (num_products,))
        last_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return last_id  # Return the ID of the inserted selection

    def add_product_data(self, selection_id, products):
        """Inserts product data into the database for the given selection.

        Args:
            selection_id (int): The ID of the selection to associate the products with.
            products (list): A list of dictionaries containing product data (name, price).
        """
        cursor = self.conn.cursor()
        for product in products:
            cursor.execute("INSERT INTO products (selection_id, product_name, price) VALUES (%s, %s, %s)",
                           (selection_id, product['name'], product['price']))
        self.conn.commit()
        cursor.close()

    def get_selections(self):
        """Retrieves all selection records from the database.

        Returns:
            list: A list of dictionaries containing selection data.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM selection")
        selections = cursor.fetchall()
        cursor.close()
        return [{'selection_id': row[0], 'selection_date': row[1], 'num_products': row[2]} for row in selections]

    def get_products_for_selection(self, selection_id):
        """Retrieves product data associated with a specific selection.

        Args:
            selection_id (int): The ID of the selection to retrieve products for.

        Returns:
            list: A list of dictionaries containing product data.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE selection_id = %s", (selection_id,))
        products = cursor.fetchall()
        cursor.close()
        return [{'selection_id': row[0], 'product_name': row[1], 'price': row[2]} for row in products]

    def close(self):
        """Closes the connection to the database."""
        self.conn.close()
