import json
import os
import sys
import logging


sys.path.append(os.path.join(os.getcwd(), '..'))
from common.globals import ENCODING, MAX_PACKAGE_LENGTH
import log.client_log_config
# import log.decorator
from log.decorator import log


@log
def get_message(sender_sock):
    LOGGER = get_message.log
    encoded_data = sender_sock.recv(MAX_PACKAGE_LENGTH)
    str_response, response = None, None
    if isinstance(encoded_data, bytes):
        str_response = encoded_data.decode(ENCODING)
        LOGGER.debug(f'декодировано')
    else:
        LOGGER.error(f'{str_response.__name__}: {str_response} не является {ENCODING}')
        ValueError()
    if isinstance(str_response, str):
        response = json.loads(str_response)
        LOGGER.debug(f'распаковано')
    else:
        LOGGER.error(f'{str_response.__name__}: {str_response} не является STR')
        ValueError()
    if isinstance(response, dict):
        LOGGER.debug(f'успех')
        return response
    else:
        LOGGER.error(f'{response.__name__}: {response} не является DICT')
        ValueError()


@log
def send_message(receiver_sock, message):
    LOGGER = send_message.log
    if not isinstance(message, dict):
        LOGGER.error(f'{message.__name__}: {message} не является DICT')
        raise TypeError
    # LOGGER.info(f'Отправляю сообщение: {message}')
    receiver_sock.send(json.dumps(message).encode(ENCODING))


@log
def is_ip_bad(ip: str):
    LOGGER = is_ip_bad.log
    if not isinstance(ip, str):
        LOGGER.error(f'Полученный IP: {ip} не является STR')
        ValueError()
    if ip == 'ANY': return False
    ip_list = ip.split('.')
    return len(ip_list) != 4 or any(not n.isdecimal() or int(n) not in range(0, 255) for n in ip_list)


@log
def is_port_bad(port):
    LOGGER = is_port_bad.log
    if isinstance(port, int):
        # print(f'IS INT {1024 < port < 65535=}')
        return not 1024 < port < 65535
    if isinstance(port, str):
        # print(f'IS STR {1024 < int(port) < 65535=}')
        return not 1024 < int(port) < 65535
    LOGGER.error(f'Полученный PORT: {port} за пределами 1024-65535')
    ValueError()


@log
def handle_parameters(ip: str, port: int):
    LOGGER = handle_parameters.log
    argv = sys.argv
    bad_ip, bad_port, result_ip, result_port = True, True, None, None
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
    else:
        LOGGER.info(f'Параметры запуска не указаны')
        # print(f'Параметры запуска не указаны.', end='')
    if bad_ip:
        if is_ip_bad(ip):
            LOGGER.error(f'ОШИБКА параметра переданного в ф-ю -> (IP={ip})')
            # print(f' | ОШИБКА параметра переданного в ф-ю -> (IP={ip}) ', end='')
            raise ValueError
        result_ip = ('' if ip == 'ANY' else ip)
    if bad_port:
        if is_port_bad(port):
            LOGGER.error(f'ОШИБКА параметра переданного в ф-ю -> (PORT={port})')
            # print(f' | ОШИБКА параметра переданного в ф-ю -> (PORT={port}) ', end='')
            raise ValueError
        result_port = port
    LOGGER.info(f'Использую: IP={result_ip} PORT={result_port}')
    # print(f'| Использую: IP={result_ip} PORT={result_port}', end='')
    return result_ip, result_port
