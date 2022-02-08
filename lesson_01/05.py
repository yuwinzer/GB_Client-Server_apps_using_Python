# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com
# и преобразовать результаты из байтовового в строковый тип на кириллице.

import chardet
import subprocess
import platform


def ping_my_favorite_and_banned_sites(hosts):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    for host in hosts:
        args = ['ping', param, '2', host]
        enc = subprocess.Popen(args, stdout=subprocess.PIPE)
        result = b''
        print('Ожидайте', end='')
        for line in enc.stdout:
            enc = chardet.detect(line)
            result += line.decode(enc['encoding']).encode('utf-8')
            print('.', end='')
        print(result.decode('utf-8'))


hosts = ['yandex.ru', 'youtube.com']
ping_my_favorite_and_banned_sites(hosts)