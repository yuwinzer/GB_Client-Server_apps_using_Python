"""
1. Реализовать обработку нескольких клиентов на сервере, используя функцию select.
 Клиенты должны общаться в «общем чате»: каждое сообщение участника отправляется всем, подключенным к серверу.
2. Реализовать функции отправки/приема данных на стороне клиента.
 Чтобы упростить разработку на данном этапе, пусть клиентское приложение будет либо только принимать,
  либо только отправлять сообщения в общий чат. Эти функции надо реализовать в рамках отдельных скриптов.
"""
# SERVER
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.globals import DEF_PORT, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, SENDER,\
    RESPONSE, ERROR, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message, handle_parameters
from time import time
import logging
import select
import log.server_log_config

SERVER_LOGGER = logging.getLogger('server')


def handle_client_message(msg, msg_list, client_sock):
    SERVER_LOGGER.debug(f'Обработка сообщения от клиента: {msg}')
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        SERVER_LOGGER.debug(f'Обработка сообщения УСПЕШНА, отправляю ответ: "RESPONSE: 200"')
        send_message(client_sock, {RESPONSE: 200})
        return
    elif ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and MESSAGE_TEXT in msg:
        SERVER_LOGGER.debug(f'Обработка сообщения УСПЕШНА, отправляю: {ACCOUNT_NAME} ответ: "{MESSAGE_TEXT}"')
        msg_list.append((msg[ACCOUNT_NAME], msg[MESSAGE_TEXT]))
        return
    else:
        SERVER_LOGGER.error(f'Обработка сообщения ПРОВАЛЕНА, отправляю ответ: "RESPONSE: 400"\n'
                            f'Содержимое неправильного запроса:\n{msg}')
        send_message(client_sock, {
            RESPONSE: 400,
            ERROR: 'Bad request'})
        return


def del_sock(sock, sock_list):
    sock.close()
    sock_list.remove(sock)


def main():
    listen_address, listen_port, _ = handle_parameters(ip='ANY', port=DEF_PORT, mode='listen')
    SERVER_LOGGER.info(f'Сервер запущен. Слушаю IP:{listen_address if listen_address else "любой"} '
                       f'PORT:{listen_port}')

    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind((listen_address, listen_port))
    serv_sock.settimeout(0.5)
    clients = []
    msgs = []

    serv_sock.listen(MAX_CONNECTIONS)
    try:
        while True:
            try:
                client_sock, client_address = serv_sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.debug(f'Подключен: {client_address}')
                clients.append(client_sock)

            recv_data_list = []
            send_data_list = []
            try:
                if clients:
                    recv_data_list, send_data_list, _ = select.select(clients, clients, [], 0)
            except OSError:
                pass

            if recv_data_list:
                for client_with_msg in recv_data_list:
                    try:
                        recvd_msg = get_message(client_with_msg)
                        handle_client_message(recvd_msg, msgs, client_with_msg)
                        if recvd_msg.get("action") == 'msg':
                            _user = recvd_msg.get("account_name")
                            _msg = recvd_msg.get("msg_text")
                        else:
                            _user = recvd_msg.get("user").get("account_name")
                            _msg = 'подключился'
                        SERVER_LOGGER.info(f'{client_with_msg.getpeername()} '
                                           f'{_user}: {_msg}')
                    except:
                        SERVER_LOGGER.info(f'{client_with_msg.getpeername()}'
                                           f' отключился от сервера.')
                        del_sock(client_with_msg, clients)

            if msgs and send_data_list:
                msg = {
                    ACTION: MESSAGE,
                    SENDER: msgs[0][0],
                    TIME: time(),
                    MESSAGE_TEXT: msgs[0][1]
                }
                del msgs[0]
                for waiting_client in send_data_list:
                    try:
                        send_message(waiting_client, msg)
                    except:
                        SERVER_LOGGER.info(f'{waiting_client.getpeername()} отключился от сервера.')
                        del_sock(waiting_client, clients)
    except KeyboardInterrupt:
        SERVER_LOGGER.info(f'Завершение работы, отключаю {len(clients)} клиентов...')
        for client in clients:
            del_sock(client, clients)
        serv_sock.close()
        SERVER_LOGGER.info(f'Сервер остановлен')


if __name__ == '__main__':
    main()
