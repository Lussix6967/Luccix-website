import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

# Intelligente Verbindungs-Funktion (Render oder Lokal)
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Live-Betrieb auf Render (PostgreSQL)
        return psycopg2.connect(db_url, sslmode='require')
    else:
        # Lokaler Testbetrieb auf deinem PC (SQLite)
        conn = sqlite3.connect('local_votes.db')
        return conn

# Erstellt die Tabelle und fügt deine Produkte ein, falls noch leer
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # PostgreSQL live auf Render
        cur.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                item_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100),
                bild_url VARCHAR(200),
                stimmen INTEGER DEFAULT 0
            );
        ''')
        conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM votes;")
        row = cur.fetchone()
        count = row[0] if row else 0
        
        if count == 0:
            cur.execute("INSERT INTO votes (item_id, name, bild_url, stimmen) VALUES (%s, %s, %s, %s)",
                        ("oversized_hoodie", "LUCCIX BOXY SHIRT", "/static/shirt.png", 0))
            cur.execute("INSERT INTO votes (item_id, name, bild_url, stimmen) VALUES (%s, %s, %s, %s)",
                        ("cargo_hose", "LUCCIX FITTED CAP", "/static/cap.png", 0))
            conn.commit()
    else:
        # SQLite lokal auf deinem PC
        cur.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                item_id TEXT PRIMARY KEY,
                name TEXT,
                bild_url TEXT,
                stimmen INTEGER DEFAULT 0
            );
        ''')
        conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM votes;")
        # Hier lesen wir das rohe Tupel aus, bevor wir row_factory nutzen
        row = cur.fetchone()
        count = row[0] if row else 0
        
        if count == 0:
            cur.execute("INSERT INTO votes (item_id, name, bild_url, stimmen) VALUES (?, ?, ?, ?)",
                        ("oversized_hoodie", "LUCCIX BOXY SHIRT", "/static/shirt.png", 0))
            cur.execute("INSERT INTO votes (item_id, name, bild_url, stimmen) VALUES (?, ?, ?, ?)",
                        ("cargo_hose", "LUCCIX FITTED CAP", "/static/cap.png", 0))
            conn.commit()
        
    cur.close()
    conn.close()

# Datenbank beim Start initialisieren
init_db()

@app.route('/')
def home():
    voted_items = request.cookies.get('voted_items', '')
    voted_list = voted_items.split(',') if voted_items else []

    conn = get_db_connection()
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT item_id, name, bild_url, stimmen FROM votes;")
        rows = cur.fetchall()
    else:
        # WICHTIG: row_factory genau hier setzen, damit row['spaltenname'] funktioniert!
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT item_id, name, bild_url, stimmen FROM votes;")
        rows = cur.fetchall()
    
    klamotten_daten = {}
    for row in rows:
        klamotten_daten[row['item_id']] = {
            "name": row['name'],
            "bild_url": row['bild_url'],
            "stimmen": row['stimmen']
        }
        
    cur.close()
    conn.close()
    return render_template('mode_index.html', klamotten=klamotten_daten, voted_items=voted_list)

@app.route('/vote/<item_id>', methods=['POST'])
def vote(item_id):
    voted_items = request.cookies.get('voted_items', '')
    voted_list = voted_items.split(',') if voted_items else []
    
    conn = get_db_connection()
    cur = conn.cursor()
    db_url = os.environ.get('DATABASE_URL')

    if item_id in voted_list:
        voted_list.remove(item_id)
        if db_url:
            cur.execute("UPDATE votes SET stimmen = GREATEST(0, stimmen - 1) WHERE item_id = %s;", (item_id,))
        else:
            cur.execute("UPDATE votes SET stimmen = CASE WHEN stimmen > 0 THEN stimmen - 1 ELSE 0 END WHERE item_id = ?;", (item_id,))
    else:
        voted_list.append(item_id)
        if db_url:
            cur.execute("UPDATE votes SET stimmen = stimmen + 1 WHERE item_id = %s;", (item_id,))
        else:
            cur.execute("UPDATE votes SET stimmen = stimmen + 1 WHERE item_id = ?;", (item_id,))
        
    conn.commit()
    cur.close()
    conn.close()
    
    new_voted_items = ','.join(voted_list)
    resp = make_response({"status": "success"})
    resp.set_cookie('voted_items', new_voted_items, max_age=30*24*60*60)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
