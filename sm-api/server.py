from flask import (
    Flask,
    abort,
    request,
    jsonify,
    render_template
)


import uuid

import sqlite3

PORT=5000

db_path = "sm.db"

db_conn = sqlite3.connect(db_path)
db = db_conn.cursor()

db.execute('''CREATE TABLE IF NOT EXISTS servers_credentials (address text unique, method text, user text, secret text)''')
db.execute('''CREATE TABLE IF NOT EXISTS users (user_id text primary key unique, username text, public_key text)''')
db.execute('''CREATE TABLE IF NOT EXISTS shares (share_id integer primary key autoincrement, user_id text, server_address text, memory int, storage int, cpu int)''')

db_conn.close()

# Create the application instance
app = Flask(__name__, template_folder="templates")

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return render_template("home.html")

@app.route('/api/version')
def get_version():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    f = open("version.txt", 'r')
    version = f.readline().strip('\n')
    f.close()
    return jsonify({"version": version})

@app.route('/api/servers')
def get_servers():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    servers = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT address FROM servers_credentials"):
        servers.append({'address': row[0]})
    db_conn.close()
    return jsonify({'servers': servers})

@app.route('/api/servers', methods=['POST'])
def add_server():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    if not request.json:
        abort(400)

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("INSERT INTO servers_credentials VALUES (?,?,?,?)", [request.json['address'], request.json['method'], request.json['user'], request.json['secret']])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/servers/<string:server_id>', methods=['DELETE'])
def delete_server(server_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM servers_credentials WHERE address=?", [server_id])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/servers/<string:server_id>')
def get_server(server_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    server = []
    try:
        for row in db.execute("SELECT address, secret FROM servers_credentials WHERE address=?", [server_id]):
            server.append({"address": row[0], "secret": row[1]})
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'server':server})

@app.route('/api/users')
def get_users():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    users = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT user_id, username, public_key FROM users"):
        users.append({'id': row[0], 'username': row[1], 'public_key': row[2]})
        print(row[2])
    db_conn.close()
    return jsonify({'users': users})

@app.route('/api/users', methods=['POST'])
def add_user():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    if not request.json:
        abort(400)

    user_uuid = str(uuid.uuid4())

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("INSERT INTO users (user_id, username, public_key) VALUES (?,?,?)", [user_uuid, request.json['username'], request.json['public_key']])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM users WHERE user_id=?", [user_id])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/shares')
def get_shares():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    shares = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT shares.share_id, shares.user_id, users.username, shares.server_address FROM shares INNER JOIN users ON users.user_id = shares.user_id"):
        shares.append({'id': row[0], 'user_id': row[1], 'username': row[2], 'server': row[3]})
        print(row[2])
    db_conn.close()
    return jsonify({'shares': shares})

@app.route('/api/shares', methods=['POST'])
def add_share():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    if not request.json:
        abort(400)

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("INSERT INTO shares (user_id, server_address) VALUES (?,?)", [request.json['user_id'], request.json['server_address']])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/shares/<string:share_id>', methods=['DELETE'])
def delete_share(share_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM shares WHERE share_id=?", [share_id])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
