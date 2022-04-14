import json
import os
import sys
import logging


sys.path.append(os.path.join(os.getcwd(), '..'))
from common.globals import ENCODING, MAX_PACKAGE_LENGTH
import log.client_log_config
from log.decorator import log
LOGGER = logging.getLogger('server') if 'server.py' in sys.argv[0] else logging.getLogger('client')


@log
def get_message(sender_sock):
    try:
        encoded_data = sender_sock.recv(MAX_PACKAGE_LENGTH)
    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
        LOGGER.debug(f'Соединение разорвано/потеряно.')
        sys.exit(1)
    if encoded_data:
        str_response, response = None, None
        if isinstance(encoded_data, bytes):
            str_response = encoded_data.decode(ENCODING)
            if isinstance(str_response, str):
                try:
                    response = json.loads(str_response)
                except json.JSONDecodeError:
                    LOGGER.error(f'Не удалось декодировать полученную Json строку: {str_response}.')
                    sys.exit(1)
                if isinstance(response, dict):
                    return response
                else:
                    LOGGER.error(f'ОШИБКА сообщение: "{response}" не является DICT')
            else:
                LOGGER.error(f'ОШИБКА сообщение: "{str_response}" не является STR')
        else:
            LOGGER.error(f'ОШИБКА сообщение: "{str_response}" не декодируется как {bytes}')
        sender_sock.close()
        ValueError()


@log
def send_message(receiver_sock, message):
    if not isinstance(message, dict):
        LOGGER.error(f'ОШИБКА сообщение "{message}" не является DICT')
        raise TypeError
    LOGGER.debug(f'Отправляю сообщение: {message}')
    receiver_sock.send(json.dumps(message).encode(ENCODING))


@log
def is_ip_bad(ip: str):
    if not isinstance(ip, str):
        LOGGER.error(f'ОШИБКА: Полученный IP: {ip} не является STR')
        ValueError()
    if ip == 'ANY': return False
    ip_list = ip.split('.')
    return len(ip_list) != 4 or any(not n.isdecimal() or int(n) not in range(0, 255) for n in ip_list)


@log
def is_port_bad(port):
    if isinstance(port, int):
        return not 1024 < port < 65535
    if isinstance(port, str):
        return not 1024 < int(port) < 65535
    LOGGER.error(f'Полученный PORT: {port} за пределами 1024-65535')
    ValueError()

@log
def is_mode_bad(mode: str):
    if not isinstance(mode, str):
        LOGGER.error(f'ОШИБКА: Полученный режим MODE: {mode} не является STR')
        ValueError()
    if mode == 'listen' or mode == 'send':
        return False
    return True


@log
def handle_parameters(ip: str, port: int, mode: str):
    argv = sys.argv
    bad_ip, bad_port, bad_mode, result_ip, result_port, result_mode = True, True, True, None, None, None
    if len(argv) > 1:
        for i, parameter in enumerate(argv):
            # Получение и проверка IP
            if parameter == '-a':
                result_ip = argv[i + 1]
                bad_ip = is_ip_bad(result_ip)
                if bad_ip:
                    LOGGER.error(f'ОШИБКА параметра запуска -> (IP={result_ip})')
            # Получение и проверка PORT
            if parameter == '-p':
                result_port = argv[i + 1]
                bad_port = is_port_bad(result_port)
                if bad_port:
                    LOGGER.error(f'ОШИБКА параметра запуска -> (PORT={result_port})')
            # Получение и проверка MODE
            if parameter == '-m':
                result_mode = argv[i + 1]
                bad_mode = is_mode_bad(result_mode)
                if bad_mode:
                    LOGGER.error(f'ОШИБКА параметра запуска -> (MODE={result_mode}) Ожидается: -m listen или -m send')
    else:
        LOGGER.info(f'Параметры запуска не указаны')
    if bad_ip:
        if is_ip_bad(ip):
            LOGGER.error(f'ОШИБКА параметра переданного в ф-ю -> (IP={ip})')
            raise ValueError
        result_ip = ('' if ip == 'ANY' else ip)
    if bad_port:
        if is_port_bad(port):
            LOGGER.error(f'ОШИБКА параметра переданного в ф-ю -> (PORT={port})')
            raise ValueError
        result_port = port
    if bad_mode:
        if is_mode_bad(mode):
            LOGGER.error(f'ОШИБКА параметра переданного в ф-ю -> (MODE={mode}) Ожидается: listen или send')
            raise ValueError
        result_mode = mode
    LOGGER.debug(f'Использую: IP={result_ip if result_ip else "любой"} PORT={result_port} MODE={result_mode}')
    return result_ip, result_port, result_mode
