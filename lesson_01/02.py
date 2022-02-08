# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования
# в последовательность кодов (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.

def print_evaluable(sl):
    for s in sl:
        b = eval(f'b"{s}"')
        print(f'{b} is {type(b)} and {len(b)} bytes long')


words_to_check = ['class', 'function', 'method']
print_evaluable(words_to_check)