import paramiko
import sqlite3
from io import StringIO
from time import sleep
import requests

db_path = "sm.db"

db_conn = sqlite3.connect(db_path)
db = db_conn.cursor()

db.execute('''CREATE TABLE IF NOT EXISTS servers_credentials (address text unique, method text, user text, secret text)''')

db_conn.close()

def get_servers_list():
    servers = []
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT address, method, user, secret FROM servers_credentials"):
        servers.append({"address":row[0], "method":row[1], "user":row[2], "secret":StringIO(row[3])})

    db_conn.close()
    return servers

def server_connect(server):
    key = paramiko.RSAKey.from_private_key(servers[0]['secret'])
    srv_conn = paramiko.SSHClient()
    srv_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    srv_conn.connect(servers[0]['address'], username=servers[0]['user'], pkey=key)
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
    exec_basic(ssh, 'sudo yum install -y unzip python-gunicorn')

def list_packages(ssh):
    exec_basic(ssh, 'which gunicorn pacman yum dnf apt-get dockeri curl wget unzip')

def install_api(ssh):
    app_repo_url = "https://github.com/Ben-Banso/nm-daemon/archive/master.zip"
    app_version_url = "https://raw.githubusercontent.com/Ben-Banso/nm-daemon/master/version.txt"

    # Check version
    latest_version = requests.get(app_version_url).content.decode('utf-8')
    print(latest_version)
    actual_version = get_file_content(ssh, "nm-daemon-master/version.txt").readline()
    print(actual_version)
    if(actual_version != latest_version):
        print("update!")
        # Download app
        exec_basic(ssh, 'sudo kill $(cat /tmp/nm-daemon.pid)')
        exec_basic(ssh, 'rm -rf nm-daemon-master')
        exec_basic(ssh, 'curl -L ' + app_repo_url + ' --output master.zip')
        exec_basic(ssh, 'unzip master.zip')
        exec_basic(ssh, 'rm master.zip')
        exec_basic(ssh, 'sudo python3 nm-daemon-master/server.py')
        exec_basic(ssh, 'ps aux | grep python')
    else:
        print("do noting")

def config_users(server, ssh):
    users = []
    db_conn = sqlite3.connect(db_path)
    db = db_conn.cursor()
    for row in db.execute("SELECT shares.user_id, users.public_key FROM shares INNER JOIN users ON shares.user_id = users.user_id WHERE shares.server_address=?", [server['address']]):
        users.append({"user_id":row[0], "public_key":row[1]})


    exec_basic(ssh, 'sudo sqlite3 /home/centos/nm.db "DELETE FROM users"')
    for user in users:
        exec_basic(ssh, 'sudo sqlite3 /home/centos/nm.db "INSERT INTO users (user_id, public_key) VALUES(\'' + user['user_id'] + '\', \'' + user['public_key'] + '\')"')

    db_conn.close()

# If we're running in stand alone mode, run the application
if __name__ == '__main__':

    while True:

        servers = get_servers_list()

        for server in servers:
            ssh = server_connect(server)
            #install_requirements(ssh)
            #list_packages(ssh)
            install_api(ssh)
            config_users(server, ssh)
            ssh.close()
        # Wait before the next check
        sleep(10)
