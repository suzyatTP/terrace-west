from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import psycopg2

app = Flask(__name__)
CORS(app)

# Connect to PostgreSQL
def get_db_connection():
    db_url = os.environ.get("TERRACE_WEST_DB")
    if not db_url:
        raise Exception("Environment variable 'TERRACE_WEST_DB' not set.")
    return psycopg2.connect(db_url)

# Create table if not exists
def ensure_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            seat_id TEXT PRIMARY KEY,
            name TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

ensure_table()

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/save', methods=['POST'])
def save_assignments():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    for seat_id, name in data.items():
        cur.execute('''
            INSERT INTO assignments (seat_id, name)
            VALUES (%s, %s)
            ON CONFLICT (seat_id) DO UPDATE SET name = EXCLUDED.name;
        ''', (seat_id, name if name != ["x"] else "x"))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/load', methods=['GET'])
def load_assignments():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT seat_id, name FROM assignments;')
    assignments = dict(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(assignments)

if __name__ == '__main__':
    app.run(debug=True)
