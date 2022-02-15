"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата. Для этого:
Подготовить данные для записи в виде словаря,
 в котором первому ключу соответствует список,
 второму — целое число,
  третьему — вложенный словарь, где значение каждого ключа — это целое число с юникод-символом,
  отсутствующим в кодировке ASCII (например, €);

Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
 При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
  а также установить возможность работы с юникодом: allow_unicode = True;
Реализовать считывание данных из созданного файла и проверить, совпадают ли они с исходными.
"""
import yaml


def write_blsht_to_yaml(data: dict):
    print(data)
    with open('file.yaml', 'w', encoding='utf-8', newline='') as blsht_file:
        yaml.dump(data, blsht_file, default_flow_style=False, allow_unicode=True)


def read_blsht_from_yaml():
    with open('file.yaml', encoding='utf-8') as blsht_file:
        blsht = yaml.load(blsht_file, Loader=yaml.FullLoader)
        print(blsht)
        return blsht


data = {
    'key_1': ['Стул', 'Стол', 'Гроб'],
    'key_2': 1,
    'key_3': {'income_price': '10€',
              'buyer_price': '30€',
              'discount_price': '28€'}
}
write_blsht_to_yaml(data)
new_data = read_blsht_from_yaml()
if new_data == data:
    print('Данные совпадают. Удивительно!')
else:
    print('Абыр.. Абырвалг!')
