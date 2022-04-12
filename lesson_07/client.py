"""
1. Реализовать обработку нескольких клиентов на сервере, используя функцию select.
 Клиенты должны общаться в «общем чате»: каждое сообщение участника отправляется всем, подключенным к серверу.
2. Реализовать функции отправки/приема данных на стороне клиента.
 Чтобы упростить разработку на данном этапе, пусть клиентское приложение будет либо только принимать,
  либо только отправлять сообщения в общий чат. Эти функции надо реализовать в рамках отдельных скриптов.
"""
# CLIENT
import json
import sys
from time import time
from socket import socket, AF_INET, SOCK_STREAM
from common.globals import ACTION, SENDER, PRESENCE, RESPONSE, ERROR, TIME, USER, ACCOUNT_NAME, DEF_PORT, DEF_IP,\
    MESSAGE, MESSAGE_TEXT
from common.utils import send_message, get_message, handle_parameters
from common.errors import ReqFieldMissingError, ServerError
import logging
import log.client_log_config

CLIENT_LOGGER = logging.getLogger('client')


def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
        # CLIENT_LOGGER.debug(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


def create_presence(acc_name='Guest'):
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {acc_name}')
    return {
        ACTION: PRESENCE,
        TIME: time(),
        USER: {
            ACCOUNT_NAME: acc_name
        }
    }


def handle_answer(msg):
    if RESPONSE in msg:
        return '200 : OK' if msg[RESPONSE] == 200 else f'400 : {msg[ERROR]}'
    CLIENT_LOGGER.error(f'Получен неправильный ответ сервера(отсутствует RESPONSE): {msg}')
    raise ValueError


def main():
    serv_ip, serv_port, client_mode = handle_parameters(ip=DEF_IP, port=DEF_PORT, mode='listen')
    CLIENT_LOGGER.info(f'Клиент запущен. Использую SERVER IP:{serv_ip} PORT:{serv_port} MODE:{client_mode}')

    try:
        CLIENT_LOGGER.debug(f'Попытка соедиения...')
        my_sock = socket(AF_INET, SOCK_STREAM)
        my_sock.connect((serv_ip, serv_port))
        CLIENT_LOGGER.debug(f'Отправляю сообщение о присутствии...')
        send_message(my_sock, create_presence())
        CLIENT_LOGGER.debug(f'Жду ответа от сервера...')
        answer = handle_answer(get_message(my_sock))
        CLIENT_LOGGER.info(f'Соединение установлено')
        CLIENT_LOGGER.debug(f'Получен ответ сервера: {answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.error(f'Не удалось подключиться к серверу {serv_ip}:{serv_port}, '
                            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    # except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
    #     CLIENT_LOGGER.error(f'Соединение с сервером {serv_ip} было потеряно.')
    #     sys.exit(1)
    # except KeyboardInterrupt:
    #     CLIENT_LOGGER.info(f'Завершение работы клиента')
    #     my_sock.close()
    #     CLIENT_LOGGER.info(f'Клиент остановлен')
    #     sys.exit(1)
    else:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            if client_mode == 'send':
                try:
                    send_message(my_sock, create_message(my_sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {serv_ip} было потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(my_sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {serv_ip} было потеряно.')
                    sys.exit(1)
    # except KeyboardInterrupt:
    #     CLIENT_LOGGER.info(f'Завершение работы клиента')
    #     my_sock.close()
    #     CLIENT_LOGGER.info(f'Клиент остановлен')
        # serv_ip, serv_port = handle_parameters(ip='127.0.0.1', port=DEF_PORT)
        # if serv_ip == '':
        #     CLIENT_LOGGER.error(f'Параметр -a является обязательным. Напимер: -a 127.0.0.1')
        #     # print(' | ОШИБКА: Параметр -a является обязательным. Напимер: -a 127.0.0.1')
        #     my_sock.close()
        #     # raise ValueError
        #     return
        # try:
        #     CLIENT_LOGGER.info(f'Попытка соедиения: ip={serv_ip} port={serv_port}')
        #     client_sock.connect((serv_ip, serv_port))
        #     CLIENT_LOGGER.info(f'Отправляю сообщение: {presence_message}')
        #     send_message(client_sock, presence_message)
        #     CLIENT_LOGGER.debug(f'Получено сообщение от сервера: ip={serv_ip} port={serv_port}')
        #     server_answer = get_message(client_sock)
        #     CLIENT_LOGGER.debug(f'Содержимое сообщения: {handle_answer(server_answer)}')
        #
        # except ConnectionResetError:
        #     CLIENT_LOGGER.info(f'Сервер {serv_ip}:{serv_port} разорвал соединение.')
        # client_sock.close()


if __name__ == '__main__':
    main()
