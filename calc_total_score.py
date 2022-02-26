import sys

args = sys.argv
times = int(args[1]) + 1

total = 0

for i in range(times):
    input_ = input().split()
    total += int(input_[2])

print('total score : ', '{:,}'.format(total))
print('if 100 times:', '{:,}'.format(int(100 / times * total)))