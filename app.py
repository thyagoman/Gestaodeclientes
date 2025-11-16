# app.py (CORRIGIDO PARA FLASK 3.1.2)

from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
from pathlib import Path

# ========= CONFIGURAÇÃO =========
app = Flask(__name__)
DB_PATH = Path(__file__).parent / 'clients.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )''')
        c.commit()

# ========= INICIALIZAÇÃO (CORRIGIDO) =========
# Removido @app.before_first_request
with app.app_context():
    init_db()  # Cria o banco na primeira execução

# ========= ROTAS =========
@app.route('/clients')
def list_clients():
    with get_conn() as c:
        cur = c.execute('SELECT * FROM client ORDER BY id DESC')
        clients = cur.fetchall()
    return render_template('list.html', clients=clients)

@app.route('/clients/new', methods=('GET', 'POST'))
def new_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        with get_conn() as c:
            c.execute('INSERT INTO client (name, email, phone) VALUES (?, ?, ?)',
                      (name, email, phone))
            c.commit()
        return redirect(url_for('list_clients'))
    return render_template('form.html', client=None)

@app.route('/clients/edit/<int:id>', methods=('GET', 'POST'))
def edit_client(id):
    with get_conn() as c:
        cur = c.execute('SELECT * FROM client WHERE id = ?', (id,))
        client = cur.fetchone()

    if client is None:
        abort(404)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')

        with get_conn() as c:
            c.execute('UPDATE client SET name = ?, email = ?, phone = ? WHERE id = ?',
                      (name, email, phone, id))
            c.commit()
        return redirect(url_for('list_clients'))

    return render_template('form.html', client=client)

# ========= EXECUÇÃO =========
if __name__ == '__main__':
    app.run(debug=True)