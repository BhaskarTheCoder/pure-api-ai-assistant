import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def query_database(query):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute(query)
    result = cur.fetchall()

    cur.close()
    conn.close()

    return result