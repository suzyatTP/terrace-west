from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL connection from Render (environment variable)
DATABASE_URL = os.environ.get("DATABASE_URL")  # Render injects this automatically

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class SeatAssignment(Base):
    __tablename__ = "seat_assignments"
    seat_id = Column(String, primary_key=True)  # e.g., "94", "92"
    name = Column(String)  # either "x" or a full name

Base.metadata.create_all(bind=engine)

@app.route('/')
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.route('/save', methods=['POST'])
def save_assignments():
    data = request.get_json()
    session = SessionLocal()

    # Clear existing assignments
    session.query(SeatAssignment).delete()

    # Insert updated assignments
    for seat_id, name in data.items():
        session.add(SeatAssignment(seat_id=seat_id, name=name))

    session.commit()
    session.close()
    return '', 204

@app.route('/load')
def load_assignments():
    session = SessionLocal()
    rows = session.query(SeatAssignment).all()
    data = {row.seat_id: row.name for row in rows}
    session.close()
    return jsonify(data)
