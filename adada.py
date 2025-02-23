import psycopg2
from psycopg2 import sql

def create_db(conn):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
                phone_number TEXT UNIQUE
            )
        ''')
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (first_name, last_name, email))
        client_id = cur.fetchone()[0]

        if phones:
            for phone in phones:
                cur.execute('''
                    INSERT INTO phones (client_id, phone_number)
                    VALUES (%s, %s)
                ''', (client_id, phone))
        conn.commit()

def add_phone(conn, client_id, phone):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO phones (client_id, phone_number)
            VALUES (%s, %s)
        ''', (client_id, phone))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        updates = []
        params = []
        if first_name:
            updates.append("first_name = %s")
            params.append(first_name)
        if last_name:
            updates.append("last_name = %s")
            params.append(last_name)
        if email:
            updates.append("email = %s")
            params.append(email)

        if updates:
            query = sql.SQL("UPDATE clients SET {} WHERE id = %s").format(sql.SQL(", ").join(map(sql.SQL, updates)))   
            params.append(client_id)
            cur.execute(query, params)

        if phones:
            cur.execute('''
                DELETE FROM phones WHERE client_id = %s
            ''', (client_id,))
            for phone in phones:
                cur.execute('''
                    INSERT INTO phones (client_id, phone_number)
                    VALUES (%s, %s)
                ''', (client_id, phone))
        conn.commit()

def delete_phone(conn, client_id, phone):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM phones
            WHERE client_id = %s AND phone_number = %s
        ''', (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM clients WHERE id = %s
        ''', (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    conn = psycopg2.connect(database="pampam", user="postgres", password="****")
    with conn.cursor() as cur:
        conditions = []
        params = []
        if first_name:
            conditions.append("first_name = %s")
            params.append(first_name)
        if last_name:
            conditions.append("last_name = %s")
            params.append(last_name)
        if email:
            conditions.append("email = %s")
            params.append(email)
        if phone:
            conditions.append("id IN (SELECT client_id FROM phones WHERE phone_number = %s)")
            params.append(phone)

        query = sql.SQL("SELECT * FROM clients WHERE {}").format(
            sql.SQL(" AND ").join(map(sql.SQL, conditions)))
        cur.execute(query, params)
        result = cur.fetchall()
        return result

with psycopg2.connect(database="pampam", user="postgres", password="****") as conn:
    create_db(conn)
    add_client(conn, "Vladimir", "Vladimirov", "Vladimir@gmail.com", ["+1111", "+2222"])
    add_client(conn, "Ivan", "Ivanov", "Ivan@gmail.com", ["+5555", "+6666"])
    add_phone(conn, 1, "+1111")
    change_client(conn, 1, first_name="Ivan", phones=["+3333", "+4444"])
    delete_phone(conn, 1, "+1111")
    clients = find_client(conn, first_name="Ivan")
    print(clients)
    delete_client(conn, 1)
conn.close()