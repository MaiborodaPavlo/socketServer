import logging
from functools import wraps

import config


ACCESS_FILE = 'access.log'
ERRORS_FILE = 'error.log'

loggers = {}


def access_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        short_log = int(config.get_setting(config.PATH, 'Settings', 'short_log'))
        logger = get_logger('access_logger', logging.INFO, ACCESS_FILE)

        request = func(*args, **kwargs)

        if int(short_log):
            message = f'[Method: {request.method}, URL: {request.target}, Cookie: {request.cookies}]\n'
        else:
            message = f'[Method: {request.method}, URL: {request.target}, Protocol: {request.version}]\n' + \
                      f'Headers: \n{request.headers}' +\
                      f'Body: {request.body}\n'

        logger.info(message)

        return request
    return wrapper


def errors_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger('errors_logger', logging.ERROR, ERRORS_FILE)
        try:
            return func(*args, **kwargs)
        except Exception:
            # log the exception
            err = f'There was an exception in {func.__name__}'

            logger.exception(err)

            # re-raise the exception
            raise

    return wrapper


# Вспомогательные функции для создания и получения логера

def create_logger(name, level, path):
    global loggers

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create the logging file handler
    fh = logging.FileHandler(path)

    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    loggers[name] = logger
    return logger


def get_logger(name, level, path):
    if loggers.get(name):
        return loggers.get(name)
    else:
        return create_logger(name, level, path)
