from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import psycopg2

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def get_db_connection():
    db_url = os.environ.get("terrace_west_db")
    if not db_url:
        raise Exception("Environment variable 'terrace_west_db' not set.")
    return psycopg2.connect(db_url)

def ensure_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seat_assignments (
            seat_id TEXT PRIMARY KEY,
            name_line1 TEXT,
            name_line2 TEXT,
            is_blackout BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

ensure_table()

# ---------- ROUTES ----------
@app.route('/', methods=['GET', 'HEAD'])  # HEAD included for Render health check
def index():
    return send_from_directory('.', 'index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    # Clear all existing assignments
    cur.execute("DELETE FROM seat_assignments")

    for seat_id, value in data.items():
        if value[0] == 'x':
            cur.execute(
                "INSERT INTO seat_assignments (seat_id, is_blackout) VALUES (%s, TRUE)",
                (seat_id,)
            )
        else:
            cur.execute(
                "INSERT INTO seat_assignments (seat_id, name_line1, name_line2, is_blackout) VALUES (%s, %s, %s, FALSE)",
                (seat_id, value[0], value[1])
            )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify(status="success")

@app.route('/load', methods=['GET'])
def load():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT seat_id, name_line1, name_line2, is_blackout FROM seat_assignments")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = {}
    for seat_id, line1, line2, is_blackout in rows:
        if is_blackout:
            result[seat_id] = ["x"]
        else:
            result[seat_id] = [line1, line2]
    return jsonify(result)

@app.route('/health')
def health():
    return '', 204

# ---------- LOCAL RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
