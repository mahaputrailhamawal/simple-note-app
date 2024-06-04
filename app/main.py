from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

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
