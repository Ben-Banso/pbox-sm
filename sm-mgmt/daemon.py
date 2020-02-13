import paramiko
import sqlite3
from io import StringIO
from time import sleep
import requests

db_path = "../../pbox.db"

def get_servers_list():
    servers = []
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT address, method, user, secret, server_id FROM servers_credentials"):
        servers.append({"address":row[0], "method":row[1], "user":row[2], "secret":row[3], "id":row[4]})

    db_conn.close()
    return servers

def server_connect(server):
    if(server['method'] == "key"):
      print(StringIO(server['secret']))
      key = paramiko.RSAKey.from_private_key(StringIO(server['secret']))
      srv_conn = paramiko.SSHClient()
      srv_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      srv_conn.connect(server['address'], username=server['user'], pkey=key)
    else:
      print("Not implemented yet")
      return 0
    return srv_conn

def exec_basic(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout:
        print(line.strip('\n'))
    for line in stderr:
        print(line.strip('\n'))

def get_file_content(ssh, path):
    stdin, stdout, stderr = ssh.exec_command('cat ' + path)
    for line in stderr:
        print(line.strip('\n'))
    return stdout


def install_requirements(ssh):
    exec_basic(ssh, 'sudo dnf install -y unzip python3-flask python3-requests sqlite')
    exec_basic(ssh, 'sudo pip3 install gunicorn daemon lockfile rsa')

def list_packages(ssh):
    exec_basic(ssh, 'which gunicorn pacman yum dnf apt-get dockeri curl wget unzip')

def install_api(ssh):
    app_repo_url = "https://github.com/Ben-Banso/pbox-na/archive/master.zip"
    app_version_url = "https://raw.githubusercontent.com/Ben-Banso/pbox-na/master/na-daemon/version.txt"

    # Check version
    latest_version = requests.get(app_version_url).content.decode('utf-8')
    print(latest_version)
    actual_version = get_file_content(ssh, "pbox-na-master/na-daemon/version.txt").readline()
    print(actual_version)
    if(actual_version != latest_version):
        print("update!")
        # Download app
        exec_basic(ssh, 'sudo kill $(cat /tmp/na-daemon.pid)')
        exec_basic(ssh, 'rm -rf nm-daemon-master')
        exec_basic(ssh, 'curl -L ' + app_repo_url + ' --output master.zip')
        exec_basic(ssh, 'unzip master.zip')
        exec_basic(ssh, 'rm master.zip')
    else:
        print("do noting")

def config_users(server, ssh):
    users = []
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT shares.username, public_keys.public_key FROM shares INNER JOIN public_keys ON shares.username = public_keys.username WHERE shares.server_id=?", [server['id']]):
        users.append({"username":row[0], "public_key":row[1]})
    for row in db.execute("SELECT (SELECT value FROM config where key='username'), certificates.public_key FROM certificates"):
        users.append({"username":row[0], "public_key":row[1]})


    exec_basic(ssh, 'sudo sqlite3 /home/ben/na.db "CREATE TABLE IF NOT EXISTS users (username text, public_key text)"')
    exec_basic(ssh, 'sudo sqlite3 /home/ben/na.db "DELETE FROM users"')
    for user in users:
        print(user['username'])
        exec_basic(ssh, 'sudo sqlite3 /home/ben/na.db "INSERT INTO users (username, public_key) VALUES(\'' + user['username'] + '\', \'' + user['public_key'] + '\')"')
    exec_basic(ssh, 'sudo  chown ben /home/ben/na.db')

    db_conn.close()

# If we're running in stand alone mode, run the application
if __name__ == '__main__':

    while True:

        servers = get_servers_list()

        for server in servers:
            ssh = server_connect(server)
            install_requirements(ssh)
            #list_packages(ssh)
            install_api(ssh)
            config_users(server, ssh)
            ssh.close()
        # Wait before the next check
        sleep(10)
