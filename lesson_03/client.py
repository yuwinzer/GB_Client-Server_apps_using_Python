"""
1. Реализовать простое клиент-серверное взаимодействие по протоколу JIM (JSON instant messaging):
            клиент отправляет запрос серверу; сервер отвечает соответствующим кодом результата.
 Клиент и сервер должны быть реализованы в виде отдельных скриптов, содержащих соответствующие функции.
Фнкции клиента:
 сформировать presence-сообщение;
 отправить сообщение серверу;
 получить ответ сервера;
 разобрать сообщение сервера;
 параметры командной строки скрипта client.py <addr> [<port>]:
                                     addr — ip-адрес сервера;
                                     port — tcp-порт на сервере, по умолчанию 7777.
Функции сервера:
 принимает сообщение клиента;
 формирует ответ клиенту;
 отправляет ответ клиенту;
 имеет параметры командной строки: -p <port> — TCP-порт для работы (по умолчанию использует 7777);
                                   -a <addr> — IP-адрес для прослушивания (по умолчанию слушает все доступные адреса).
"""
# CLIENT

from time import time
from socket import socket, AF_INET, SOCK_STREAM
from common.globals import ACTION, PRESENCE, RESPONSE, ERROR, TIME, USER, ACCOUNT_NAME, DEF_PORT
from common.utils import send_message, get_message, handle_parameters


def create_presence(acc_name='Guest'):
    return {
        ACTION: PRESENCE,
        TIME: time(),
        USER: {
            ACCOUNT_NAME: acc_name
        }
    }


def handle_answer(msg):
    # print(f'{msg} {type(msg)}')
    if RESPONSE in msg:
        return '200 : OK' if msg[RESPONSE] == 200 else f'400 : {msg[ERROR]}'
    raise ValueError


def main():
    presence_message = create_presence()
    client_sock = socket(AF_INET, SOCK_STREAM)
    ip, port = handle_parameters(ip='', port=DEF_PORT)
    if ip == '':
        print('Параметр -a является обязательным. Напимер: -a 127.0.0.1')
        client_sock.close()
        return
    client_sock.connect((ip, port))
    send_message(client_sock, presence_message)
    server_answer = get_message(client_sock)
    print(handle_answer(server_answer))
    client_sock.close()


main()