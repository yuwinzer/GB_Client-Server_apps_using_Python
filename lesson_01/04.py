# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard»
# из строкового представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).

def code_list(sl, encode=True):
    res = []
    for s in sl:
        res.append(s.encode('utf-8')) if encode else res.append(s.decode('utf-8'))
    return res


words_to_convert = ['разработка', 'администрирование', 'protocol', 'standard']
words_encoded = code_list(words_to_convert)
print(words_encoded)
print(code_list(words_encoded, False))