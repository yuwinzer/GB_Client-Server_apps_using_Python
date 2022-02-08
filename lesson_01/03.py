# 3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
# Важно: решение должно быть универсальным, т.е. не зависеть от того, какие конкретно слова мы исследуем.

def print_evaluable(sl):
    err_list = []
    for s in sl:
        try:
            eval(f'b"{s}"')
        except SyntaxError:
            err_list.append(s)
    print(f'This words need encoding: {str(err_list)[1:-1]}')


words_to_check = ['attribute', 'класс', 'функция', 'type']
print_evaluable(words_to_check)