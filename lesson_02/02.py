"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
 Написать скрипт, автоматизирующий его заполнение данными. Для этого:
Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item),
 количество (quantity), цена (price), покупатель (buyer), дата (date).
  Функция должна предусматривать запись данных в виде словаря в файл orders.json.
   При записи данных указать величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
"""
import json


def write_order_to_json(item: str, quantity: str, price: str, buyer: str, date: str):
    with open('orders.json', 'r', encoding='utf-8') as orders_file:
        file_data = json.load(orders_file)
        orders = file_data['orders']
        new_order = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }
        orders.append(new_order)

    with open('orders.json', 'w', encoding='utf-8', newline='') as orders_file:
        orders_file.write(json.dumps(file_data, indent=4, ensure_ascii=False))


write_order_to_json('Стул', '1', '10', 'Стульщик', '05.12.21')
write_order_to_json('Стол', '2', '20', 'Стольщик', '06.12.21')
write_order_to_json('Гроб', '3', '30', 'Шкафник', '08.12.21')