"""
1. Задание на закрепление знаний по модулю CSV.
 Написать скрипт, осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt, info_3.txt
  и формирующий новый «отчетный» файл в формате CSV. Для этого:
Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и считывание данных.
 В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения параметров
  «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
   Значения каждого параметра поместить в соответствующий список.
   Должно получиться четыре списка — например, os_prod_list, os_name_list, os_code_list, os_type_list.
   В этой же функции создать главный список для хранения данных отчета — например, main_data —
   и поместить в него названия столбцов отчета в виде списка:
   «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
    Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла);
Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
 В этой функции реализовать получение данных через вызов функции get_data(),
  а также сохранение подготовленных данных в соответствующий CSV-файл;
Проверить работу программы через вызов функции write_to_csv().
"""
from chardet import detect
import re
import csv


def read_file_encoding(file_name: str) -> any:
    with open(file_name, 'rb') as f:
        content = f.read()
    return detect(content)['encoding']


def get_data(to_extract: list, info_files: list):
    sys_prod_list, os_name_list, prod_code_list, sys_type_list, main_data = [], [], [], [], []
    main_data.append(to_extract.copy())
    for file_name in info_files:
        enc = read_file_encoding(file_name)
        with open(file_name, encoding=enc) as file:
            for file_row in file:
                for idx, search_row in enumerate(to_extract, 0):
                    reg_exp = fr'{search_row}' + r'.\s*'
                    if re.search(reg_exp, file_row):
                        fr = re.sub(r'\s*\n', '', re.sub(reg_exp, '', file_row))
                        # print(f'{fr=} {idx=}')
                        # ================================================================
                        # На моем курсе регулярки НЕ ПРЕПОДАВАЛИСЬ как таковые и ни разу не рекомендовались к обучению
                        # (На этот курс перешел с другого)
                        # Много времени потратил на понимание как их вообще использовать
                        # Минуту потратил на следующий код:
                        # fs = file_row[file_row.find(search_row)+len(search_row)+1:].lstrip().rstrip()
                        # print(f'{fs=}')
                        # ================================================================
                        if idx == 0: sys_prod_list.append(fr)
                        if idx == 1: os_name_list.append(fr)
                        if idx == 2: prod_code_list.append(fr)
                        if idx == 3: sys_type_list.append(fr)
                        break
    for i in range(0, len(to_extract)-1):
        main_data.append([sys_prod_list[i], os_name_list[i], prod_code_list[i], sys_type_list[i]])
    return main_data


def write_to_csv(income_data_list, income_file_list, output_file_name):
    data = get_data(income_data_list, income_file_list)
    # print(data)
    with open(output_file_name, 'w', encoding='utf-8', newline='') as of:
        of_wrighter = csv.writer(of)
        of_wrighter.writerows(data)


data_to_extract = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
income_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']
output_file = 'main_data.csv'
write_to_csv(data_to_extract, income_files, output_file)