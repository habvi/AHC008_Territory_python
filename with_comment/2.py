from collections import defaultdict
import random

W = 30
T = 300
print('erase : T = 2')
# T = 2
place_all = defaultdict(list)
pets_place = [None]
human_place = [None]
pets_kind = [None]


class Global:
    def __init__(self) -> None:
        # pets(10 <= n <= 20, 1 ~ n)
        self.n = int(input())
        self.pets_xyk = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(self.n)]
        # human(5 <= m <= 10, -1 ~ -m)
        self.m = int(input())
        self.human_xy = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(self.m)]

        self.human_col_place = False
        self.human_col_destination = sorted(random.sample(range(1, W, 2), k=self.m))

        self.human_row_left = [False] * self.m
        self.human_row_right = [False] * self.m


def set_place(g):
    for i, (x, y, k) in enumerate(g.pets_xyk, 1):
        place_all[(x, y)].append(i)
        pets_place.append((x, y))
        pets_kind.append(k)
    for i, (x, y) in enumerate(g.human_xy, 1):
        place_all[(x, y)].append(-i)
        human_place.append((x, y))


def get_nxt_xy(x, y, dir):
    if dir == 'U':
        return x - 1, y
    elif dir == 'D':
        return x + 1, y
    elif dir == 'L':
        return x, y - 1
    else:
        return x, y + 1


def erase_place(x, y, i):
    place_all[(x, y)].remove(i)
    if not place_all[(x, y)]:
        del place_all[(x, y)]


def is_pets_adjacent(g, x, y) -> bool:
    for i, (dx, dy) in enumerate(zip((0, 1, 0, -1), (1, 0, -1, 0))):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < W and 0 <= ny < W):
            continue
        for i in range(1, g.n + 1):
            if i in place_all[(nx, ny)]:
                return True
    return False


def move_human(g):
    res = [None] * g.m
    # 全員目的地に着いてなければ
    if not g.human_col_place:
        # human (x, i)
        h_xs = []
        for i, (x, y) in enumerate(human_place[1:], 1):
            h_xs.append((x, i))
        h_xs.sort()

        # 目的地に着くまで上下に移動
        for (now_x, i), dest_x in zip(h_xs, g.human_col_destination):
            if now_x == dest_x:
                res[i - 1] = '.'
                continue
            if now_x < dest_x:
                res[i - 1] = 'D'
                dir = 'D'
            else:
                res[i - 1] = 'U'
                dir = 'U'
            now_x, now_y = human_place[i]
            erase_place(now_x, now_y, -i)
            now_x, now_y = get_nxt_xy(now_x, now_y, dir)
            human_place[i] = (now_x, now_y)
            place_all[(now_x, now_y)].append(-i)

        # 全員目的地に着いていれば True に更新
        h_xs = sorted(x for x, y in human_place[1:])
        if h_xs == g.human_col_destination:
            g.human_col_place = True
    else:
        # 全員着いてるなら横方向に移動(行けるだけ左, 左に突き当ったら右に行けるだけ)
        # しながら壁を置けるなら置く(置きたいところに何かいたら何もしない)
        for i, (x, y) in enumerate(human_place[1:], 1):
            if x == 0:
                res[i - 1] = '.'
                continue
            if y == 0 and '#' in place_all[(x - 1, y)]:
                g.human_row_left[i - 1] = True
            if y == W - 1 and '#' in place_all[(x - 1, y)]:
                g.human_row_right[i - 1] = True
            if g.human_row_left[i - 1] and g.human_row_right[i - 1]:
                res[i - 1] = '.'
                continue

            # left
            if not g.human_row_left[i - 1]:
                # 上に何かある
                if place_all[(x - 1, y)]:
                    # human or pets : 何もしない
                    if '#' not in place_all[(x - 1, y)]:
                        res[i - 1] = '.'
                    # 壁 : 左に移動
                    else:
                        res[i - 1] = 'L'
                        erase_place(x, y, -i)
                        human_place[i] = (x, y - 1)
                        place_all[(x, y - 1)].append(-i)
                # 上が空
                else:
                    # 空の更に隣接にpetsがいたら何もしない(humanだったら？)
                    if is_pets_adjacent(g, x - 1, y):
                        res[i - 1] = '.'
                    # 空の更に隣接にpetsがいなければ壁を置く
                    else:
                        res[i - 1] = 'u'
                        place_all[(x - 1, y)].append('#')
                continue

            # right
            # 上に何かある
            if place_all[(x - 1, y)]:
                # human or pets : 何もしない
                if '#' not in place_all[(x - 1, y)]:
                    res[i - 1] = '.'
                # 壁 : 右に移動
                else:
                    res[i - 1] = 'R'
                    erase_place(x, y, -i)
                    human_place[i] = (x, y + 1)
                    place_all[(x, y + 1)].append(-i)
            # 上が空
            else:
                # 空の更に隣接にpetsがいたら何もしない(humanだったら？)
                if is_pets_adjacent(g, x - 1, y):
                    res[i - 1] = '.'
                # 空の更に隣接にpetsがいなければ壁を置く
                else:
                    res[i - 1] = 'u'
                    place_all[(x - 1, y)].append('#')

    return ''.join(res)


# 入力通りにpetsを移動
def move_pets(nxt_pets_move):
    for i, dir in enumerate(nxt_pets_move, 1):
        now_x, now_y = pets_place[i]
        erase_place(now_x, now_y, i)
        for d in dir:
            now_x, now_y = get_nxt_xy(now_x, now_y, d)
        pets_place[i] = (now_x, now_y)
        place_all[(now_x, now_y)].append(i)


# visualizer用 pets移動先 生成
def create_nxt_pets_move():
    direction = 'RDLU'
    res = []
    for x, y in pets_place[1:]:
        for i, (dx, dy) in enumerate(zip((0, 1, 0, -1), (1, 0, -1, 0))):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < W) or '#' in place_all[(nx, ny)]:
                continue
            res.append(direction[i])
            break
    return ' '.join(res)


def main():
    g = Global()
    set_place(g)
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
        nxt_pets_move = create_nxt_pets_move()
        print(nxt_pets_move)
        nxt_pets_move = nxt_pets_move.split()
        # print('提出時消す---------------------------------------------------------------')

        # print('提出時これ必要')
        # nxt_pets_move = input().split()
        move_pets(nxt_pets_move)


if __name__ == '__main__':
    main()