import json
import sys

from common.globals import ENCODING, MAX_PACKAGE_LENGTH, DEF_IP, DEF_PORT


def get_message(sender_sock):
    encoded_data = sender_sock.recv(MAX_PACKAGE_LENGTH)
    str_response = encoded_data.decode(ENCODING) if isinstance(encoded_data, bytes) else ValueError
    response = json.loads(str_response) if isinstance(str_response, str) else ValueError
    print(f"+ Получено сообщение: '{response}'\n+ Отправлено клиентом: {sender_sock})")
    # print(f'{str_response=}')
    # print(f'{response=}')
    # print(f'{type(response)=}')
    return response if isinstance(response, dict) else ValueError


def send_message(receiver_sock, message):
    print(f'- Отправляю сообщение: {message}')
    receiver_sock.send(json.dumps(message).encode(ENCODING))


def handle_parameters(ip: str, port: int):
    argv = sys.argv
    if len(argv) > 1:
        print(f'Получены внешние параметры: ', end='')
        for i, parameter in enumerate(argv):
            # Получение и проверка IP
            if parameter == '-a':
                p_addr = argv[i + 1]
                p_list = p_addr.split('.')
                if len(p_list) == 4 and all(p.isdecimal() and int(p) in range(0, 255) for p in p_list):
                    ip = p_addr
                    print(f'IP={p_addr} ', end='')
                else:
                    print(f'ОШИБКА -> (IP={p_addr}) ', end='')
            # Получение и проверка PORT
            if parameter == '-p':
                p_port = argv[i + 1]
                if p_port.isdecimal() and 1024 < int(p_port) < 65535:
                    port = p_port
                    print(f'PORT={p_port} ', end='')
                else:
                    print(f'ОШИБКА -> (PORT={p_port}) ', end='')

    else:
        print(f'Параметры не указаны. ', end='')
    print(f'| Использую: IP={ip} PORT={port}')
    return ip, int(port)