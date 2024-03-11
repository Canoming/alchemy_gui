alpha: float
beta: float
method: str

from time import sleep

print("Hello, here is an independent script.")

with open('example.txt', 'r') as f:
    print(f.read())

print(f'{alpha = }')
print(f'{beta = }')
print(f'{method = }')

for i in range(8):
    print('count:',i)
    sleep(.5)

raise ValueError("This is a test error, you should be able to see this in the error log.")