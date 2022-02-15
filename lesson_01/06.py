# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Далее забыть о том, что мы сами только что создали этот файл и исходить из того,
# что перед нами файл в неизвестной кодировке.
# Задача: открыть этот файл БЕЗ ОШИБОК вне зависимости от того, в какой кодировке он был создан.

from chardet import detect


def read_and_print_file_with_any_encoding(file_name):
    with open(file_name, 'rb') as f:
        content = f.read()
    encoding = detect(content)['encoding']
    print('encoding: ', encoding)

    with open(file_name, encoding=encoding) as f_n:
        for el_str in f_n:
            print(el_str, end='')
        print()


file_to_read = 'test_file.txt'
read_and_print_file_with_any_encoding(file_to_read)