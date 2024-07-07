import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def _connect_to_db():
    mydb = mysql.connector.connect(
        host=os.getenv("USER"),
        user=os.getenv("HOST"),
        password=os.getenv("PASSWORD"),
        database="ticketservice"
    )

    return mydb
