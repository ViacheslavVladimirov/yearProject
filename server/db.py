import mysql.connector
from mysql.connector import Error
import json
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / 'server_config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def get_connection():
    try:
        config = load_config()
        db_config = config['database']
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['name']
        )
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None
