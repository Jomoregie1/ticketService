import os
from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    pool_reset_session=True,
    host=os.getenv('HOST', '127.0.0.1'),
    user=os.getenv('USER', 'root'),
    password=os.getenv('PASSWORD', 'root'),
    database=os.getenv('DATABASE', 'ticketservice'),
    port=int(os.getenv('PORT', 3306))  # Explicitly set port with default to 3306
)

def get_db_connection():
    return connection_pool.get_connection()
