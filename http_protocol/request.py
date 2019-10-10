from collections import namedtuple
from email.parser import Parser

from .exceptions import HTTPError, RequestError


__all__ = ['Request', 'parse_http_request']


MAX_LINE = 64*1024
MAX_HEADERS = 100

METHODS = ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'TRACE', 'CONNECT')


Request = namedtuple('Request', ('method', 'target', 'version', 'cookies', 'headers', 'body'))


def parse_http_request(req_file):
    """
    Составляет Request из raw_data

    :param req_file: file-like object, ассоциорованный с сокетом,
    в бинарном виде
    :return: Request
    """

    method, target, ver = _parse_request_line(req_file)
    headers = _parse_headers(req_file)

    host = headers.get('Host')
    if not host:
        raise HTTPError(400, 'Bad request', 'Host header is missing')

    try:
        size = int(headers.get('Content-Length'))
    except TypeError:
        body = None
    else:
        body = req_file.read(size)

    cookies = _get_cookie(headers)

    return Request(method, target, ver, cookies, headers, body)


def _parse_request_line(req_file):
    """
    Вспомогательный метод для разбора стартовой строки

    :param req_file: file-like object, ассоциорованный с сокетом,
    в бинарном виде
    :return: method, target, ver
    """

    raw_line = req_file.readline(MAX_LINE + 1)

    if len(raw_line) > MAX_LINE:
        raise HTTPError(400, 'Bad request', 'Request line is too long')

    req_line = raw_line.decode('iso-8859-1')
    words = req_line.split()

    if len(words) != 3:
        raise RequestError('Unsupported format')

    method, target, ver = words

    if method not in METHODS:
        raise RequestError('Unsupported format')

    if ver.startswith('HTTP/'):
        if ver != 'HTTP/1.1':
            raise HTTPError(505, 'HTTP Version Not Supported', 'Server supported only HTTP/1.1')
    else:
        raise RequestError('Unsupported format')

    return method, target, ver


def _parse_headers(req_file):
    """
    Вспомогательный метод для разбора Headers

    :param req_file: file-like object, ассоциорованный с сокетом,
    в бинарном виде
    :return: email.message.Message object
    """

    headers = []
    while True:
        line = req_file.readline(MAX_LINE + 1)
        if len(line) > MAX_LINE:
            raise HTTPError(494, 'Request header too large', f'Request header large then max value {MAX_LINE}')

        if line in (b'\r\n', b'\n', b''):
            break

        headers.append(line)
        if len(headers) > MAX_HEADERS:
            raise HTTPError(431, 'Too many headers', f'Server supported max {MAX_HEADERS} headers')

    # Используется встроенный email парсер
    one_str_headers = b''.join(headers).decode('iso-8859-1')
    return Parser().parsestr(one_str_headers)


def _get_cookie(headers):
    """
    Вспомогательный метод для парсинга Cookies

    :param headers: email.message.Message object
    :return: dict() or None
    """

    cookie = headers.get('cookie')

    if cookie is not None:
        cookies_dict = {}
        cookies_list = cookie.split('; ')
        for item in cookies_list:
            key, value = item.split('=')
            cookies_dict[key] = value

        return cookies_dict
    else:
        return None
