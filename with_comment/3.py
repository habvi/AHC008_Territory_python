from collections import defaultdict
import random

W = 30
T = 300


class Global:
    def __init__(self):
        # pets(10 <= n <= 20, 1 ~ n)
        self.n = int(input())
        self.pets_xyk = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(self.n)]
        # human(5 <= m <= 10, -1 ~ -m)
        self.m = int(input())
        self.human_xy = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(self.m)]

        self.is_all_human_reach_the_row = False
        self.human_row_destination = [None, *sorted(random.sample(range(1, W, 2), k=self.m))]

        self.is_human_col_left = [False] * (self.m + 1)
        self.is_human_col_left[0] = True
        self.is_human_col_right = [False] * (self.m + 1)
        self.is_human_col_right[0] = True

    def set_place(self):
        self.place_all = defaultdict(list)
        self.pets_place = [None]
        self.pets_kind = [None]
        for i, (x, y, k) in enumerate(self.pets_xyk, 1):
            self.place_all[(x, y)].append(i)
            self.pets_place.append((x, y))
            self.pets_kind.append(k)

        self.human_place = [None]
        for i, (x, y) in enumerate(self.human_xy, 1):
            self.place_all[(x, y)].append(-i)
            self.human_place.append((x, y))


def get_nxt_xy(x, y, dir):
    if dir == 'U':
        return x - 1, y
    elif dir == 'D':
        return x + 1, y
    elif dir == 'L':
        return x, y - 1
    else:
        return x, y + 1


# pets : i, human : -i
def erase_place(g, x, y, i):
    g.place_all[(x, y)].remove(i)
    if not g.place_all[(x, y)]:
        del g.place_all[(x, y)]


# pets : i, human : -i
def update_place(g, x, y, i):
    if i > 0:
        g.pets_place[i] = (x, y)
    else:
        g.human_place[-i] = (x, y)
    g.place_all[(x, y)].append(i)


# 上の空マスの更に隣接にpetsがいるか
def is_pets_adjacent(g, x, y):
    for dx, dy in zip((0, 1, 0, -1), (1, 0, -1, 0)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < W and 0 <= ny < W):
            continue
        for i in range(1, g.n + 1):
            if i in g.place_all[(nx, ny)]:
                return True
    return False


def move_human(g):
    res = [None] * g.m

    # まだ全員目的rowに着いてない
    if not g.is_all_human_reach_the_row:
        # human(x, i) sort済 毎回必要
        human_xi = sorted((x, i) for i, (x, _) in enumerate(g.human_place[1:], 1))

        # updown
        for (now_x, i), dest_x in zip(human_xi, g.human_row_destination[1:]):
            if now_x == dest_x:
                res[i - 1] = '.'
                continue
            if now_x < dest_x:
                res[i - 1] = 'D'
                dir = 'D'
            else:
                res[i - 1] = 'U'
                dir = 'U'
            x, y = g.human_place[i]
            erase_place(g, x, y, -i)
            x, y = get_nxt_xy(x, y, dir)
            update_place(g, x, y, -i)

        # 全員着いていれば True
        h_now_xs = sorted(x for x, _ in g.human_place[1:])
        if h_now_xs == g.human_row_destination[1:]:
            g.is_all_human_reach_the_row = True
    else:
        # 全員着いてる : 横方向に移動(行けるだけ左, 左に突き当ったら右に行けるだけ)
        # しながら壁を置けるなら置く(置きたいところに何かいたら何もしない)
        for i, (x, y) in enumerate(g.human_place[1:], 1):
            # 左端 and 上が壁
            if y == 0 and '#' in g.place_all[(x - 1, y)]:
                g.is_human_col_left[i] = True

            # 右端 and 上が壁
            if y == W - 1 and '#' in g.place_all[(x - 1, y)]:
                g.is_human_col_right[i] = True
            
            # 横全部置き終わった
            if g.is_human_col_left[i] and g.is_human_col_right[i]:
                res[i - 1] = '.'
                continue

            # left
            if not g.is_human_col_left[i]:
                if g.place_all[(x - 1, y)]:
                    # 上に human or pets : 何もしない
                    if '#' not in g.place_all[(x - 1, y)]:
                        res[i - 1] = '.'
                    # 上に壁 : 左に移動
                    else:
                        res[i - 1] = 'L'
                        erase_place(g, x, y, -i)
                        x, y = get_nxt_xy(x, y, 'L')
                        update_place(g, x, y, -i)
                else:
                    # 上の空の更に隣接にpetsがいたら何もしない
                    if is_pets_adjacent(g, x - 1, y):
                        res[i - 1] = '.'
                    # 上の空の更に隣接にpetsがいなければ壁を置く
                    else:
                        res[i - 1] = 'u'
                        g.place_all[(x - 1, y)].append('#')
                continue

            # right
            if g.place_all[(x - 1, y)]:
                if '#' not in g.place_all[(x - 1, y)]:
                    res[i - 1] = '.'
                else:
                    res[i - 1] = 'R'
                    erase_place(g, x, y, -i)
                    x, y = get_nxt_xy(x, y, 'R')
                    update_place(g, x, y, -i)
            else:
                if is_pets_adjacent(g, x - 1, y):
                    res[i - 1] = '.'
                else:
                    res[i - 1] = 'u'
                    g.place_all[(x - 1, y)].append('#')

    return ''.join(res)


# 入力通りにpetsを移動
def move_pets(g, nxt_pets_move):
    for i, dir in enumerate(nxt_pets_move, 1):
        x, y = g.pets_place[i]
        erase_place(g, x, y, i)
        for d in dir:
            x, y = get_nxt_xy(x, y, d)
        update_place(g, x, y, i)


# visualizer用 pets移動先 生成
def create_nxt_pets_move(g):
    direction = 'UDLR'
    res = []
    for x, y in g.pets_place[1:]:
        for i, (dx, dy) in enumerate(zip((-1, 1, 0, 0), (0, 0, -1, 1))):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < W) or '#' in g.place_all[(nx, ny)]:
                continue
            res.append(direction[i])
            break
    return ' '.join(res)


def main():
    g = Global()
    g.set_place()
    # print('> place_all :', place_all)
    # print('> pets_place :', pets_place)
    # print('> human_place :', human_place)
    # print('> human_col_destination :', g.human_col_destination)

    for _ in range(T):
        res = move_human(g)
        # don't erase
        print(res, flush=True)

        # print('提出時消す---------------------------------------------------------------')
        # visualizer用 pets移動先 出力
        nxt_pets_move = create_nxt_pets_move(g)
        print(nxt_pets_move)
        nxt_pets_move = nxt_pets_move.split()
        # print('提出時消す---------------------------------------------------------------')

        # print('提出時これ必要')
        # nxt_pets_move = input().split()
        move_pets(g, nxt_pets_move)


if __name__ == '__main__':
    main()