from flask import Flask, jsonify, render_template
from flask_cors import CORS  # Import Flask-CORS
import ssh_module
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv('db_credentials.env')

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')

def connect_to_db():
    # Connect to the MySQL server
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database='shellm_sessions'
    )
    cursor = conn.cursor()

    return conn, cursor

app = Flask(__name__)

CORS(app)

# Route to fetch SSH sessions from the database
@app.route('/ssh_sessions', methods=['GET'])
def get_ssh_sessions():
    conn, cursor = connect_to_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor.execute("SELECT * FROM ssh_session ORDER BY id DESC;")
        sessions = cursor.fetchall()  # Fetch data as a list of dictionaries
        return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/shellm_sessions', methods=['GET'])
def get_shellm_sessions():
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM shellm_session ORDER BY id DESC;")
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(sessions)

@app.route('/commands', methods=['GET'])
def get_commands():
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM commands ORDER BY command_id DESC;")
    commands = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(commands)

@app.route('/answers', methods=['GET'])
def get_answers():
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM answers ORDER BY answer_id DESC;")
    answers = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(answers)

# Route to render the dashboard
@app.route('/', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/commands_answers/<int:shellm_session_id>', methods=['GET'])
def get_commands_answers(shellm_session_id):
    conn, cursor = connect_to_db()

    # Fetch commands and their associated answers
    cursor.execute("""
        SELECT c.command_id, c.command, a.answer_id, COALESCE(a.answer, 'No answer') AS answer
        FROM commands c
        LEFT JOIN answers a ON c.command_id = a.command_id
        WHERE c.shellm_session_id = %s
    """, (shellm_session_id,))

    results = cursor.fetchall()
    conn.close()

    # Return as a JSON response
     # Return as a JSON response
    return jsonify([
        {
            "command_id": row[0],
            "command": row[1],
            "answer_id": row[2],
            "answer": row[3]
        }
        for row in results
    ])

if __name__ == "__main__":
    app.run(debug=True)