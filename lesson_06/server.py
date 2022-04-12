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
import logging
import log.server_log_config

SERVER_LOGGER = logging.getLogger('server')


def handle_client_message(msg):
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {msg}')
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        SERVER_LOGGER.debug(f'Обработка сообщения УСПЕШНА, отправляю ответ: "RESPONSE: 200"')
        return {RESPONSE: 200}
    SERVER_LOGGER.info(f'Обработка сообщения ПРОВАЛЕНА, отправляю ответ: "RESPONSE: 400"')
    SERVER_LOGGER.info(f'Содержимое неправильного запроса:\n{msg}')
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


def main():
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind(handle_parameters(ip='ANY', port=DEF_PORT))  # (по умолчанию слушает все доступные адреса).
    SERVER_LOGGER.info(f'Сервер запущен')
    serv_sock.listen(1)
    try:
        while True:
            SERVER_LOGGER.info(f'Ожидаю сообщение')
            # print('Слушаю...')
            client_sock, addr = serv_sock.accept()
            SERVER_LOGGER.info(f'Получено сообщение от: {addr}')
            msg = get_message(client_sock)
            SERVER_LOGGER.info(f'Содержимое сообщения: {msg}')
            answer = handle_client_message(msg)
            SERVER_LOGGER.info(f'Отправляю ответ: {answer}| Адрес: {addr}')
            send_message(client_sock, answer)
    finally:
        serv_sock.close()


if __name__ == '__main__':
    main()



