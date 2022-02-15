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
# SERVER
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.globals import DEF_PORT, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, DEF_IP_FOR_RESPONSE, ERROR
from common.utils import get_message, send_message, handle_parameters


def handle_client_message(msg):
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        DEF_IP_FOR_RESPONSE: 400,
        ERROR: 'Bad request'
    }


def main():
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind(handle_parameters(ip='', port=DEF_PORT))  # (по умолчанию слушает все доступные адреса).
    serv_sock.listen(1)
    try:
        while True:
            print('Слушаю...')
            client_sock, addr = serv_sock.accept()
            msg = get_message(client_sock)
            answer = handle_client_message(msg)
            send_message(client_sock, answer)
    finally:
        serv_sock.close()


main()


