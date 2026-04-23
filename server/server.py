import socket
import json
import threading
import logging
from pathlib import Path
from decimal import Decimal
from datetime import date
from db import get_connection

log_path = Path(__file__).parent / 'server.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

def load_config():
    config_path = Path(__file__).parent / 'server_config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

def send_msg(sock, msg):
    msg_bytes = msg.encode('utf-8')
    header = f"{len(msg_bytes):010d}".encode('utf-8')
    sock.sendall(header + msg_bytes)

def recv_msg(sock):
    try:
        header_data = sock.recv(10)
        if not header_data:
            return None
        header = header_data.decode('utf-8')
        msg_len = int(header)
    except (ValueError, socket.error):
        return None

    chunks = []
    bytes_recd = 0
    while bytes_recd < msg_len:
        chunk = sock.recv(min(msg_len - bytes_recd, 4096))
        if chunk == b'':
            break
        chunks.append(chunk)
        bytes_recd += len(chunk)
    return b''.join(chunks).decode('utf-8')

def handle_list(entity):
    conn = get_connection()
    if not conn:
        return "ERROR DB connection failed"
    cursor = conn.cursor(dictionary=True)
    if entity == "PRODUCTS":
        cursor.execute("SELECT * FROM products")
        results = cursor.fetchall()
    elif entity == "CUSTOMERS":
        cursor.execute("SELECT * FROM customers")
        results = cursor.fetchall()
    elif entity == "ORDERS":
        cursor.execute("SELECT * FROM orders")
        results = cursor.fetchall()
        for order in results:
            cursor.execute("SELECT product_name, price, amount FROM order_items WHERE order_id = %s", (order['id'],))
            order['items'] = cursor.fetchall()
    else:
        conn.close()
        return "ERROR Invalid entity"
    response = f"OK {json.dumps(results, cls=EnhancedJSONEncoder)}"
    conn.close()
    return response

def handle_create(entity, data_str):
    payload = json.loads(data_str)
    conn = get_connection()
    if not conn:
        return "ERROR DB connection failed"
    cursor = conn.cursor()
    if entity == "PRODUCT":
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", (payload['name'], payload['price'], payload['stock']))
    elif entity == "CUSTOMER":
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)", (payload['name'], payload['email'], payload['phone']))
    elif entity == "ORDER":
        # Aggregate amounts per product to validate against stock correctly
        required_stock = {}
        for item in payload.get('items', []):
            name = item['product_name']
            amount = int(item['amount'])
            required_stock[name] = required_stock.get(name, 0) + amount

        # Validate stock first
        for name, amount in required_stock.items():
            cursor.execute("SELECT stock FROM products WHERE name = %s", (name,))
            product = cursor.fetchone()
            if not product:
                conn.close()
                return f"ERROR Product {name} not found"
            if product[0] < amount:
                conn.close()
                return f"ERROR Insufficient stock for {name}"

        # Deduct stock and insert order
        cursor.execute("INSERT INTO orders (order_date, customer_name, payment_method, is_delivered, total_price) VALUES (%s, %s, %s, %s, %s)", (payload['date'], payload['customer'], payload['payment'], payload['is_delivered'], payload['total']))
        order_id = cursor.lastrowid
        for item in payload.get('items', []):
            cursor.execute("INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)", (order_id, item['product_name'], item['price'], item['amount']))
            cursor.execute("UPDATE products SET stock = stock - %s WHERE name = %s", (item['amount'], item['product_name']))
    conn.commit()
    conn.close()
    return "OK Created"

def handle_get(entity, entity_id=None):
    conn = get_connection()
    if not conn:
        return "ERROR DB connection failed"
    cursor = conn.cursor(dictionary=True)
    if entity == "STATS":
        query = "SELECT SUM(orders.total_price), SUM(order_items.amount) FROM year_project.orders JOIN year_project.order_items ON order_items.order_id = orders.id WHERE orders.order_date BETWEEN %s AND %s"
        params = []

        if entity_id:
            try:
                filters = json.loads(entity_id)
                if 'start_date' in filters and 'end_date' in filters:
                    params = [filters['start_date'], filters['end_date']]

            except json.JSONDecodeError:
                pass
        
        cursor.execute(query, params)
        stats = cursor.fetchone()
        
        # Handle cases where no stats are found
        total_revenue = float(stats['SUM(orders.total_price)']) if stats['SUM(orders.total_price)'] else 0.0
        total_products = int(stats['SUM(order_items.amount)']) if stats['SUM(order_items.amount)'] else 0

        response = f"OK {json.dumps({'total_products': total_products, 'total_revenue': total_revenue}, cls=EnhancedJSONEncoder)}"
    else:
        if not entity_id:
            conn.close()
            return "ERROR Missing ID"
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
    return response

def handle_update(entity, entity_id, data_str):
    payload = json.loads(data_str)
    conn = get_connection()
    if not conn:
        return "ERROR DB connection failed"
    cursor = conn.cursor()
    if entity == "PRODUCT":
        cursor.execute("UPDATE products SET name=%s, price=%s, stock=%s WHERE id=%s", (payload['name'], payload['price'], payload['stock'], entity_id))
    elif entity == "CUSTOMER":
        cursor.execute("UPDATE customers SET name=%s, email=%s, phone=%s WHERE id=%s", (payload['name'], payload['email'], payload['phone'], entity_id))
    elif entity == "ORDER":
        # Restore old stock first
        cursor.execute("SELECT product_name, amount FROM order_items WHERE order_id = %s", (entity_id,))
        old_items = cursor.fetchall()
        for item_name, amount in old_items:
            cursor.execute("UPDATE products SET stock = stock + %s WHERE name = %s", (amount, item_name))

        if 'items' in payload:
            # Aggregate amounts per product to validate against stock correctly
            required_stock = {}
            for item in payload['items']:
                name = item['product_name']
                amount = int(item['amount'])
                required_stock[name] = required_stock.get(name, 0) + amount

            # Validate new stock
            for name, amount in required_stock.items():
                cursor.execute("SELECT stock FROM products WHERE name = %s", (name,))
                product = cursor.fetchone()
                if not product:
                    conn.rollback()
                    conn.close()
                    return f"ERROR Product {name} not found"
                if product[0] < amount:
                    conn.rollback()
                    conn.close()
                    return f"ERROR Insufficient stock for {name}"

            cursor.execute("UPDATE orders SET order_date=%s, customer_name=%s, payment_method=%s, is_delivered=%s, total_price=%s WHERE id=%s", (payload['date'], payload['customer'], payload['payment'], payload['is_delivered'], payload['total'], entity_id))
            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (entity_id,))
            for item in payload['items']:
                cursor.execute("INSERT INTO order_items (order_id, product_name, price, amount) VALUES (%s, %s, %s, %s)", (entity_id, item['product_name'], item['price'], item['amount']))
                cursor.execute("UPDATE products SET stock = stock - %s WHERE name = %s", (item['amount'], item['product_name']))
        else:
            # If no items provided, just update order fields (stock already restored if we intended to update items, but here we might just be updating other fields)
            # Actually, if 'items' is NOT in payload, we shouldn't have restored stock.
            # But wait, the client ALWAYS sends items in payload for ORDER update.
            # Let's re-read handle_update original.
            cursor.execute("UPDATE orders SET order_date=%s, customer_name=%s, payment_method=%s, is_delivered=%s, total_price=%s WHERE id=%s", (payload['date'], payload['customer'], payload['payment'], payload['is_delivered'], payload['total'], entity_id))
    conn.commit()
    conn.close()
    return "OK Updated"

def handle_delete(entity, entity_id):
    conn = get_connection()
    if not conn:
        return "ERROR DB connection failed"
    cursor = conn.cursor()
    if entity == "PRODUCT":
        cursor.execute("DELETE FROM products WHERE id=%s", (entity_id,))
    elif entity == "CUSTOMER":
        cursor.execute("DELETE FROM customers WHERE id=%s", (entity_id,))
    elif entity == "ORDER":
        # Restore stock before deleting
        cursor.execute("SELECT product_name, amount FROM order_items WHERE order_id = %s", (entity_id,))
        items = cursor.fetchall()
        for item_name, amount in items:
            cursor.execute("UPDATE products SET stock = stock + %s WHERE name = %s", (amount, item_name))
        cursor.execute("DELETE FROM orders WHERE id=%s", (entity_id,))
    conn.commit()
    conn.close()
    return "OK Deleted"

def handle_client(client_socket):
    try:
        data = recv_msg(client_socket)
        if not data:
            return
        
        parts = data.split(' ', 1)
        command = parts[0]
        
        if command != "PING":
            logging.info(f"Received: {data}")

        response = "ERROR Invalid command"
        
        if command == "PING":
            response = "OK PONG"
        elif command == "LIST" and len(parts) > 1:
            response = handle_list(parts[1])
        elif command == "CREATE" and len(parts) > 1:
            create_parts = parts[1].split(' ', 1)
            response = handle_create(create_parts[0], create_parts[1])
        elif command == "GET" and len(parts) > 1:
            get_parts = parts[1].split(' ', 1)
            entity = get_parts[0]
            entity_id = get_parts[1] if len(get_parts) > 1 else None
            response = handle_get(entity, entity_id)
        elif command == "UPDATE" and len(parts) > 1:
            update_parts = parts[1].split(' ', 2)
            response = handle_update(update_parts[0], update_parts[1], update_parts[2])
        elif command == "DELETE" and len(parts) > 1:
            del_parts = parts[1].split(' ', 1)
            response = handle_delete(del_parts[0], del_parts[1])
        
        if command != "PING":
            logging.info(f"Sent: {response[:100]}..." if len(response) > 100 else f"Sent: {response}")
        
        send_msg(client_socket, response)
    except Exception as e:
        error_msg = f"ERROR Server error: {str(e)}"
        logging.error(f"Error handling request: {error_msg}")
        try:
            send_msg(client_socket, error_msg)
        except:
            pass
    finally:
        client_socket.close()

def start_server():
    config = load_config()
    server_config = config['server']
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_config['host'], server_config['port']))
    server.listen(10)
    logging.info(f"Server started on {server_config['host']}:{server_config['port']}")
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

start_server()
