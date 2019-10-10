import argparse

import config
import http_server


parser = argparse.ArgumentParser(description='Конфигурация работы сервера')
parser.add_argument('--host', help='Укажите адрес хоста')
parser.add_argument('--port', help='Укажите порт хоста')

host = parser.parse_args().host or \
       config.get_setting(config.PATH, 'Connection', 'host')
port = parser.parse_args().port or \
       config.get_setting(config.PATH, 'Connection', 'port')

# start server
http_server.start(host, port)


