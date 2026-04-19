import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="1234",
            database="year_project"
        )
        return connection
    except Error as e:
        if e.errno == 1049: # Unknown database
            # Try connecting without database to create it
            temp_conn = mysql.connector.connect(
                host="localhost",
                port="3306",
                user="root",
                password="1234"
            )
            cursor = temp_conn.cursor()
            cursor.execute("CREATE DATABASE year_project")
            temp_conn.close()
            return get_connection()
        else:
            print(f"Error: {e}")
            return None

def init_db():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        
        # Create Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50)
            )
        """)
        
        # Create Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2),
                stock INT
            )
        """)
        
        # Create Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_date DATE,
                customer_name VARCHAR(255),
                payment_method VARCHAR(50),
                status VARCHAR(50),
                total_price DECIMAL(10, 2)
            )
        """)
        
        # Create Order Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                product_name VARCHAR(255),
                price DECIMAL(10, 2),
                amount INT,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
