import os
from ftplib import FTP
import io

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

usingFTP = False
if ('FTP' in config['DEFAULT']):
    usingFTP = True
    
    ftp = FTP(config['DEFAULT']['FTP'])
    ftp.login(user=config['DEFAULT']['FTP_User'], 
              passwd=config['DEFAULT']['FTP_Password'])
    ftp.cwd(config['DEFAULT']['FTP_Directory'])
elif ('Path' in config['DEFAULT']):
    path = config['DEFAULT']['Path']

token = config['DEFAULT']['Token']


def getfiles():
    if usingFTP:
        y = ftp.nlst('.')
        y = [e for e in y if e not in ('.', '..')]
        return set(y)

    y = os.listdir(path)
    return set(y)

def file_to_send_path(files):
    file = files.pop()
    if usingFTP:
        bio = io.BytesIO()
        ftp.retrbinary("RETR %s" % file, bio.write)
        bio.name = file
        bio.seek(0)
        return bio
    return open(os.path.join(path, file), 'rb')




