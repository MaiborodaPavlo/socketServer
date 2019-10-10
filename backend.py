from urllib.parse import urlparse
import re

import config
from http_protocol.response import Response
from http_protocol.exceptions import HTTPError

from router import routes, route
import view


__all__ = ['run']

AVAILABLE_METHODS = ('GET', 'POST')


def run(request):
    """
    Основной метод, отвечает за роутинг

    :param request: Request
    :return: Response
    """

    url = urlparse(request.target).path.strip('/')
    try:
        action, params_str = url.split('/', 1)
    except ValueError:
        action = url
        params_str = None

    if request.method not in AVAILABLE_METHODS:
        # Ответ в случае использования не GET/POST метода
        body = view.default_page(f'{request.method} не поддерживается, только GET/POST')
        return Response(body, status=405, reason='Method Not Allowed')

    if action in routes.keys():

        try:
            rule, func = routes[action][request.method]
        except KeyError:
            raise HTTPError(405, 'Method Not Allowed', 'Method not allowed for this url')

        # запрос без параметров
        if params_str is None and rule is None:
            return func()

        # запрос с параметрами
        elif rule is not None and params_str is not None:
            params = _get_params(rule, params_str)

            if params is not None:
                return func(*params)
            else:
                raise HTTPError(406, 'Not Acceptable', 'Incorrect parameters in request')
        else:
            raise HTTPError(406, 'Not Acceptable', 'Incorrect URL')

    else:
        # Все прочие GET/POST запросы на любые другие url отдают HTTP ошибку.
        raise HTTPError(404, 'Not Found', 'Not Found: Incorrect Method/URL')


def _get_params(rule, params_str):
    """
    Вспомогательный метод, парсит параметры из запроса,
    если они есть
    """

    rule = rule.strip('<>')

    if rule.startswith('re:'):
        _, pattern = rule.split(':', 1)
        match = re.match(pattern, params_str)
        if match:
            return match.groups()
        else:
            # None
            return match
    else:
        return params_str


@route('/div/<re:(?P<a>\d*\.?\d*)/to/(?P<b>\d*\.?\d*)$>')
def route_div(a, b):
    """
    Обработка GET запроса /div/<любозначение1>/to/<любозначение2>
    """

    try:
        result = float(a)/float(b)
    except (ZeroDivisionError, ValueError):
        message = f'Не удается разделить {a} на {b}, введите корректные данные'
    else:
        message = f'Результат деления {a} на {b}: {result}'

    body = view.default_page(message)
    return Response(body)


@route('/show_errors/<re:^(?P<value>[0,1])$>', methods=('POST',))
def route_show_errors(value):
    """
    Обработка POST запроса /show_errors
    """
    config.update_setting(config.PATH, 'Settings', 'show_errors', value)
    message = f'Свойство show_errors в значение {value} установлено'
    body = view.default_page(message)
    return Response(body)


@route('/short_log/<re:^(?P<value>[0,1])$>', methods=('POST', 'GET'))
def route_short_log(value):
    """
    Обработка POST запросоа /short_log
    """

    config.update_setting(config.PATH, 'Settings', 'short_log', value)
    message = f'Свойство short_log в значение {value} установлено'
    body = view.default_page(message)
    return Response(body)


@route('/set_cookie/<re:^(?P<key>[\w\d]*)=(?P<value>[\w\d]*)$>')
def route_set_cookie(key, value):
    """
    Обработка GET запроса /set_cookie/=
    """

    if key == 'bg_color':
        set_bg_color(value)

    message = f'Cookie {key}={value} установлено'
    body = view.default_page(message)
    return Response(body, headers={'Set-Cookie': f'{key}={value}; Path=/'})


def set_bg_color(color):
    """
    Установка значения bg_color
    """

    config.update_setting(config.PATH, 'Settings', 'bg_color', color)


@route('/')
def route_main_page():
    """
    Обработка GET запроса на /
    """

    body = view.index_page()
    return Response(body)
