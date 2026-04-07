from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("bpo.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- INIT ----------
def init_db():
    conn = sqlite3.connect("bpo.db")
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("INSERT OR IGNORE INTO users VALUES(1,'admin','admin')")

    cur.execute("CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, salary REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS clients(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, company TEXT)")

    conn.commit()
    conn.close()

# ---------- LOGIN ----------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()
        conn.close()

        if user:
            session['user'] = u
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("dashboard.html")

# ================= EMPLOYEES =================
@app.route('/employees')
def employees():
    if 'user' not in session:
        return redirect('/')

    search = request.args.get('search')
    conn = get_db()

    if search:
        data = conn.execute("SELECT * FROM employees WHERE name LIKE ?",('%'+search+'%',)).fetchall()
    else:
        data = conn.execute("SELECT * FROM employees").fetchall()

    conn.close()
    return render_template("employees.html", employees=data)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    role = request.form['role']
    salary = request.form['salary']

    conn = get_db()
    conn.execute("INSERT INTO employees(name,role,salary) VALUES(?,?,?)",(name,role,salary))
    conn.commit()
    conn.close()
    return redirect('/employees')

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db()
    conn.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/employees')

@app.route('/edit_employee/<int:id>')
def edit_employee(id):
    conn = get_db()
    emp = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_employee.html", emp=emp)

@app.route('/update_employee/<int:id>', methods=['POST'])
def update_employee(id):
    name = request.form['name']
    role = request.form['role']
    salary = request.form['salary']

    conn = get_db()
    conn.execute("UPDATE employees SET name=?, role=?, salary=? WHERE id=?",
                 (name, role, salary, id))
    conn.commit()
    conn.close()
    return redirect('/employees')

# ================= CLIENTS =================
@app.route('/clients')
def clients():
    if 'user' not in session:
        return redirect('/')

    search = request.args.get('search')
    conn = get_db()

    if search:
        data = conn.execute("SELECT * FROM clients WHERE name LIKE ?",('%'+search+'%',)).fetchall()
    else:
        data = conn.execute("SELECT * FROM clients").fetchall()

    conn.close()
    return render_template("clients.html", clients=data)

@app.route('/add_client', methods=['POST'])
def add_client():
    name = request.form['name']
    company = request.form['company']

    conn = get_db()
    conn.execute("INSERT INTO clients(name,company) VALUES(?,?)",(name,company))
    conn.commit()
    conn.close()
    return redirect('/clients')

@app.route('/delete_client/<int:id>')
def delete_client(id):
    conn = get_db()
    conn.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/clients')

@app.route('/edit_client/<int:id>')
def edit_client(id):
    conn = get_db()
    c = conn.execute("SELECT * FROM clients WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit_client.html", client=c)

@app.route('/update_client/<int:id>', methods=['POST'])
def update_client(id):
    name = request.form['name']
    company = request.form['company']

    conn = get_db()
    conn.execute("UPDATE clients SET name=?, company=? WHERE id=?",
                 (name, company, id))
    conn.commit()
    conn.close()
    return redirect('/clients')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)