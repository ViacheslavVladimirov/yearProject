import socket
import json

# Change this to your server's IP address when running over the network
SERVER_HOST = 'localhost' 
SERVER_PORT = 9999

def send_msg(sock, msg):
    # Prefix each message with a 10-byte length header
    msg_bytes = msg.encode('utf-8')
    header = f"{len(msg_bytes):010d}".encode('utf-8')
    sock.sendall(header + msg_bytes)

def recv_msg(sock):
    # Read the 10-byte length header
    try:
        header_data = sock.recv(10)
        if not header_data:
            return None
        header = header_data.decode('utf-8')
        msg_len = int(header)
    except (ValueError, socket.error):
        return None
    
    # Read the actual message body
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
        client.settimeout(5.0) # increased timeout for network reliability
        client.connect((SERVER_HOST, SERVER_PORT))
        
        send_msg(client, command)
        
        response = recv_msg(client)
        client.close()
        
        if response and response.startswith("OK"):
            body = response[3:].strip()
            # Handle non-JSON success messages like "Created" or "Updated"
            if body in ["Created", "Updated", "Deleted"]:
                return True
            if not body:
                return True
            try:
                return json.loads(body)
            except json.JSONDecodeError as e:
                print(f"JSON error: {e}, body: '{body}'")
                return body
        else:
            print(f"Server error: {response}")
            return None
    except Exception as e:
        print(f"Network error: {e}")
        return None

# These functions mimic the old direct DB access but use the network protocol
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
        client.settimeout(1.0) # Slightly longer timeout for network ping
        client.connect((SERVER_HOST, SERVER_PORT))
        send_msg(client, "PING")
        response = recv_msg(client)
        client.close()
        return response == "OK PONG"
    except:
        return False
