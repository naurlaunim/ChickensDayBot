import os
from ftplib import FTP
import io
import pickle
import random

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

def connect_to_ftp():
    ftp.connect(config['DEFAULT']['FTP'])
    ftp.login(user=config['DEFAULT']['FTP_User'], 
              passwd=config['DEFAULT']['FTP_Password'])
    ftp.cwd(config['DEFAULT']['FTP_Directory'])


usingFTP = False
if ('FTP' in config['DEFAULT']):
    usingFTP = True
    
    ftp = FTP(config['DEFAULT']['FTP'])
    connect_to_ftp()
elif ('Path' in config['DEFAULT']):
    path = config['DEFAULT']['Path']

token = config['DEFAULT']['Token']

def getfiles():
    if usingFTP:
        y = ftp.nlst('.')
        return [e for e in y if e not in ('.', '..')]

    return os.listdir(path)

def file_to_send_path(files):
    file = random.choice(files)
    if usingFTP:
        connect_to_ftp()
        bio = io.BytesIO()
        ftp.retrbinary("RETR %s" % file, bio.write)
        bio.name = file
        bio.seek(0)
        return bio
    return open(os.path.join(path, file), 'rb')

def get_chats():
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
    f = open('chats.txt', 'wb')
    pickle.dump(chats, f)
    f.close()


