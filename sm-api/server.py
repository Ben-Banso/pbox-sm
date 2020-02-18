from flask import (
    Flask,
    abort,
    request,
    jsonify,
    render_template
)

from Crypto.PublicKey import RSA

import sqlite3

PORT=5000

db_path = "../../pbox.db"

db_conn = sqlite3.connect(db_path)
db = db_conn.cursor()

# Cluster
db.execute('''CREATE TABLE IF NOT EXISTS nodes (address text unique)''')
db.execute('''CREATE TABLE IF NOT EXISTS nodes_infos (address text, key text, value text)''')
db.execute('''CREATE TABLE IF NOT EXISTS tokens (address text unique, token text, creation_date timestamp)''')
# Servers
db.execute('''CREATE TABLE IF NOT EXISTS servers_credentials (server_id integer primary key autoincrement, address text unique, method text, user text, secret text)''')
db.execute('''CREATE TABLE IF NOT EXISTS users (username text primary key unique)''')
db.execute('''CREATE TABLE IF NOT EXISTS public_keys (key_id integer primary key autoincrement, username text, public_key text)''')
db.execute('''CREATE TABLE IF NOT EXISTS shares (share_id integer primary key autoincrement, username text, server_id int, memory int, storage int, cpu int)''')
# Account
db.execute('''CREATE TABLE IF NOT EXISTS certificates (key_id integer primary key autoincrement, private_key text, public_key text, status text, creation_date timestamp, revocation_date timestamp)''')
db.execute('''CREATE TABLE IF NOT EXISTS config (key text primary key unique, value text)''')

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

    for row in db.execute("SELECT server_id, address FROM servers_credentials"):
        servers.append({'id': row[0], 'address': row[1]})
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
        db.execute("INSERT INTO servers_credentials (address, method, user, secret) VALUES (?,?,?,?)", [request.json['address'], request.json['method'], request.json['user'], request.json['secret']])
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
        db.execute("DELETE FROM servers_credentials WHERE server_id=?", [server_id])
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
    server = ""
    try:
        for row in db.execute("SELECT server_id, address FROM servers_credentials WHERE server_id=?", [server_id]):
            server = {"id": row[0], "address": row[1]}
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'server':server})

@app.route('/api/servers/<string:server_id>/shares')
def get_server_shares(server_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    shares = []
    try:
        for row in db.execute("SELECT share_id, username FROM shares WHERE server_id=?", [server_id]):
            shares.append({"id": row[0], "username": row[1]})
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'shares':shares})

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
    for row in db.execute("SELECT key, value FROM config where key='username'"):
        users.append({'username': row[1]})
    for row in db.execute("SELECT username FROM users"):
        users.append({'username': row[0]})
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
        db.execute("INSERT INTO users (username) VALUES (?)", [request.json['username']])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM users WHERE username=?", [username])
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
        db.execute("INSERT INTO shares (username, server_id) VALUES (?,?)", [request.json['username'], request.json['server_id']])
        db_conn.commit()

        # Check if share is to owner
        infos ={}
        for row in db.execute("SELECT key, value FROM config where key='username'"):
            infos[row[0]] = row[1]

        # If yes, add a node to the cluster
        print(request.json['server_address'])
        if(request.json['username'] == infos['username']):
            print("yes it is")
            db.execute("INSERT INTO nodes (address) VALUES (?)", [request.json['server_address']])
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

@app.route('/api/nodes')
def get_nodes():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    nodes = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT address FROM nodes"):
        nodes.append({'address': row[0]})
    db_conn.close()
    return jsonify({'nodes': nodes})

@app.route('/api/nodes', methods=['POST'])
def add_node():
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
        db.execute("INSERT INTO nodes VALUES (?)", [request.json['address']])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/nodes/<string:node_id>', methods=['DELETE'])
def delete_node(node_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM nodes WHERE address=?", [node_id])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/nodes/<string:node_id>')
def get_node(node_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    node = []
    try:
        for row in db.execute("SELECT address FROM nodes WHERE address=?", [node_id]):
            node.append({"address": row[0]})
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'node':node})


@app.route('/api/account')
def get_account():
    """
    Get all the account settings

    :return:        a full list of user settings as JSON
    """
    infos = {}

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT key, value FROM config"):
        infos[row[0]] = row[1]
    db_conn.close()
    return jsonify({'infos': infos})

@app.route('/api/account/register', methods=['POST'])
def register_account():
    """
    Register the username locally, and generate the first certificate

    :return:        the rendered template 'home.html'
    """
    if not request.json:
        abort(400)

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("INSERT INTO config ('key','value') VALUES (?,?)", ["username", request.json['username']])
        db_conn.commit()
        db_conn.close()
        generate_certificate()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})

@app.route('/api/certificates')
def get_certificates():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    certificates = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT key_id, public_key FROM certificates"):
        certificates.append({'id': row[0], 'public_key':row[1]})
    db_conn.close()
    return jsonify({'certificates': certificates})

@app.route('/api/certificates/<string:certificate_id>')
def get_certificate(certificate_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    certificates = []

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    for row in db.execute("SELECT key_id, public_key, private_key FROM certificates"):
        certificate = [{'id': row[0], 'public_key':row[1], 'private_key': row[2]}]
    db_conn.close()
    return jsonify({'certificate': certificate})

@app.route('/api/certificates', methods=['POST'])
def generate_certificate():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    key = RSA.generate(2048)
    print(key.exportKey().decode())

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    try:
        db.execute("INSERT INTO certificates (private_key, public_key) VALUES (?,?)", [key.exportKey().decode(), key.publickey().exportKey().decode()])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})


@app.route('/api/certificates/<string:certificate_id>', methods=['DELETE'])
def delete_certificate(certificate_id):
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """

    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()

    try:
        db.execute("DELETE FROM certificates WHERE key_id=?", [certificate_id])
        db_conn.commit()
        db_conn.close()
    except sqlite3.IntegrityError:
        db_conn.close()
        abort(400)
    return jsonify({'success':True})


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT)
