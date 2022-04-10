import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.globals import ENCODING, MAX_PACKAGE_LENGTH


def get_message(sender_sock):
    encoded_data = sender_sock.recv(MAX_PACKAGE_LENGTH)
    str_response = encoded_data.decode(ENCODING) if isinstance(encoded_data, bytes) else ValueError
    response = json.loads(str_response) if isinstance(str_response, str) else ValueError
    return response if isinstance(response, dict) else ValueError


def send_message(receiver_sock, message):
    if not isinstance(message, dict):
        raise TypeError
    receiver_sock.send(json.dumps(message).encode(ENCODING))


def is_ip_bad(ip: str):
    if not isinstance(ip, str):
        ValueError
    ip_list = ip.split('.')
    return len(ip_list) != 4 or any(not n.isdecimal() or int(n) not in range(0, 255) for n in ip_list)


def is_port_bad(port):
    if isinstance(port, int):
        # print(f'IS INT {1024 < port < 65535=}')
        return not 1024 < port < 65535
    if isinstance(port, str):
        # print(f'IS STR {1024 < int(port) < 65535=}')
        return not 1024 < int(port) < 65535
    ValueError


def handle_parameters(ip: str, port: int):
    argv = sys.argv
    bad_ip, bad_port, result_ip, result_port = True, True, None, None
    if len(argv) > 1:
        for i, parameter in enumerate(argv):
            # Получение и проверка IP
            if parameter == '-a':
                result_ip = argv[i + 1]
                bad_ip = is_ip_bad(result_ip)
            # Получение и проверка PORT
            if parameter == '-p':
                result_port = argv[i + 1]
                bad_port = is_port_bad(result_port)
        if bad_ip:
            pass
            # print(f' | ОШИБКА параметра запуска -> (IP={result_ip}) ', end='')
        if bad_port:
            pass
            # print(f' | ОШИБКА параметра запуска -> (PORT={result_port}) ', end='')
        else:
            bad_port = int(bad_port)
    # else:
    #     print(f'Параметры запуска не указаны.', end='')
    if bad_ip:
        if is_ip_bad(ip):
            # print(f' | ОШИБКА параметра переданного в ф-ю -> (IP={ip}) ', end='')
            raise ValueError
        result_ip = ip
    if bad_port:
        if is_port_bad(port):
            # print(f' | ОШИБКА параметра переданного в ф-ю -> (PORT={port}) ', end='')
            raise ValueError
        result_port = port
    # print(f'| Использую: IP={result_ip} PORT={result_port}', end='')
    return result_ip, result_port