import sqlite3
from time import sleep
import requests
import json
import rsa
from base64 import b64encode
import datetime

db_path = "../../pbox.db"

def get_node_token(node):
    token = "test"
    # Check if I have a token in database
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT token from tokens WHERE address=?", [node]):
        token = row[0]

    # Check if token is still valid
    if(token != ""):
        r = requests.get('http://' + node + ':5001/api/version', headers={'X-Api-Token':token})
        if(r.status_code == 200):
            db_conn.close()
            return token


    # Delete all tokens concerning this server
    db.execute('DELETE FROM tokens WHERE address=?', [node])
    db_conn.commit()

    # If one of the answer is negative, get a new token
    # Generate seed
    seed = "test"
    r = requests.post('http://' + node + ':5001/api/auth', data=json.dumps({'seed':seed}), headers={'content-type':'application/json'})
    challenge = r.json()['challenge']

    for row in db.execute('SELECT private_key FROM certificates LIMIT 1'):
        private_key = row[0]
    pkey = rsa.PrivateKey.load_pkcs1(private_key)
    response = b64encode(rsa.sign(challenge.encode('utf-8'), pkey, "SHA-512")).decode('utf-8')

    r = requests.post('http://' + node + ':5001/api/auth', data=json.dumps({'challenge':challenge, 'response': response}), headers={'content-type':'application/json'})
    token = r.json()['token']

    # Save token
    db.execute('INSERT INTO tokens VALUES (?,?,?)', [node, token, datetime.datetime.now()])
    db_conn.commit()


    db_conn.close()
    return token

def get_node_version(node):
    token = get_node_token(node)
    r = requests.get('http://' + node + ':5001/api/version', headers={'X-Api-Token':token})
    if 'version' in r.json():
        return r.json()['version']
    else:
        return None


def get_nodes_list():
    nodes = []
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT address  secret FROM nodes"):
        nodes.append(row[0])

    db_conn.close()
    return nodes


# If we're running in stand alone mode, run the application
if __name__ == '__main__':

    while True:

        nodes = get_nodes_list()

        for node in nodes:
            print(get_node_version(node))
        # Wait before the next check
        sleep(10)
