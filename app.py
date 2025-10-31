from flask import Flask, request, redirect, url_for, render_template_string, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ------------ MySQL CONFIG ------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # your MySQL username
    "password": "dushyant@mysql",  # your MySQL password
    "database": "project_mgmt"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ------------ Initialize DB ------------
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(200),
        role ENUM('student','guide','coordinator') NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        creator_id INT,
        guide_id INT,
        status ENUM('ongoing','completed') DEFAULT 'ongoing',
        FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE SET NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_members (
        project_id INT,
        user_id INT,
        role_in_project ENUM('member','lead') DEFAULT 'member',
        PRIMARY KEY (project_id, user_id),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        project_id INT,
        title VARCHAR(255),
        description TEXT,
        assigned_to INT,
        status ENUM('To-Do','In Progress','Completed') DEFAULT 'To-Do',
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
    )""")

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ------------ HTML BASE ------------
BASE_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Student Project Management</title>
<style>
body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f7fa;
    color: #333;
}
.container {
    width: 90%;
    max-width: 1100px;
    margin: 40px auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
    padding: 25px 40px;
}
h1 {
    color: #0056b3;
    text-align: center;
    margin-bottom: 15px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
    border-radius: 8px;
    overflow: hidden;
}
th, td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: center;
}
th {
    background: #0056b3;
    color: white;
}
tr:nth-child(even) { background-color: #f2f2f2; }
tr:hover { background-color: #eaf2ff; transition: 0.3s; }

.btn {
    padding: 6px 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
}
.btn:hover {
    background-color: #0056b3;
    transition: 0.2s;
}
.flash {
    margin: 10px 0;
    padding: 10px;
    border-radius: 6px;
}
.flash.info { background: #e6f7ff; border-left: 5px solid #17a2b8; }
.flash.warning { background: #fff4e5; border-left: 5px solid #ffc107; }
.flash.danger { background: #ffe6e6; border-left: 5px solid #dc3545; }

.progress-bar {
    background: #e4e4e4;
    border-radius: 10px;
    width: 120px;
    display: inline-block;
    height: 12px;
    position: relative;
    top: 3px;
}
.progress-fill {
    background: linear-gradient(90deg, #4CAF50, #28a745);
    height: 12px;
    border-radius: 10px;
}
.percent-text {
    font-size: 0.85em;
    margin-left: 8px;
    color: #333;
}
.status-badge {
    padding: 4px 8px;
    border-radius: 6px;
    color: white;
    font-size: 0.85em;
}
.status-ongoing { background: #f0ad4e; }
.status-completed { background: #28a745; }

form {
    margin-top: 10px;
}
input, textarea, select {
    padding: 8px;
    width: 100%;
    border-radius: 6px;
    border: 1px solid #ccc;
    margin-bottom: 8px;
}
input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 5px rgba(0,123,255,0.5);
}

.header-links {
    text-align: center;
    margin-bottom: 10px;
}
.header-links a {
    color: #007bff;
    margin: 0 10px;
    text-decoration: none;
    font-weight: 500;
}
.header-links a:hover {
    text-decoration: underline;
}
</style>
<script>
function confirmDelete(){return confirm('Are you sure you want to delete this project?');}
function autoSubmit(form){form.submit();}
</script>
</head>
<body>
<div class="container">
<h1>Student Project Management System</h1>
<div>
{% with messages = get_flashed_messages(with_categories=true) %}
{% for category, msg in messages %}
<div class="flash {{ category }}">{{ msg }}</div>
{% endfor %}
{% endwith %}
</div>

<div class="header-links">
{% if session.user %}
<p>Logged in as <b>{{session.user.username}}</b> ({{session.user.role}})
<a href="{{ url_for('index') }}">Home</a> |
<a href="{{ url_for('logout') }}">Logout</a></p>
{% else %}
<a href="{{ url_for('index') }}">Home</a> |
<a href="{{ url_for('login') }}">Login</a> |
<a href="{{ url_for('register') }}">Register</a>
{% endif %}
</div>
<hr>
{{ content|safe }}
</div>
</body>
</html>
"""

# ------------ Helpers ------------
def query_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close(); conn.close()
    return user

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*a, **kw):
            if 'user' not in session:
                flash("Login required","warning")
                return redirect(url_for('login'))
            if role and session['user']['role']!=role:
                flash("Access denied","danger")
                return redirect(url_for('index'))
            return f(*a, **kw)
        return wrapper
    return decorator

# ------------ Routes ------------
@app.route('/')
def index():
    if 'user' not in session:
        return render_template_string(BASE_HTML, content="<p>Please <a href='/login'>login</a> or <a href='/register'>register</a>.</p>")
    role = session['user']['role']
    uid = session['user']['id']
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if role == 'student':
        cur.execute("""
        SELECT DISTINCT p.*, s.username AS creator_name, g.username AS guide_username
        FROM projects p
        LEFT JOIN users s ON p.creator_id=s.id
        LEFT JOIN users g ON p.guide_id=g.id
        LEFT JOIN project_members m ON p.id=m.project_id
        WHERE p.creator_id=%s OR m.user_id=%s
        """, (uid, uid))
    elif role == 'guide':
        cur.execute("""
        SELECT p.*, s.username AS creator_name, g.username AS guide_username
        FROM projects p
        LEFT JOIN users s ON p.creator_id=s.id
        LEFT JOIN users g ON p.guide_id=g.id
        WHERE p.guide_id=%s
        """, (uid,))
    else:
        cur.execute("""
        SELECT p.*, s.username AS creator_name, g.username AS guide_username
        FROM projects p
        LEFT JOIN users s ON p.creator_id=s.id
        LEFT JOIN users g ON p.guide_id=g.id
        """)

    projects = cur.fetchall()

    # Calculate progress %
    for p in projects:
        cur.execute("SELECT COUNT(*) AS total FROM tasks WHERE project_id=%s", (p['id'],))
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) AS completed FROM tasks WHERE project_id=%s AND status='Completed'", (p['id'],))
        completed = cur.fetchone()['completed']
        p['percent'] = round((completed / total * 100), 2) if total > 0 else 0

    cur.close(); conn.close()

    rows = ""
    for p in projects:
        percent_bar = f"""
        <div class='progress-bar'><div class='progress-fill' style='width:{p['percent']}%;'></div></div>
        <span class='percent-text'>{p['percent']}%</span>
        """
        badge_class = 'status-completed' if p['status'] == 'completed' else 'status-ongoing'
        rows += (f"<tr><td>{p['id']}</td><td>{p['title']}</td><td>{p.get('creator_name','')}</td>"
                 f"<td>{p.get('guide_username','-')}</td>"
                 f"<td><span class='status-badge {badge_class}'>{p['status'].capitalize()}</span></td>"
                 f"<td><a class='btn' href='/project/{p['id']}'>View</a> "
                 f"<form style='display:inline;' method='post' action='/project/{p['id']}/delete' onsubmit='return confirmDelete();'>"
                 f"<button class='btn' type='submit'>Delete</button></form> {percent_bar}</td></tr>")

    content = f"""
    <h3>Dashboard ({role.capitalize()})</h3>
    <table><tr><th>ID</th><th>Title</th><th>Creator</th><th>Guide</th><th>Status</th><th>Actions</th></tr>
    {rows or '<tr><td colspan=6>No projects</td></tr>'}</table>
    """
    if role == 'student':
        content += """
        <h3>Create New Project</h3>
        <form method='post' action='/project/create'>
        <input name='title' placeholder='Project Title' required><br>
        <textarea name='description' placeholder='Description'></textarea><br>
        <input name='guide_username' placeholder='Guide username (optional)'><br>
        <button class='btn'>Create</button></form>
        """
    return render_template_string(BASE_HTML, content=content)

# ------------ Authentication Routes ------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u, f, p, r = request.form.get('username').strip(), request.form.get('full_name'), request.form.get('password'), request.form.get('role')
        if query_user_by_username(u):
            flash("Username exists","warning"); return redirect(url_for('register'))
        h = generate_password_hash(p)
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password_hash,full_name,role) VALUES(%s,%s,%s,%s)", (u,h,f,r))
        conn.commit(); cur.close(); conn.close()
        flash("Registered! Please login.","info"); return redirect(url_for('login'))
    return render_template_string(BASE_HTML, content="""
    <h3>Register</h3>
    <form method='post'>
    <input name='username' placeholder='Username' required><br>
    <input name='full_name' placeholder='Full Name'><br>
    <input type='password' name='password' placeholder='Password' required><br>
    <select name='role'><option>student</option><option>guide</option><option>coordinator</option></select><br>
    <button class='btn'>Register</button></form>
    """)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u,p=request.form['username'],request.form['password']
        user=query_user_by_username(u)
        if not user or not check_password_hash(user['password_hash'],p):
            flash("Invalid credentials","danger"); return redirect(url_for('login'))
        session['user']={'id':user['id'],'username':user['username'],'role':user['role']}
        flash("Login successful!","info"); return redirect(url_for('index'))
    return render_template_string(BASE_HTML, content="""
    <h3>Login</h3>
    <form method='post'>
    <input name='username' placeholder='Username'><br>
    <input type='password' name='password' placeholder='Password'><br>
    <button class='btn'>Login</button></form>
    """)

@app.route('/logout')
def logout():
    session.pop('user',None)
    flash("Logged out","info")
    return redirect(url_for('index'))

# ------------ Project CRUD ------------
@app.route('/project/create', methods=['POST'])
@login_required('student')
def create_project():
    t, d, guser = request.form['title'], request.form.get('description'), request.form.get('guide_username')
    gid=None
    if guser:
        g=query_user_by_username(guser)
        if g and g['role']=='guide': gid=g['id']
        else: flash("Guide not found","warning")
    conn=get_db_connection(); cur=conn.cursor()
    cur.execute("INSERT INTO projects(title,description,creator_id,guide_id) VALUES(%s,%s,%s,%s)",(t,d,session['user']['id'],gid))
    pid=cur.lastrowid
    cur.execute("INSERT INTO project_members(project_id,user_id,role_in_project) VALUES(%s,%s,'lead')",(pid,session['user']['id']))
    conn.commit(); cur.close(); conn.close()
    flash("Project created!","info")
    return redirect(url_for('index'))

@app.route('/project/<int:pid>')
@login_required()
def view_project(pid):
    conn=get_db_connection();cur=conn.cursor(dictionary=True)
    cur.execute("""SELECT p.*, u.username AS creator, g.username AS guide
                   FROM projects p
                   LEFT JOIN users u ON p.creator_id=u.id
                   LEFT JOIN users g ON p.guide_id=g.id
                   WHERE p.id=%s""",(pid,))
    p=cur.fetchone()
    if not p:
        flash("Not found","warning"); return redirect(url_for('index'))
    cur.execute("SELECT u.username, m.role_in_project FROM project_members m JOIN users u ON m.user_id=u.id WHERE m.project_id=%s",(pid,))
    members=cur.fetchall()
    cur.execute("SELECT * FROM tasks WHERE project_id=%s",(pid,))
    tasks=cur.fetchall()
    cur.close();conn.close()

    member_rows="".join(f"<li>{m['username']} ({m['role_in_project']})</li>" for m in members)
    task_rows=""
    for t in tasks:
        if session['user']['id'] == p['creator_id'] or session['user']['id'] == p['guide_id']:
            task_rows += f"""
            <tr><td>{t['title']}</td>
            <td>
            <form method='post' action='/task/{t['id']}/update'>
            <select name='status' onchange='autoSubmit(this.form)'>
                <option {'selected' if t['status']=='To-Do' else ''}>To-Do</option>
                <option {'selected' if t['status']=='In Progress' else ''}>In Progress</option>
                <option {'selected' if t['status']=='Completed' else ''}>Completed</option>
            </select>
            <input type='hidden' name='pid' value='{pid}'>
            </form>
            </td></tr>"""
        else:
            task_rows += f"<tr><td>{t['title']}</td><td>{t['status']}</td></tr>"

    content=f"""
    <h3>Project: {p['title']}</h3>
    <p>{p['description'] or ''}</p>
    <p>Guide: {p.get('guide','-')}</p>
    <h4>Team Members</h4>
    <ul>{member_rows}</ul>
    <h4>Tasks</h4>
    <table><tr><th>Title</th><th>Status</th></tr>{task_rows or '<tr><td colspan=2>No tasks</td></tr>'}</table>
    """

    if session['user']['id'] == p['creator_id']:
        content += f"""
        <h4>Add New Task</h4>
        <form method='post' action='/project/{pid}/task/add'>
        <input name='title' placeholder='Task Title' required><br>
        <textarea name='description' placeholder='Task Description'></textarea><br>
        <select name='status'><option>To-Do</option><option>In Progress</option><option>Completed</option></select><br>
        <button class='btn'>Add Task</button></form>

        <h4>Add Team Member</h4>
        <form method='post' action='/project/{pid}/add_member'>
          <input name='username' placeholder='Enter student username' required>
          <button class='btn'>Add Member</button>
        </form>
        """

    content += f"""
    <form method='post' action='/project/{pid}/delete' onsubmit='return confirmDelete();'>
      <button class='btn' type='submit'>Delete Project</button>
    </form>
    """
    return render_template_string(BASE_HTML, content=content)

# ------------ Add Team Member ------------
@app.route('/project/<int:pid>/add_member', methods=['POST'])
@login_required()
def add_member(pid):
    username = request.form['username'].strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT creator_id FROM projects WHERE id=%s", (pid,))
    project = cur.fetchone()
    if not project:
        flash("Project not found", "warning")
        cur.close(); conn.close()
        return redirect(url_for('index'))
    if session['user']['id'] != project['creator_id']:
        flash("Only project lead can add members", "danger")
        cur.close(); conn.close()
        return redirect(f"/project/{pid}")
    cur.execute("SELECT id, role FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    if not user:
        flash("User not found", "warning")
    elif user['role'] != 'student':
        flash("Only students can be added as team members", "warning")
    else:
        cur.execute("SELECT * FROM project_members WHERE project_id=%s AND user_id=%s", (pid, user['id']))
        existing = cur.fetchone()
        if existing:
            flash("User already in team", "info")
        else:
            cur.execute("INSERT INTO project_members (project_id, user_id, role_in_project) VALUES (%s, %s, 'member')", (pid, user['id']))
            conn.commit()
            flash("Team member added!", "info")
    cur.close(); conn.close()
    return redirect(f"/project/{pid}")

# ------------ Task Update ------------
@app.route('/project/<int:pid>/task/add', methods=['POST'])
@login_required()
def add_task(pid):
    t=request.form['title']; d=request.form.get('description'); s=request.form.get('status')
    conn=get_db_connection(); cur=conn.cursor()
    cur.execute("INSERT INTO tasks(project_id,title,description,status) VALUES(%s,%s,%s,%s)",(pid,t,d,s))
    conn.commit(); cur.close(); conn.close()
    flash("Task added!","info")
    return redirect(f"/project/{pid}")

@app.route('/task/<int:tid>/update', methods=['POST'])
@login_required()
def update_task(tid):
    status=request.form['status']
    pid=request.form['pid']
    conn=get_db_connection(); cur=conn.cursor()
    cur.execute("UPDATE tasks SET status=%s WHERE id=%s",(status,tid))
    cur.execute("SELECT COUNT(*) FROM tasks WHERE project_id=%s",(pid,))
    total=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks WHERE project_id=%s AND status='Completed'",(pid,))
    completed=cur.fetchone()[0]
    new_status='completed' if total>0 and total==completed else 'ongoing'
    cur.execute("UPDATE projects SET status=%s WHERE id=%s",(new_status,pid))
    conn.commit(); cur.close(); conn.close()
    flash("Task status updated","info")
    return redirect(f"/project/{pid}")

@app.route('/project/<int:pid>/delete', methods=['POST'])
@login_required()
def delete_project(pid):
    conn=get_db_connection(); cur=conn.cursor()
    cur.execute("DELETE FROM projects WHERE id=%s",(pid,))
    conn.commit(); cur.close(); conn.close()
    flash("Project deleted","info")
    return redirect(url_for('index'))

# ------------ Run ------------
if __name__=="__main__":
    app.run(debug=True)
