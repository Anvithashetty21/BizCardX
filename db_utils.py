import mysql.connector
from typing import List, Dict

DB_NAME = "bizcardxdb"

def get_db_conn(no_db: bool = False):
    cfg = {
        "user": "root",
        "password": "admin",
        "host": "localhost",
        "auth_plugin": "mysql_native_password"
    }
    if not no_db:
        cfg["database"] = DB_NAME
    return mysql.connector.connect(**cfg)

def init_db():
    conn = get_db_conn(no_db=True)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4")
    conn.commit()
    conn.close()

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS BUSINESS_CARD (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Name VARCHAR(100),
            Designation VARCHAR(100),
            Company VARCHAR(100),
            Contact VARCHAR(50),
            Email VARCHAR(100),
            Website VARCHAR(200),
            Address TEXT,
            Pincode VARCHAR(20),
            Image LONGBLOB
        )
    """)
    conn.commit()
    return conn

def insert_card(conn, d: Dict[str, str], img_bytes: bytes = None):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO BUSINESS_CARD
        (Name, Designation, Company, Contact, Email, Website, Address, Pincode, Image)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        d.get("Name",""), d.get("Designation",""), d.get("Company",""),
        d.get("Contact",""), d.get("Email",""), d.get("Website",""),
        d.get("Address",""), d.get("Pincode",""), img_bytes
    ))
    conn.commit()

def list_cards(conn) -> List[Dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM BUSINESS_CARD ORDER BY id ASC")
    return cur.fetchall()

def fetch_names(conn) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Name FROM BUSINESS_CARD")
    return [r[0] for r in cur.fetchall()]

def delete_card(conn, name: str, designation: str) -> bool:
    cur = conn.cursor()
    cur.execute("DELETE FROM BUSINESS_CARD WHERE Name=%s AND Designation=%s", (name, designation))
    conn.commit()
    return cur.rowcount > 0
