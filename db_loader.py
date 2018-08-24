import psycopg2
from ftplib import FTP
import io
import configparser
import sys

config = configparser.ConfigParser()
config.read('config.ini')

database = config['DATABASE']['Database']
user = config['DATABASE']['DB_user']
password = config['DATABASE']['DB_password']
host = config['DATABASE']['DB_host']
port = config['DATABASE']['DB_port']

ftp = FTP(config['FTP']['FTP'])

conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
print('connected to database')

def connect_to_ftp():
    print(sys._getframe().f_code.co_name)
    ftp.connect(config['FTP']['FTP'])
    ftp.login(user=config['FTP']['FTP_User'],
              passwd=config['FTP']['FTP_Password'])
    ftp.cwd(config['FTP']['FTP_Directory'])

def getfiles():
    print(sys._getframe().f_code.co_name)
    y = ftp.nlst('.')
    return [e for e in y if e not in ('.', '..')]

def open_file(file):
    connect_to_ftp()
    bio = io.BytesIO()
    ftp.retrbinary("RETR %s" % file, bio.write)
    bio.name = file
    bio.seek(0)
    return bio


def create():
    print(sys._getframe().f_code.co_name)
    cur = conn.cursor()

    cur.execute("CREATE TABLE Chickens(Id SERIAL PRIMARY KEY, name VARCHAR, picture BYTEA NOT NULL)")
    cur.execute("CREATE TABLE Chats(list INT NOT NULL PRIMARY KEY, data BYTEA)")
    cur.execute("INSERT INTO Chats (list) VALUES (1)")

    conn.commit()


def store(file, name):
    print(sys._getframe().f_code.co_name)
    cur = conn.cursor()

    # f = open(path, 'rb')
    filedata = file.read()
    cur.execute("INSERT INTO Chickens(id, name, picture) VALUES (DEFAULT,%s,%s) RETURNING id",
                (name, filedata))
    returned_id = cur.fetchone()[0]
    # f.close()

    conn.commit()
    return returned_id


def fetch(path, name):
    cur = conn.cursor()

    cur.execute("SELECT picture FROM Chickens WHERE name = %s", (name,))
    file_data = cur.fetchone()[0]

    # f = open(os.path.join(path, name), 'wb')
    # f.write(file_data)
    # f.close()
    # conn.commit()
    return file_data

def main():
    connect_to_ftp()

    create()
    files = getfiles()
    for file_name in files:
        file = open_file(file_name)
        store(file, file_name)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()


