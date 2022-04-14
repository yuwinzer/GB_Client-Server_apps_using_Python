"""
1. На клиентской стороне реализовать прием и отправку сообщений с помощью потоков в P2P-формате
(обмен сообщениями между двумя пользователями).
Итогом выполнения домашних заданий первой части продвинутого курса Python стал консольный мессенджер.

Усовершенствуем его во второй части: реализуем взаимосвязь мессенджера с базами данных
и создадим для него графический пользовательский интерфейс.
"""
# CLIENT
import json
import sys
import threading
from time import time, sleep
from socket import socket, AF_INET, SOCK_STREAM
from common.globals import ACTION, SENDER, DESTINATION, PRESENCE, RESPONSE, ERROR, EXIT, ONLINE,\
    TIME, USER, ACCOUNT_NAME, DEF_PORT, DEF_IP, MESSAGE, MESSAGE_TEXT
from common.utils import send_message, get_message, handle_parameters
from common.errors import ReqFieldMissingError, ServerError
import logging
import log.client_log_config

LOGGER = logging.getLogger('client')


def message_from_server(sock, acc_name):
    while True:
        try:
            msg = get_message(sock)
            if not msg:
                sys.exit(0)
            if ACTION in msg and msg[ACTION] == MESSAGE and TIME in msg and \
            SENDER in msg and MESSAGE_TEXT in msg:
                if DESTINATION in msg and msg[DESTINATION] == acc_name:
                    print(f'ЛИЧНО [{msg[SENDER]}]: {msg[MESSAGE_TEXT]}')
                else:
                    print(f'[{msg[SENDER]}]: {msg[MESSAGE_TEXT]}')
                LOGGER.debug(f'Получено сообщение от пользователя {msg[SENDER]}: {msg[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {msg}')
        except Exception:
            LOGGER.error(f'Не удалось декодировать полученное сообщение: {msg}')
            break
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.error(f'Потеряно соединение с сервером.')
            break


def create_message(sock, acc_name, dest_name, msg):
    message_dict = {
        ACTION: MESSAGE,
        TIME: time(),
        SENDER: acc_name,
        DESTINATION: dest_name,
        MESSAGE_TEXT: msg
    }
    try:
        send_message(sock, message_dict)
        LOGGER.debug(f'Отправлено сообщение для пользователя {dest_name}')
    except:
        LOGGER.error('Потеряно соединение с сервером.')
        sys.exit(1)


def create_service_message(acc_name, mgs_type):
    if mgs_type == PRESENCE:
        LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {acc_name}')
        return {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                ACCOUNT_NAME: acc_name
            }
        }
    if mgs_type == ONLINE:
        LOGGER.debug(f'Сформировано {ONLINE} сообщение для сервера')
        return {
            ACTION: ONLINE,
            TIME: time(),
            USER: {
                ACCOUNT_NAME: acc_name
            }
        }
    if mgs_type == EXIT:
        return {
            ACTION: EXIT,
            TIME: time(),
            ACCOUNT_NAME: acc_name
        }


def handle_answer(msg):
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200 : OK'
        elif msg[RESPONSE] == 400:
            LOGGER.error(f'Ошибка соединения: {msg}')
            raise Exception
    LOGGER.error(f'Получен неправильный ответ сервера(отсутствует RESPONSE): {msg}')
    raise ValueError


def print_help():
    print('Поддерживаемые команды:')
    print('<сообщение> - отправить сообщение всем')
    print('! <имя> <сообщение> - отправить личное сообщение')
    print('/! - запросить список собеседников')
    print('/h или /? - вывести подсказки по командам')
    print('/q или /й - выход из программы')


def UI(sock, acc_name):
    print_help()
    while True:
        msg = input(f'<: ')
        command = msg[0:2]

        if command in ['/q', '/й']:
            send_message(sock, create_service_message(acc_name, EXIT))
            print('Завершение работы')
            LOGGER.info('Завершение работы по команде пользователя.')
            sys.exit(0)

        elif command in ['/h', '/?']:
            print_help()

        elif command in ['! ']:
            _name_len = msg[2:].find(' ')
            if _name_len > 0:
                dest_name = msg[2:2+_name_len]
                create_message(sock, acc_name, dest_name, msg[3+_name_len:])
            else:
                print('Для отправки личного сообщения введите "! <имя> <сообщение>"')

        elif command in ['/!']:
            send_message(sock, create_service_message(acc_name, ONLINE))
        else:
            create_message(sock, acc_name, '', msg)


def main():
    try:
        serv_ip, serv_port, acc_name = handle_parameters(ip=DEF_IP, port=DEF_PORT)
        print('Клиент системы обмена сообщениями. ВЕРСИЯ 015 БУ. ГОСТ 189-27-1956.')
        if not acc_name:
            acc_name = input('Представьтесь: ')
        print(f'Приветствуем, {acc_name}.\n'
              f'Напоминаем, что вы несете полную ответственность за свои слова в соответствии с законодательнвом.\n'
              f'Приятного общения.')
        sleep(1)
        LOGGER.info(f'Клиент запущен. Использую SERVER IP:{serv_ip} PORT:{serv_port} NAME:{acc_name}')

        try:
            LOGGER.debug(f'Попытка соедиения...')
            my_sock = socket(AF_INET, SOCK_STREAM)
            my_sock.connect((serv_ip, serv_port))
            LOGGER.debug(f'Отправляю сообщение о присутствии...')
            send_message(my_sock, create_service_message(acc_name, PRESENCE))
            LOGGER.debug(f'Жду ответа от сервера...')
            answer = handle_answer(get_message(my_sock))
            LOGGER.info(f'Соединение установлено')
            LOGGER.debug(f'Получен ответ сервера: {answer}')
            print(f'Соединение установлено')
        except json.JSONDecodeError:
            LOGGER.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            LOGGER.info(f'Не удалось подключиться к серверу {serv_ip}:{serv_port}, '
                        f'сервер отверг запрос на подключение.')
            sys.exit(1)
        else:
            thread_receiver = threading.Thread(target=message_from_server, args=(my_sock, acc_name))
            thread_receiver.daemon = True
            thread_receiver.start()
            LOGGER.debug('Запущен процесс получатель')

            thread_sender_ui = threading.Thread(target=UI, args=(my_sock, acc_name))
            thread_sender_ui.daemon = True
            thread_sender_ui.start()
            LOGGER.debug('Запущен процесс интерфейс и отправщик')

            while thread_receiver.is_alive() and thread_sender_ui.is_alive():
                sleep(0.7)

    except KeyboardInterrupt:
        LOGGER.info(f'Завершение работы клиента')
        # my_sock.close()
        LOGGER.info(f'Клиент остановлен')
        sys.exit(1)


if __name__ == '__main__':
    main()
