"""
1. На клиентской стороне реализовать прием и отправку сообщений с помощью потоков в P2P-формате
(обмен сообщениями между двумя пользователями).
Итогом выполнения домашних заданий первой части продвинутого курса Python стал консольный мессенджер.

Усовершенствуем его во второй части: реализуем взаимосвязь мессенджера с базами данных
и создадим для него графический пользовательский интерфейс.
"""
# SERVER
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.globals import DEF_PORT, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, SENDER, DESTINATION, \
    RESPONSE, ERROR, EXIT, ONLINE, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message, handle_parameters
from time import time
import logging
import select
import log.server_log_config

LOGGER = logging.getLogger('server')


def handle_connection(msg, cli_sock, cli_ip, msg_list, clients, cli_socks):
    LOGGER.debug(f'Проверка типа сообщения: {msg}')
    # Запрос подключения
    if ACTION in msg and TIME in msg and USER in msg:
        cli_name = msg[USER][ACCOUNT_NAME]
        if msg[ACTION] == PRESENCE:
            if cli_name in clients.keys():
                send_message(cli_sock, {
                    RESPONSE: 400,
                    ERROR: 'Имя занято'})
                cli_socks.remove(cli_sock)
                cli_sock.close()
            else:
                clients[cli_name] = cli_sock
                LOGGER.info(f'Подключился: {cli_ip} {cli_name}')
                send_message(cli_sock, {RESPONSE: 200})
            return
    # Запрос списка пользователей
        elif msg[ACTION] == ONLINE:
            LOGGER.info(f'Получен запрос списка собеседников от: {cli_ip} {cli_name}')
            send_message(clients[cli_name], {
                ACTION: MESSAGE,
                TIME: time(),
                SENDER: 'SERVER',
                DESTINATION: cli_name,
                MESSAGE_TEXT: f'{" ".join(clients.keys())}'})
            return
    # Сообщение
    elif ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and \
            SENDER in msg and DESTINATION in msg and MESSAGE_TEXT in msg:
        msg_list.append(msg)
        LOGGER.debug(f'Сообщение типа MESSAGE добавлено в обработку: {msg[MESSAGE_TEXT]}')
        return
    # Отключение
    elif ACTION in msg and msg[ACTION] == EXIT and ACCOUNT_NAME in msg:
        LOGGER.info(f'Отключился: {cli_ip} {msg[ACCOUNT_NAME]}')
        del_sock(clients[msg[ACCOUNT_NAME]], cli_socks)
        del clients[msg[ACCOUNT_NAME]]
        return
    # Ошибки
    else:
        LOGGER.error(f'Ошибка: Не удается обработать запрос:\n{msg}')
        send_message(cli_sock, {
            RESPONSE: 400,
            ERROR: 'Bad request'})
        return


def handle_message(msg, clients, cli_socks):
    dest_cli, send_cli = msg[DESTINATION], msg[SENDER]
    LOGGER.debug(f'{dest_cli=} {send_cli=}')
    if dest_cli == '':
        for every_cli in cli_socks:
            LOGGER.debug(f'Отправляю сообщение ВСЕМ: {msg}')
            send_message(every_cli, msg)
        LOGGER.info(f'{send_cli}: {msg}')
    elif dest_cli in clients and clients[dest_cli] in cli_socks:
            LOGGER.debug(f'Отправляю сообщение {dest_cli}: {msg}')
            send_message(clients[dest_cli], msg)
            LOGGER.info(f'{send_cli} => {dest_cli}: {msg}')
    elif dest_cli in clients and clients[dest_cli] not in cli_socks:
        LOGGER.error(f'Ошибка: {dest_cli} Пропал вслед за кораблем')
        raise ConnectionError
    else:
        # LOGGER.debug(f'Отправляю {send_cli} сообщение: Пользователь {dest_cli} не найден, неудалось доставить: {msg}')
        send_message(clients[send_cli], {
            ACTION: MESSAGE,
            TIME: time(),
            SENDER: 'SERVER',
            DESTINATION: send_cli,
            MESSAGE_TEXT: f'Пользователь {dest_cli} не найден, неудалось доставить: {msg[MESSAGE_TEXT]}'})
        LOGGER.debug(f'Пользователь {dest_cli} не найден, неудалось доставить: {send_cli} => {dest_cli}: '
                     f'{msg[MESSAGE_TEXT]}')


def del_sock(sock, sock_list):
    sock.close()
    sock_list.remove(sock)


def main():
    listen_address, listen_port, _ = handle_parameters(ip='', port=DEF_PORT)
    LOGGER.info(f'Сервер запущен. Слушаю IP:{listen_address if listen_address else "ANY"} '
                f'PORT:{listen_port}')

    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serv_sock.bind((listen_address, listen_port))
    serv_sock.settimeout(0.5)
    cli_socks = []
    clients = {}
    msgs = []
    client_address = ''

    serv_sock.listen(MAX_CONNECTIONS)
    try:
        while True:
            try:
                client_sock, client_address = serv_sock.accept()
            except OSError:
                pass
            else:
                LOGGER.debug(f'Подключение: {client_address}')
                cli_socks.append(client_sock)

            recv_data_list = []
            send_data_list = []
            try:
                if cli_socks:
                    recv_data_list, send_data_list, _ = select.select(cli_socks, cli_socks, [], 0)
            except OSError:
                pass

            if recv_data_list:
                for client_with_msg in recv_data_list:
                    try:
                        recvd_msg = get_message(client_with_msg)
                        if recvd_msg:
                            handle_connection(recvd_msg, client_with_msg, client_address, msgs, clients, cli_socks)
                        else:
                            LOGGER.info(f'{client_with_msg.getpeername()} отключился')
                            # del_sock(client_with_msg, cli_socks)
                            cli_socks.remove(client_with_msg)
                            del clients[client_with_msg.getpeername()]
                    except:
                        LOGGER.info(f'{client_with_msg.getpeername()} отключился')
                        # del_sock(client_with_msg, cli_socks)
                        cli_socks.remove(client_with_msg)
                        del clients[client_with_msg.getpeername()]

            for m in msgs:
                try:
                    handle_message(m, clients, send_data_list)
                except:
                    LOGGER.info(f'{m[DESTINATION]} отключился от сервера.')
                    del_sock(clients[m[DESTINATION]], cli_socks)
                    del clients[m[DESTINATION]]
            msgs.clear()

    except KeyboardInterrupt:
        LOGGER.info(f'Завершение работы, отключаю {len(cli_socks)} клиентов...')
        for client in cli_socks:
            del_sock(client, cli_socks)
        serv_sock.close()
        LOGGER.info(f'Сервер остановлен')


if __name__ == '__main__':
    main()
