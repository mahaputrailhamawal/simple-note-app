from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import psycopg2
import os

app = Flask(__name__)
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python3 -c \"import secrets; print(secrets.token_hex(32))\""
    )
app.config['SECRET_KEY'] = secret_key

# 'Lax' instead of 'Strict' — Strict blocks session cookie on normal page navigation
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Only True when running HTTPS — True on HTTP causes browser to drop session cookie
is_https = os.environ.get('HTTPS_ENABLED', 'false').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = is_https

app.config['SESSION_COOKIE_HTTPONLY'] = True  # prevent JS access

csrf = CSRFProtect(app)  # Fix: Anti-CSRF tokens on all forms

@app.after_request
def set_security_headers(response):
    # Fix: CSP + clickjacking
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    # Fix: clickjacking (belt & suspenders with CSP above)
    response.headers['X-Frame-Options'] = 'DENY'
    # Fix: MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Fix: Cross-origin headers
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    # Fix: Permissions policy
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
    )
    # Fix: Server version leak
    response.headers['Server'] = ''
    # Fix: Cache control for task routes
    if request.path.startswith('/task/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Koneksi ke database PostgreSQL
conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"]
)

# Fungsi untuk membuat tabel tugas
def create_task_table():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            description TEXT
        );
    """)
    conn.commit()
    cursor.close()

# Fungsi untuk menambahkan tugas baru
def add_task(title, description):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description)
        VALUES (%s, %s);
    """, (title, description))
    conn.commit()
    cursor.close()

# Fungsi untuk mendapatkan semua tugas
def get_all_tasks():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks;")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# Fungsi untuk menghapus tugas berdasarkan ID
def delete_task(task_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
    conn.commit()
    cursor.close()

# Fungsi untuk mendapatkan tugas berdasarkan ID
def get_task(task_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    return task

@app.route("/")
def index():
    tasks = get_all_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/task/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        add_task(title, description)
        return redirect(url_for("index"))
    return render_template("task.html", action="Add", task=None)

@app.route("/task/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    task = get_task(task_id)
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET title = %s, description = %s
            WHERE id = %s;
        """, (title, description, task_id))
        conn.commit()
        cursor.close()
        return redirect(url_for("index"))
    return render_template("task.html", action="Edit", task=task)

@app.route("/task/delete/<int:task_id>")
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    create_task_table()
    app.run(host="0.0.0.0")
