import sys
import logging
import inspect

if sys.argv[0].find('client.py') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):

    def decor(*args, **kwargs):
        result = func(*args, **kwargs)
        # s = '\\'
        # LOGGER.debug(f'Функция: "{func.__module__}/{func.__name__}({args} {kwargs})" '
        #              f'вызвана "{inspect.getmodule(inspect.stack()[1][0]).__file__.rpartition(s)[-1]}'
        #              f'/{inspect.getouterframes(inspect.currentframe())[1][3]}"; Результат: "{str(result)}"')
        # print(inspect.getmodule(inspect.stack()[1][0]).__file__.rpartition('\\')[-1])
        return result
    decor.log = LOGGER
    return decor
