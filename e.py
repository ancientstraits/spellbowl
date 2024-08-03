s = 'blasé'
print(s)
b = bytes(s, encoding='utf-8')
with open('x', 'wb') as f:
    f.write(b)