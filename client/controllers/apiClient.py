import socket
import json

SERVER_HOST = 'localhost' 
SERVER_PORT = 9999

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

def send_command(command):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5.0)
        client.connect((SERVER_HOST, SERVER_PORT))
        
        send_msg(client, command)
        
        response = recv_msg(client)
        client.close()
        
        if response and response.startswith("OK"):
            body = response[3:].strip()

            if body in ["Created", "Updated", "Deleted"]:
                return True
            if not body:
                return True
            try:
                return json.loads(body)
            except json.JSONDecodeError as e:
                return f"ERROR JSON error: {str(e)}"
        else:
            return response if response else "ERROR Unknown server error"
    except Exception as e:
        return f"ERROR Network error: {str(e)}"

def get_all_products():
    return send_command("LIST PRODUCTS")

def get_all_customers():
    return send_command("LIST CUSTOMERS")

def get_all_orders():
    return send_command("LIST ORDERS")

def create_product(data):
    return send_command(f"CREATE PRODUCT {json.dumps(data)}")

def update_product(product_id, data):
    return send_command(f"UPDATE PRODUCT {product_id} {json.dumps(data)}")

def delete_product(product_id):
    return send_command(f"DELETE PRODUCT {product_id}")

def create_customer(data):
    return send_command(f"CREATE CUSTOMER {json.dumps(data)}")

def update_customer(customer_id, data):
    return send_command(f"UPDATE CUSTOMER {customer_id} {json.dumps(data)}")

def delete_customer(customer_id):
    return send_command(f"DELETE CUSTOMER {customer_id}")

def create_order(data):
    return send_command(f"CREATE ORDER {json.dumps(data)}")

def update_order(order_id, data):
    return send_command(f"UPDATE ORDER {order_id} {json.dumps(data)}")

def delete_order(order_id):
    return send_command(f"DELETE ORDER {order_id}")

def get_stats(start_date=None, end_date=None):
    if start_date and end_date:
        filters = json.dumps({"start_date": start_date, "end_date": end_date})
        return send_command(f"GET STATS {filters}")
    return send_command("GET STATS")

def ping():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1.0)
        client.connect((SERVER_HOST, SERVER_PORT))
        send_msg(client, "PING")
        response = recv_msg(client)
        client.close()
        return response == "OK PONG"
    except:
        return False
