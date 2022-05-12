H, W = 30, 30
T = 300

class Global:
    def __init__(self) -> None:
        # pets(10 <= N <= 20)
        self.N = int(input())
        self.P = [tuple(map(int, input().split())) for _ in range(self.N)]
        # human(5 <= M <= 10)
        self.M = int(input())
        self.H = [tuple(map(int, input().split())) for _ in range(self.M)]

def move(g):
    for _ in range(T):
        print('.' * g.M, flush=True)
        pets_move = input().split()

def main():
    g = Global()
    move(g)

if __name__ == '__main__':
    main()