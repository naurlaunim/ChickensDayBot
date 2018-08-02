import os
from ftplib import FTP
import io
import pickle
import random
import psycopg2

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

after_number = int(config['TIMEOUTS']['After_Number']) # The number of messages after which there will be chicken.
to_number = int(config['TIMEOUTS']['To_Number']) # The number of messages to which there will be no chicken.
timer = int(config['TIMEOUTS']['Timer']) # The time interval between regular chickens (not chickens for activity). (seconds)

def connect_to_ftp():
    ftp.connect(config['FTP']['FTP'])
    ftp.login(user=config['FTP']['FTP_User'],
              passwd=config['FTP']['FTP_Password'])
    ftp.cwd(config['FTP']['FTP_Directory'])


usingDB = False
usingFTP = False
if 'Database' in config['DATABASE']:
    usingDB = True
    database = config['DATABASE']['Database']
    user = config['DATABASE']['DB_user']
    password = config['DATABASE']['DB_password']
    host = config['DATABASE']['DB_host']
    port = config['DATABASE']['DB_port']

elif ('FTP' in config['FTP']):
    usingFTP = True
    
    ftp = FTP(config['FTP']['FTP'])
    connect_to_ftp()
elif ('Path' in config['DEFAULT']):
    path = config['DEFAULT']['Path']


token = config['DEFAULT']['Token']


def getconnection():
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()
    return (conn, cur)


def getfiles():
    if usingDB:
        (conn, cur) = getconnection()
        cur.execute("SELECT name FROM Chickens ")
        files = cur.fetchall()
        conn.close()
        return [e[0] for e in files]
    if usingFTP:
        y = ftp.nlst('.')
        return [e for e in y if e not in ('.', '..')]

    return os.listdir(path)

def file_to_send(files):
    file = files.pop(random.choice(range(len(files))))
    return open_file(file)

def open_file(file):
    if usingDB:
        (conn, cur) = getconnection()
        cur.execute("SELECT picture FROM Chickens WHERE name = %s", (file,))
        file_data = cur.fetchone()[0]
        conn.close()
        return file_data
    if usingFTP:
        connect_to_ftp()
        bio = io.BytesIO()
        ftp.retrbinary("RETR %s" % file, bio.write)
        bio.name = file
        bio.seek(0)
        return bio
    return open(os.path.join(path, file), 'rb')


def get_chats():
    if usingDB:
        (conn, cur) = getconnection()
        cur.execute("SELECT data FROM Chats WHERE List = 1")
        data = cur.fetchone()[0]
        conn.close()
        try:
            chats = pickle.loads(data)
        except:
            chats = set()
        return chats

    try:
        f = open('chats.txt', 'rb')
        chats = pickle.load(f)
        f.close()
    except FileNotFoundError:
        chats = set()
    return chats

def add_chat(chat_id):
    chats = get_chats()
    chats.add(chat_id)
    save_chats(chats)

def save_chats(chats):
    if usingDB:
        (conn, cur) = getconnection()
        data = pickle.dumps(chats)
        cur.execute("UPDATE Chats SET data = %s WHERE list = 1", (data,))
        conn.commit()
        conn.close()
    else:
        f = open('chats.txt', 'wb')
        pickle.dump(chats, f)
        f.close()

def del_chat(chat_id):
    chats = get_chats()
    chats.discard(chat_id)
    save_chats(chats)


