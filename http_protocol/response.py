
__all__ = ['Response']


class Response:
    def __init__(self, body, status=200, reason='OK', headers=None):
        self.status = status
        self.reason = reason
        self._headers = headers
        self.body = body

    @property
    def headers(self):

        headers = f'HTTP/1.1 {self.status} {self.reason}\r\n'
        headers += 'Content-Type:text/html; charset=utf-8\r\n'
        headers += f'Content-Length: {len(self.body)}'

        if self._headers is not None:
            for key, value in self._headers.items():
                headers += f'{key}: {value}\r\n'

        headers += 'Connection: close\r\n'
        headers += '\r\n'

        return headers.encode('iso-8859-1')

    def render(self):
        """
        Генерация HTTP сообщения из Response

        :return: Сообщение в формате HTTP
        """

        # headers
        message = self.headers

        # body
        if self.body is not None:
            message += self.body

        return message
