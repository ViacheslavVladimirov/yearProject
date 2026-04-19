import socket
import json
import sys
import os
from decimal import Decimal
from datetime import date

# Add root directory to sys.path to import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.product import Product
from models.customer import Customer
from models.order import Order
try:
    from db import get_connection, init_db
except ImportError:
    from server.db import get_connection, init_db

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def recv_all(sock):
    data = b''
    while True:
        part = sock.recv(4096)
        if not part:
            break
        data += part
    return data.decode('utf-8')

def handle_client(client_socket):
    try:
        data = recv_all(client_socket)
        if not data:
            return

        print(f"Received command")
        parts = data.split(' ', 1)
        if not parts:
            return
            
        command = parts[0]
        response = "ERROR Invalid command"

        if command == "LIST":
            if len(parts) < 2:
                response = "ERROR Missing entity for LIST"
            else:
                entity = parts[1]
                conn = get_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    if entity == "PRODUCTS":
                        cursor.execute("SELECT * FROM products")
                        results = cursor.fetchall()
                        response = f"OK {json.dumps(results, cls=EnhancedJSONEncoder)}"
                    elif entity == "CUSTOMERS":
                        cursor.execute("SELECT * FROM customers")
                        results = cursor.fetchall()
                        response = f"OK {json.dumps(results, cls=EnhancedJSONEncoder)}"
                    elif entity == "ORDERS":
                        cursor.execute("SELECT * FROM orders")
                        results = cursor.fetchall()
                        for order in results:
                            cursor.execute("SELECT product_name, price, amount FROM order_items WHERE order_id = %s", (order['id'],))
                            order['items'] = cursor.fetchall()
                        response = f"OK {json.dumps(results, cls=EnhancedJSONEncoder)}"
                    conn.close()
                else:
                    response = "ERROR DB connection failed"

        elif command == "CREATE":
            create_parts = parts[1].split(' ', 1)
            if len(create_parts) < 2:
                response = "ERROR Missing data for CREATE"
            else:
                entity = create_parts[0]
                data_str = create_parts[1]
                payload = json.loads(data_str)
                
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    if entity == "PRODUCT":
                        cursor.execute(
                            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                            (payload['name'], payload['price'], payload['stock'])
                        )
                    elif entity == "CUSTOMER":
                        cursor.execute(
                            "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)",
                            (payload['name'], payload['email'], payload['phone'])
                        )
                    elif entity == "ORDER":
                        cursor.execute(
                            "INSERT INTO orders (order_date, customer_name, payment_method, status, total_price) VALUES (%s, %s, %s, %s, %s)",
                            (payload['date'], payload['customer'], payload['payment'], payload['status'], payload['total'])
                        )
                        order_id = cursor.lastrowid
                        for item in payload.get('items', []):
                            cursor.execute(
                                "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                                (order_id, item['product_name'], item['price'], item['amount'])
                            )
                    
                    conn.commit()
                    conn.close()
                    response = "OK Created"
                else:
                    response = "ERROR DB connection failed"

        elif command == "GET":
            get_parts = parts[1].split(' ', 1)
            entity = get_parts[0]
            conn = get_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                if entity == "STATS":
                    cursor.execute("SELECT amount, price FROM order_items")
                    items = cursor.fetchall()
                    total_products = 0
                    total_revenue = 0.0
                    for item in items:
                        amount = int(item.get('amount', 0))
                        price = float(item.get('price', 0))
                        total_products += amount
                        total_revenue += amount * price
                    response = f"OK {json.dumps({'total_products': total_products, 'total_revenue': total_revenue}, cls=EnhancedJSONEncoder)}"
                else:
                    if len(get_parts) < 2:
                        response = "ERROR Missing ID for GET"
                    else:
                        entity_id = get_parts[1]
                        if entity == "PRODUCT":
                            cursor.execute("SELECT * FROM products WHERE id=%s", (entity_id,))
                        elif entity == "CUSTOMER":
                            cursor.execute("SELECT * FROM customers WHERE id=%s", (entity_id,))
                        elif entity == "ORDER":
                            cursor.execute("SELECT * FROM orders WHERE id=%s", (entity_id,))
                        
                        result = cursor.fetchone()
                        if result:
                            if entity == "ORDER":
                                cursor.execute("SELECT * FROM order_items WHERE order_id=%s", (entity_id,))
                                result['items'] = cursor.fetchall()
                            response = f"OK {json.dumps(result, cls=EnhancedJSONEncoder)}"
                        else:
                            response = "ERROR Not found"
                conn.close()
            else:
                response = "ERROR DB connection failed"

        elif command == "UPDATE":
            update_parts = parts[1].split(' ', 2)
            if len(update_parts) < 3:
                response = "ERROR Missing data for UPDATE"
            else:
                entity = update_parts[0]
                entity_id = update_parts[1]
                data_str = update_parts[2]
                payload = json.loads(data_str)
                
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    if entity == "PRODUCT":
                        cursor.execute(
                            "UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s",
                            (payload['name'], payload['price'], payload['stock'], entity_id)
                        )
                    elif entity == "CUSTOMER":
                        cursor.execute(
                            "UPDATE customers SET name=%s, email=%s, phone=%s WHERE id=%s",
                            (payload['name'], payload['email'], payload['phone'], entity_id)
                        )
                    elif entity == "ORDER":
                        cursor.execute(
                            "UPDATE orders SET order_date=%s, customer_name=%s, payment_method=%s, status=%s, total_price=%s WHERE id=%s",
                            (payload['date'], payload['customer'], payload['payment'], payload['status'], payload['total'], entity_id)
                        )
                        if 'items' in payload:
                            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (entity_id,))
                            for item in payload['items']:
                                cursor.execute(
                                    "INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)",
                                    (entity_id, item['product_name'], item['price'], item['amount'])
                                )
                    
                    conn.commit()
                    conn.close()
                    response = "OK Updated"
                else:
                    response = "ERROR DB connection failed"

        elif command == "DELETE":
            delete_parts = parts[1].split(' ', 1)
            if len(delete_parts) < 2:
                response = "ERROR Missing ID for DELETE"
            else:
                entity = delete_parts[0]
                entity_id = delete_parts[1]
                
                conn = get_connection()
                if conn:
                    cursor = conn.cursor()
                    if entity == "PRODUCT":
                        cursor.execute("DELETE FROM products WHERE id=%s", (entity_id,))
                    elif entity == "CUSTOMER":
                        cursor.execute("DELETE FROM customers WHERE id=%s", (entity_id,))
                    elif entity == "ORDER":
                        cursor.execute("DELETE FROM orders WHERE id=%s", (entity_id,))
                    
                    conn.commit()
                    conn.close()
                    response = "OK Deleted"
                else:
                    response = "ERROR DB connection failed"

        client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.send(f"ERROR {str(e)}".encode('utf-8'))
    finally:
        client_socket.close()

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server listening on port 9999")
    
    while True:
        client, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client)

if __name__ == "__main__":
    start_server()
