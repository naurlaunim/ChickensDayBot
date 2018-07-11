import os

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
path = config['DEFAULT']['Path']
token = config['DEFAULT']['Token']


def getfiles():
    y = os.listdir(path)
    return set(y)

def file_to_send_path(files):
    file = files.pop()
    return os.path.join(path, file)




