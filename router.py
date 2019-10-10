routes = dict()


def route(url=None, methods=('GET',)):

    def decorator(func):
        global routes

        path = url.strip('/')
        try:
            action, rule = path.split('/', 1)
        except ValueError:
            action = path
            rule = None

        routes[action] = {method: (rule, func) for method in methods}

    return decorator
