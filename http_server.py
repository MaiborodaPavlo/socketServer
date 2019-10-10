import socket

import config
import backend
from http_protocol.response import Response
from http_protocol.request import parse_http_request
from http_protocol.exceptions import HTTPError, RequestError

from loggers import access_logger, errors_logger


__all__ = ['start']


def start(host, port):

    with create_sock(host, port) as sock:
        while True:
            conn, _ = sock.accept()

            try:
                serve_client(conn)

            except HTTPError as e:
                send_error(conn, e)
            except RequestError:
                exit(1)
            # Тут есть сомнения
            except ConnectionError:
                continue


def create_sock(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind((host, int(port)))
    except OSError:
        print(f'Error: {host}:{port} Address already in use')
        exit(1)

    print(f'Server started at {host}:{port}')

    sock.listen()

    return sock


@errors_logger
def serve_client(conn):
    """
    Логика работы сервера
    """

    # 1. Парсим http запрос
    request = process_request(conn)

    # 2. Получаем ответ
    response = backend.run(request)

    # 3. Составляем http ответ и отправляем
    process_response(conn, response)


@access_logger
def process_request(conn):
    """
    Обработка входящих сообщений, возвращает Request
    """

    req_file = conn.makefile('rb')

    request = parse_http_request(req_file)

    return request


def process_response(conn, resp):
    """
    Отправка Response
    """

    resp_file = conn.makefile('wb')

    resp_msg = resp.render()
    resp_file.write(resp_msg)

    resp_file.flush()
    resp_file.close()


def send_error(conn, err):
    """
    Отправка ошибки
    """

    show_errors = int(config.get_setting(config.PATH, 'Settings', 'show_errors'))

    if show_errors:
        body = err.body.encode('utf-8')
    else:
        body = 'Error'.encode('utf-8')

    resp = Response(body, status=err.status, reason=err.reason)

    process_response(conn, resp)






