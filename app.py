from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Configuration
DB_NAME = os.getenv('DB_NAME', 'notes.db')  # Default to 'notes.db' if not specified in .env
DEBUG_MODE = os.getenv('DEBUG', 'True').lower() == 'true'

app = Flask(__name__)

# CORS configuration for specific frontend domains
frontend_url = "https://dev.d2ja1oqjsjxh9q.amplifyapp.com"  # For React frontend in production
if os.getenv('FLASK_ENV') == 'development':  # Local environment check
    frontend_url = "http://localhost:3000"  # Local frontend URL for development

CORS(app, resources={r"/*": {"origins": [frontend_url, "https://main.d3mwc4763exqfp.amplifyapp.com", "*"]}})  # Allow all origins for now to test

# Initialize SQLite database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
    conn.close()

init_db()  # Create the database when the app starts

# Utility function to connect to the database
def get_db_connection():
    return sqlite3.connect(DB_NAME)

# Root route for testing
@app.route("/", methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the QuickNotes Backend!"})

# Route to get all notes
@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM notes")
        rows = cursor.fetchall()
        notes = [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    return jsonify(notes)

# Route to add a new note
@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Both title and content are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        note_id = cursor.lastrowid
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"id": note_id, "title": title, "content": content}), 201

# Route to delete a note by ID
@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"message": "Note deleted"}), 200

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)
