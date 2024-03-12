from types import SimpleNamespace
hyper_paras : SimpleNamespace

from time import sleep

print("Hello, here is an independent script.")

with open('example.txt', 'r') as f:
    print(f.read())

print(f'{hyper_paras.alpha = }')
print(f'{hyper_paras.beta = }')
print(f'{hyper_paras.method = }')

for i in range(5):
    print('count:',i)
    sleep(.5)

raise ValueError("This is a test error, you should be able to see this in the error log.")