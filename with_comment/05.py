from collections import defaultdict

W = 30
T = 300

class Global_4:
    def __init__(self, n, pets_xyk, m, human_xy):
        self.n = n
        self.pets_xyk = pets_xyk
        self.m = m
        self.human_xy = human_xy
        # 担当
        self.roles = [0] * self.m
        # 目的地
        self.top5_row_destination = [2, 6, 10, 14, 18]
        self.col_aisle = [7, 15, 23]
        # next move (i, dir)
        self.move_human_later = []
        # new roles (i, role)
        self.new_human_roles = []
        # roleを与えた瞬間に追加 roleだけ,roleごとの人数
        self.done_roles = set()
        self.done_roles_count = defaultdict(int)

        # state 0 : 誰がどこrow(x)を目指す
        self.top5_each_destination = {}
        # state 1 : 5人目的rowに着いたか -> 壁を置き始めて良い
        self.state_1 = [False] * self.m
        # 5人左右端に着いたか
        self.state_2 = [False] * self.m
        # 5人左右壁置き終わり端に着いたか
        self.state_4_left = [False] * self.m
        self.state_4_right = [False] * self.m
        # 上2人の付与されたrole, 下2人の付与されたrole
        self.state_6_roles = set()
        # 上1人が左右に壁を置き終わったか
        self.state_12_left = False
        self.state_12_right = False
        # 上1人が6個壁を置く場所
        self.state_12_wall_y = set([6, 8, 14, 16, 22, 24])
        # 個々が上下どっちに移動してるか
        self.state_200_dir = ['U'] * self.m


        # 最後上下pet塞ぎながら移動のとき通路(7, 15, 23)何人担当してるか  (全員 - 4人)
        self.number_of_each_aisle = defaultdict(int)
        # 最後上下pet塞ぎながら移動のとき通路(7, 15, 23)の担当は誰か {7 : [i, i, i], 15:[], 23[i, i]}
        self.who_each_aisle = defaultdict(list)
        # i番の人は通路のどこを担当してるか
        self.where_my_aisle = defaultdict(int)
        # row_xに壁置いた人がもう置き終わって通路に出てるか もう置けるマス(x, y)
        self.no_human = set()
        # next no human place (x, y)
        self.no_human_later = []
        # next put wall place (x, y)
        self.put_wall_later = set()
        # pair list (hi_1, hi_2,)
        self.pair_list = []


    def set_all_place(self):
        self.place_all = defaultdict(list)
        self.pets_place = []
        self.pets_kind = []
        for i, (x, y, k) in enumerate(self.pets_xyk, 1):
            self.place_all[(x, y)].append(i)
            self.pets_place.append((x, y))
            self.pets_kind.append(k)
        self.human_place = []
        for i, (x, y) in enumerate(self.human_xy, 1):
            self.place_all[(x, y)].append(-i)
            self.human_place.append((x, y))

    def initial_set_roles(self):
        def _set_roles(hi, role):
            self.roles[hi] = role
            self.done_roles.add(role)
            self.done_roles_count[role] += 1

        human_xyi = sorted((x, y, i) for i, (x, y) in enumerate(self.human_place))
        # 上5人
        for i, (x, y, hi) in enumerate(human_xyi[:5]):
            my_destination = self.top5_row_destination[i]
            self.top5_each_destination[hi] = my_destination
            # 縦がまだ1へ                                               role: 0 -> 1
            if x != my_destination:
                _set_roles(hi, 1)
                # 左右端にいる
                if y in (0, 29):
                    self.state_2[hi] = True
            # 縦はもう着いてる
            else:
                self.state_1[hi] = True
                # 横がまだ                                              role: 0 -> 2
                if y not in (0, 29):
                    _set_roles(hi, 2)
                # 左右端にいる                                           role: 0 -> 3
                else:
                    self.state_2[hi] = True
                    _set_roles(hi, 3)


        # 通路の状態
        def _set_col_aisle(hi, place):
            self.number_of_each_aisle[place] += 1
            self.who_each_aisle[place].append(hi)
            self.where_my_aisle[hi] = place


        # 1番上の人の最後担当col
        x, y, hi = human_xyi[0]
        left, middle, right = self.col_aisle
        if y < 15:
            _set_col_aisle(hi, left)
        else:
            _set_col_aisle(hi, right)


        def _assign_rest_human(hi, x, y, place):
            # 縦がまだ100へ                                             role: 0 -> 100
            if x % 2 == 1:
                _set_roles(hi, 100)
                # y指定通路に着いてる
                if y == place:
                    self.state_2[hi] = True
            # 縦はもう着いてる
            else:
                self.state_1[hi] = True
                # 横がまだ                                              role: 0 -> 101
                if y != place:
                    _set_roles(hi, 101)
                # 左右端にいる                                          role: 0 -> 1000
                else:
                    self.state_2[hi] = True
                    _set_roles(hi, 1000)


        # 残りの人
        rest_human = human_xyi[5:]
        rest_human.sort(key=lambda x: x[1])
        # 2人以下なら7,15,23の0人のところ
        if len(rest_human) <= 2:
            for x, y, hi in rest_human:
                if self.number_of_each_aisle[left] == 0:
                    _set_col_aisle(hi, left)
                    _assign_rest_human(hi, x, y, left)
                elif self.number_of_each_aisle[middle] == 0:
                    _set_col_aisle(hi, middle)
                    _assign_rest_human(hi, x, y, middle)
                else:
                    _set_col_aisle(hi, right)
                    _assign_rest_human(hi, x, y, right)
        # 3人なら1人ずつ
        elif len(rest_human) == 3:
            for place, (x, y, hi) in zip([left, middle, right], rest_human):
                _set_col_aisle(hi, place)
                _assign_rest_human(hi, x, y, place)
        # 4~5人なら左から順に1人以下なら決定
        else:
            for x, y, hi in rest_human:
                if self.number_of_each_aisle[left] <= 1:
                    _set_col_aisle(hi, left)
                    _assign_rest_human(hi, x, y, left)
                elif self.number_of_each_aisle[middle] <= 1:
                    _set_col_aisle(hi, middle)
                    _assign_rest_human(hi, x, y, middle)
                else:
                    _set_col_aisle(hi, right)
                    _assign_rest_human(hi, x, y, right)

    def reset_for_next(self):
        self.move_human_later = []
        self.new_human_roles = []
        self.no_human_later = []
        self.put_wall_later = set()


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


def get_next_xy(x, y, dir):
    if dir == 'U':
        return x - 1, y
    elif dir == 'D':
        return x + 1, y
    elif dir == 'L':
        return x, y - 1
    else:
        return x, y + 1


def is_wall_up(g, x, y):
    return '#' in g.place_all[(x - 1, y)]


def is_wall_down(g, x, y):
    return '#' in g.place_all[(x + 1, y)]


def is_wall_left(g, x, y):
    return '#' in g.place_all[(x, y - 1)]


def is_wall_right(g, x, y):
    return '#' in g.place_all[(x, y + 1)]


def is_wall_xy(g, x, y):
    return '#' in g.place_all[(x, y)]


# 空マスの更に隣接にpetsがいるか
def is_pets_adjacent(g, x, y):
    for dx, dy in zip((0, 1, 0, -1), (1, 0, -1, 0)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < W and 0 <= ny < W):
            continue
        for i in g.place_all[(nx, ny)]:
            if i == '#':
                continue
            if i > 0:
                return True
    return False


def is_pets_left(g, x, y):
    for i in g.place_all[(x, y - 1)]:
        if i == '#':
            continue
        if i > 0:
            return True
    return False


def is_pets_right(g, x, y):
    for i in g.place_all[(x, y + 1)]:
        if i == '#':
            continue
        if i > 0:
            return True
    return False


def is_pets_xy(g, x, y):
    for i in g.place_all[(x, y)]:
        if i == '#':
            continue
        if i > 0:
            return True
    return False


def count_pets_xy(g, x, y):
    count_ = 0
    for i in g.place_all[(x, y)]:
        if i == '#':
            continue
        if i > 0:
            count_ += 1
    return count_


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

# top5

# updown
def do_state_1(g, hi):
    x, y = g.human_place[hi]
    dest_x = g.top5_each_destination[hi]

    # 縦目的地にいる
    if x == dest_x:
        g.state_1[hi] = True
        # まだ左右端にいない                        　                   role : 1 -> 2
        if y not in (0, 29):
            g.new_human_roles.append((hi, 2))
        # もう左右端にいる                          　                   role : 1 -> 3
        else:
            g.state_2[hi] = True
            g.new_human_roles.append((hi, 3))
        return '.'

    # まだ縦目的地にいない
    if x < dest_x:
        dir = 'D'
    else:
        dir = 'U'
    g.move_human_later.append((hi, dir))
    return dir


# left or right
def do_state_2(g, hi):
    _, y = g.human_place[hi]

    # 横目的地にいる                                                       role: 2 -> 3
    if y in (0, 29):
        g.state_2[hi] = True
        g.new_human_roles.append((hi, 3))
        return '.'

    if y < 15:
        dir =  'L'
    else:
        dir = 'R'
    g.move_human_later.append((hi, dir))
    return dir


# 左右端に着いたら待機。全員縦が大丈夫なら壁を置き始める4へ                  role: 3 -> 4
def do_state_3(g, hi):
    if all(g.state_1):
        g.new_human_roles.append((hi, 4))
    return '.'


# put wall updown
# 上下に壁を置きながら端まで行く
def do_state_4(g, hi):
    x, y = g.human_place[hi]
    wall_up = is_wall_up(g, x, y)
    wall_down = is_wall_down(g, x, y)

    # 左端 and 上下が壁
    if y == 0 and wall_up and wall_down:
        g.state_4_left[hi] = True

    # 右端 and 上下が壁
    if y == 29 and wall_up and wall_down:
        g.state_4_right[hi] = True

    # 壁を置き終わって端にいたら                                               role: 4 -> 5
    l_fin, r_fin = g.state_4_left[hi], g.state_4_right[hi]
    if l_fin and r_fin:
        g.new_human_roles.append((hi, 5))
        return '.'

    # 上下壁 or 埋めない通路なら左右に移動
    if (wall_up and wall_down) or (y in g.col_aisle):
        if l_fin:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later.append((hi, dir))
        return dir

    something_up = g.place_all[(x - 1, y)]
    something_down = g.place_all[(x + 1, y)]

    # 上下とも壁or生き物(壁は0か1)
    if something_up and something_down:
        return '.'

    # 上下に壁置けるなら置く,両方置けないなら何もしない
    if not something_up and not is_pets_adjacent(g, x - 1, y):
        res = 'u'
        g.put_wall_later.add((x - 1, y))
    elif not something_down and not is_pets_adjacent(g, x + 1, y):
        res = 'd'
        g.put_wall_later.add((x + 1, y))
    else:
        res = '.'
    return res


# 7 or 23 の近い方の通路に出る
def do_state_5(g, hi):
    x, y = g.human_place[hi]
    # もうy=(7,23)にいる                                                        role: 5 -> 6
    if y in (7, 23):
        g.new_human_roles.append((hi, 6))
        return '.'

    # まだy=(7,23)にいない
    if y < 7:
        dir = 'R'
    elif 23 < y:
        dir = 'L'
    g.move_human_later.append((hi, dir))
    return dir


# 通路に出たので no_human_later.append((x, y)) * 6 して10(上1人), 20,21(次2人), 50,51(次2人)を付与
def do_state_6(g, hi):
    x, y = g.human_place[hi]

    # そのrowを塞ぎ始めてokという合図
    for py in (6, 8, 14, 16, 22, 24):
        g.no_human_later.append((x, py))

    # top1                                                                        role: 6 -> 10
    if x == 2:
        g.new_human_roles.append((hi, 10))
    # next top2                                                                   role: 6 -> 20,21
    elif x in (6, 10):
        is_20 = 20 in g.done_roles or 20 in g.state_6_roles
        is_21 = 21 in g.done_roles or 21 in g.state_6_roles
        if y == 0 and not is_20:
            g.new_human_roles.append((hi, 20))
            g.state_6_roles.add(20)
        elif y == 29 and not is_21:
            g.new_human_roles.append((hi, 21))
            g.state_6_roles.add(21)
        elif not is_20:
            g.new_human_roles.append((hi, 20))
            g.state_6_roles.add(20)
        else:
            g.new_human_roles.append((hi, 21))
            g.state_6_roles.add(21)
    # under2                                                                       role: 6 -> 50,51
    elif x in (14, 18):
        is_50 = 50 in g.done_roles or 50 in g.state_6_roles
        is_51 = 51 in g.done_roles or 51 in g.state_6_roles
        if y == 0 and not is_50:
            g.new_human_roles.append((hi, 50))
            g.state_6_roles.add(50)
        elif y == 29 and not is_51:
            g.new_human_roles.append((hi, 51))
            g.state_6_roles.add(51)
        elif not is_50:
            g.new_human_roles.append((hi, 50))
            g.state_6_roles.add(50)
        else:
            g.new_human_roles.append((hi, 51))
            g.state_6_roles.add(51)
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

# top1

# x=28まで行く
def do_state_10(g, hi):
    x, y = g.human_place[hi]
    # x=28に着いたら11へ                                                            10 -> 11
    if x == 28:
        g.new_human_roles.append((hi, 11))
        res = '.'
    else:
        res = 'D'
        g.move_human_later.append((hi, res))
    return res


# x=28に着いてるのでy=6,24に行く
def do_state_11(g, hi):
    # y=(6, 24)に着いたら12へ                                                        11 -> 12
    x, y = g.human_place[hi]
    if y in (6, 24):
        g.new_human_roles.append((hi, 12))
        res = '.'
    else:
        if y == 7:
            res = 'L'
        else:
            res = 'R'
        g.move_human_later.append((hi, res))
    return res


# (28, 6) or (28, 24)にいるので下に6つ壁を置きながら反対に移動,置き終わったら13へ
def do_state_12(g, hi):
    x, y = g.human_place[hi]

    # 6つ壁を置く
    wall_down = is_wall_down(g, x, y)
    if y == 6 and wall_down:
        g.state_12_left = True
    if y == 24 and wall_down:
        g.state_12_right = True

    # 両側壁終わってたら次                                                           12 -> 13
    if g.state_12_left and g.state_12_right:
        g.new_human_roles.append((hi, 13))
        return '.'

    # 下が壁 or 埋めない通路なら左右に移動
    if (wall_down) or (y not in g.state_12_wall_y):
        if g.state_12_left:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later.append((hi, dir))
        return dir

    # 下に壁置けるなら置く,置けないなら何もしない
    something_down = g.place_all[(x + 1, y)]
    if not something_down and not is_pets_adjacent(g, x + 1, y):
        res = 'd'
        g.put_wall_later.add((x + 1, y))
    else:
        res = '.'
    return res


# (28, 6) or (28, 24)にいる。壁を置き終わったので通路(7, 23)に移動               　      13 -> 14
def do_state_13(g, hi):
    x, y = g.human_place[hi]
    if y == 6:
        dir = 'R'
    else:
        dir = 'L'
    g.move_human_later.append((hi, dir))
    g.new_human_roles.append((hi, 14))
    return dir


# 通路に出たので no_human_later.append((x, y)) * 6 して1000へ                         14 -> 1000
def do_state_14(g, hi):
    x, y = g.human_place[hi]

    # x = 28 を塞ぎ始めてok
    for py in (6, 8, 14, 16, 22, 24):
        g.no_human_later.append((x, py))

    g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

# top2

# x=22まで行く
def do_state_20_21(g, hi, role):
    x, y = g.human_place[hi]
    # x=22に着いてるなら次へ                                                20,21 -> 22,23
    if x == 22:
        g.new_human_roles.append((hi, role + 2))
        return '.'

    dir = 'D'
    g.move_human_later.append((hi, dir))
    return dir


# x=22なのでrole=20は左端,21は右端に移動
def do_state_22_23(g, hi, role):
    x, y = g.human_place[hi]

    # 左右端にいる                                                               22,23 -> 24,25
    if y in (0, 29):
        g.new_human_roles.append((hi, role + 2))
        return '.'

    if role == 22:
        dir = 'L'
    else:
        dir = 'R'
    g.move_human_later.append((hi, dir))
    return dir


# 上下に壁を置きながら中央まで行く
def do_state_24_25(g, hi, role):
    x, y = g.human_place[hi]

    # 真ん中についてたら24の人は左通路に戻る,25の人は真ん中担当として一瞬待機           24 -> 26, 25 -> 27
    if y == 15:
        g.new_human_roles.append((hi, role + 2))
        return '.'

    wall_up = is_wall_up(g, x, y)
    wall_down = is_wall_down(g, x, y)
    if (wall_up and wall_down) or (y in (7, 23)):
        if role == 24:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later.append((hi, dir))
        return dir

    something_up = g.place_all[(x - 1, y)]
    something_down = g.place_all[(x + 1, y)]
    if something_up and something_down:
        return '.'

    if not something_up and not is_pets_adjacent(g, x - 1, y):
        res = 'u'
        g.put_wall_later.add((x - 1, y))
    elif not something_down and not is_pets_adjacent(g, x + 1, y):
        res = 'd'
        g.put_wall_later.add((x + 1, y))
    else:
        res = '.'
    return res


# y=7に移動して28へ       　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　26 -> 28
def do_state_26(g, hi):
    x, y = g.human_place[hi]
    if y == 7:
        g.new_human_roles.append((hi, 28))
        return '.'
    dir = 'L'
    g.move_human_later.append((hi, dir))
    return dir


# 中央の人すぐ1000へ
def do_state_27(g, hi):
    g.new_human_roles.append((hi, 1000))
    return '.'


# そのrow2人終わって通路に退避完了かcheckして26 & 27 no_human_later.append((x, y)) * 6 する
def do_state_28(g, hi):
    x, y = g.human_place[hi]
    if (26 in g.done_roles) and (27 in g.done_roles):
        # x = 22 を塞ぎ始めてok
        for py in (6, 8, 14, 16, 22, 24):
            g.no_human_later.append((x, py))
        g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

# under2

def do_state_50_51(g, hi, role):
    x, y = g.human_place[hi]
    # x=26に着いてるなら次へ                                                    50,51 -> 52,53
    if x == 26:
        g.new_human_roles.append((hi, role + 2))
        return '.'
    dir = 'D'
    g.move_human_later.append((hi, dir))
    return dir


def do_state_52_53(g, hi, role):
    x, y = g.human_place[hi]
    # 左右端にいる                                                               52,53 -> 54,55
    if y in (0, 29):
        g.new_human_roles.append((hi, role + 2))
        return '.'
    if role == 52:
        dir = 'L'
    else:
        dir = 'R'
    g.move_human_later.append((hi, dir))
    return dir


def do_state_54_55(g, hi, role):
    x, y = g.human_place[hi]

    # 真ん中についてたら54の人は右通路に戻る,55の人は真ん中担当として一瞬待機         54 -> 56, 55 -> 57
    if y == 15:
        g.new_human_roles.append((hi, role + 2))
        return '.'

    wall_up = is_wall_up(g, x, y)
    wall_down = is_wall_down(g, x, y)
    if (wall_up and wall_down) or (y in (7, 23)):
        if role == 54:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later.append((hi, dir))
        return dir

    something_up = g.place_all[(x - 1, y)]
    something_down = g.place_all[(x + 1, y)]
    if something_up and something_down:
        return '.'

    if not something_up and not is_pets_adjacent(g, x - 1, y):
        res = 'u'
        g.put_wall_later.add((x - 1, y))
    elif not something_down and not is_pets_adjacent(g, x + 1, y):
        res = 'd'
        g.put_wall_later.add((x + 1, y))
    else:
        res = '.'
    return res


# y=23に移動して58へ       　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　56 -> 58
def do_state_56(g, hi):
    x, y = g.human_place[hi]
    if y == 23:
        g.new_human_roles.append((hi, 58))
        return '.'
    dir = 'R'
    g.move_human_later.append((hi, dir))
    return dir


# 中央の人すぐ1000へ
def do_state_57(g, hi):
    g.new_human_roles.append((hi, 1000))
    return '.'


# そのrow2人終わって通路に退避完了かcheckして56 & 57 no_human_later.append((x, y)) * 6 する
def do_state_58(g, hi):
    x, y = g.human_place[hi]
    if (56 in g.done_roles) and (57 in g.done_roles):
        # x = 26 を塞ぎ始めてok
        for py in (6, 8, 14, 16, 22, 24):
            g.no_human_later.append((x, py))
        g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


# rest, up
def do_state_100(g, hi):
    x, y = g.human_place[hi]

    # 縦目的地にいる
    if x % 2 == 0:
        g.state_1[hi] = True
        # まだ横指定通路にいない                        　                 role : 100 -> 101
        if y != g.where_my_aisle[hi]:
            g.new_human_roles.append((hi, 101))
        # もう横指定通路にいる                          　                 role : 100 -> 1000
        else:
            g.state_2[hi] = True
            g.new_human_roles.append((hi, 1000))
        return '.'

    # まだ縦にいない,1回だけ偶数rowに移動(壁避け)
    dir = 'U'
    g.move_human_later.append((hi, dir))
    return dir


# rest, left or right
def do_state_101(g, hi):
    _, y = g.human_place[hi]
    my_destination = g.where_my_aisle[hi]
    # 横指定通路にいる                                                      role: 101 -> 1000
    if y == my_destination:
        g.state_2[hi] = True
        g.new_human_roles.append((hi, 1000))
        return '.'

    # まだ指定横通路にいない
    if y < my_destination:
        dir =  'R'
    else:
        dir = 'L'
    g.move_human_later.append((hi, dir))
    return dir


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

# put wall updown

# 通路(7, 15, 23)の人が独立して左右の動物を塞ぐ

def both_side_left(y):
    return y - 7, y - 1


def both_side_right(y):
    if y == 23:
        return y + 1, y + 6
    else:
        return y + 1, y + 7


def is_row_x_wall_done(g, x, ly, ry):
    wall_created = True
    for y in range(ly, ry):
        if '#' not in g.place_all[(x, y)]:
            wall_created = False
            break
    return wall_created


def is_updown_wall_done(g, x, ly, ry):
    # x = 0 なら下の壁だけcheck
    if x == 0:
        res = is_row_x_wall_done(g, x + 1, ly, ry)
    # x = 28 なら上の壁だけcheck
    elif x == 28:
        res = is_row_x_wall_done(g, x - 1, ly, ry)
    # それ以外は上下check
    else:
        res = is_row_x_wall_done(g, x - 1, ly, ry) and \
            is_row_x_wall_done(g, x + 1, ly, ry)
    return res


def check_space_left(g, x, y):
    # 左入口が壁
    if is_wall_left(g, x, y):
        return False

    # 左入口にpetがいる
    if is_pets_left(g, x, y):
        return False

    # 左入口の隣接にpetがいる
    if is_pets_adjacent(g, x, y - 1):
        return False

    # 左入口が置かれる予定である
    if (x, y - 1) in g.put_wall_later:
        return False

    # 入口は置ける状態
    # 左spaceの上下の壁が完成していない
    # 端まで完成してなくても塞げるので端の壁は調べない閉区間？
    ly, ry = both_side_left(y)
    if not is_updown_wall_done(g, x, ly, ry):
        return False

    return True


def check_space_right(g, x, y):
    # 右入口が壁
    if is_wall_right(g, x, y):
        return False

    # 右入口にpetがいる
    if is_pets_right(g, x, y):
        return False

    # 右入口の隣接にpetがいる
    if is_pets_adjacent(g, x, y + 1):
        return False

    # 右入口が置かれる予定である
    if (x, y + 1) in g.put_wall_later:
        return False

    # 入口は置ける状態
    # 右spaceの上下の壁が完成していない
    # 端まで完成してなくても塞げるので端の壁は調べない閉区間？
    ly, ry = both_side_right(y)
    if not is_updown_wall_done(g, x, ly + 1, ry + 1):
        return False

    return True


def count_space_pet_left(g, x, y):
    count_ = 0
    ly, ry = both_side_left(y)
    for sy in range(ly, ry - 1):
        count_ += count_pets_xy(g, x, sy)
    if x == 28:
        if y == 7:
            for sy in range(ly, ry):
                count_ += count_pets_xy(g, x + 1, sy)
        else:
            for sy in range(ly + 1, ry):
                count_ += count_pets_xy(g, x + 1, sy)
    return count_


def count_space_pet_right(g, x, y):
    count_ = 0
    ly, ry = both_side_right(y)
    for sy in range(ly + 2, ry + 1):
        count_ += count_pets_xy(g, x, sy)
    if x == 28:
        if y == 23:
            for sy in range(ly + 1, ry + 1):
                count_ += count_pets_xy(g, x + 1, sy)
        else:
            for sy in range(ly + 1, ry):
                count_ += count_pets_xy(g, x + 1, sy)
    return count_


def do_state_200(g, hi):
    x, y = g.human_place[hi]
    if x == 0:
        g.state_200_dir[hi] = 'D'
    if x in (28, 29):
        g.state_200_dir[hi] = 'U'

    # 奇数rowなら上下移動
    if x % 2 == 1:
        dir = g.state_200_dir[hi]
        g.move_human_later.append((hi, dir))
        return dir

    # 両側壁か
    wall_left = is_wall_left(g, x, y)
    wall_right = is_wall_right(g, x, y)
    # 両側壁が置かれる予定か (x, y) in g.put_wall_later
    next_put_wall_left = (x, y - 1) in g.put_wall_later
    next_put_wall_right = (x, y + 1) in g.put_wall_later

    # 左が壁か次置かれる予定 and 右が壁か次置かれる予定 なら上下移動
    if (wall_left or next_put_wall_left) and (wall_right or next_put_wall_right):
        dir = g.state_200_dir[hi]
        g.move_human_later.append((hi, dir))
        return dir

    # 人がかつていたrowの x = (2, 6, 10, 14, 18, 22, 26, 28) でまだ終わってなかったら上下移動
    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, y - 1) not in g.no_human:
            dir = g.state_200_dir[hi]
            g.move_human_later.append((hi, dir))
            return dir

    # 壁が完成してるか,入口に壁あるか,壁が置かれる予定であるか,壁の隣接のpetがいるかをcheck
    can_put_left = check_space_left(g, x, y)
    can_put_right = check_space_right(g, x, y)

    # 両方置けないなら上下移動
    if (not can_put_left) and (not can_put_right):
        dir = g.state_200_dir[hi]
        g.move_human_later.append((hi, dir))
        return dir

    # 両側のpetの数を調べる(3以上先)
    number_pet_left = count_space_pet_left(g, x, y)
    number_pet_right = count_space_pet_right(g, x, y)

    # 両方とも置けるなら
    if can_put_left and can_put_right:

        # petが両方ともいない
        if (not number_pet_left) and (not number_pet_right):
            # 自分の所,自分の隣接にpetがいるなら待機
            if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
                return '.'
            # 周辺にもいないなら上下移動
            dir = g.state_200_dir[hi]
            g.move_human_later.append((hi, dir))
            return dir

        # petが両方にいる
        elif number_pet_left and number_pet_right:
            # petが多い方に壁を置く
            if number_pet_left >= number_pet_right:
                res = 'l'
                g.put_wall_later.add((x, y - 1))
            else:
                res = 'r'
                g.put_wall_later.add((x, y + 1))
            return res

        # petが左だけいるなら左に壁を置く
        elif number_pet_left:
            res = 'l'
            g.put_wall_later.add((x, y - 1))
            return res

        # petが右だけいる右に壁を置く
        elif number_pet_right:
            res = 'r'
            g.put_wall_later.add((x, y + 1))
            return res

    # 左だけ置けるなら
    if can_put_left:
        # petがいれば左に置く
        if number_pet_left:
            res = 'l'
            g.put_wall_later.add((x, y - 1))
            return res

        # petがいなければ
        # 自分の所,自分の隣接にpetがいるなら待機
        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        # 周辺にもいないなら上下移動
        dir = g.state_200_dir[hi]
        g.move_human_later.append((hi, dir))
        return dir

    # 右だけ置けるなら
    if can_put_right:
        # petがいれば右に置く
        if number_pet_right:
            res = 'r'
            g.put_wall_later.add((x, y + 1))
            return res

        # petがいなければ
        # 自分の所,自分の隣接にpetがいるなら待機
        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        # 周辺にもいないなら上下移動
        dir = g.state_200_dir[hi]
        g.move_human_later.append((hi, dir))
        return dir

    # ここにはこないはず
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


# to 200
def do_state_1000(g, hi):
    g.new_human_roles.append((hi, 200))
    return '.'


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


def do_each_roles(g):
    res = ['.'] * g.m

    # must
    # 動くとき             g.move_human_later.append((hi, dir))
    # roleをupdateするとき g.new_human_roles.append((hi, role))
    # 壁を置くとき         g.put_wall_later.add((x, y))

    for i in range(g.m):
        role = g.roles[i]
        # roleを付与する                                                 0 -> 1,2,3, 100,101,1000
        if role == 0:
            next_move = '.'

        # 上5人,縦目的地row_xに行く                                              1 -> 2, 3
        elif role == 1:
            next_move = do_state_1(g, i)
        # 上5人,左右近い方の壁(0, 29)に移動                                      2 -> 3
        elif role == 2:
            next_move = do_state_2(g, i)
        # 全員縦移動が終わってるかcheckしてokなら次へ                             3 -> 4
        elif role == 3:
            next_move = do_state_3(g, i)
        # 上下に壁を置きながら端まで行く                                          4 -> 5
        elif role == 4:
            next_move = do_state_4(g, i)
        # 7 or 23 の近い方の通路に出る                                           5 -> 6
        elif role == 5:
            next_move = do_state_5(g, i)
        # 通路に出たので1,2,2人に次の行き先を付与                            6 -> 10(上1人), 20,21(次2人), 50,51(次2人)
        elif role == 6:
            next_move = do_state_6(g, i)

        # top1 x=28まで行く                                                       10 -> 11
        elif role == 10:
            next_move = do_state_10(g, i)
        # x=28に着いてるのでy=6,24に行く                                           11 -> 12
        elif role == 11:
            next_move = do_state_11(g, i)
        # 下に6つ壁を置きながら反対に移動                                           12 -> 13
        elif role == 12:
            next_move = do_state_12(g, i)
        # 壁を置き終わったので通路(7, 23)に移動               　                     13 -> 14
        elif role == 13:
            next_move = do_state_13(g, i)
        # 通路に出たので1000へ                                                      14 -> 1000
        elif role == 14:
            next_move = do_state_14(g, i)


        # top2 x=22まで行く                                                      20,21 -> 22,23
        elif role in (20, 21):
            next_move = do_state_20_21(g, i, role)
        # role=20は左端,21は右端に移動                                           22,23 -> 24,25
        elif role in (22, 23):
            next_move = do_state_22_23(g, i, role)
        # 上下に壁を置きながら中央まで行く機                                      24,25 -> 26,27
        elif role in (24, 25):
            next_move = do_state_24_25(g, i, role)
        # y=7に移動して28へ       　　　　　　　　　　　　　　　　　　　　　　　　   26 -> 28
        elif role == 26:
            next_move = do_state_26(g, i)
        # 中央の人はすぐ1000へ　　　　                        　　　　　　　　　　  27 -> 1000
        elif role == 27:
            next_move = do_state_27(g, i)
        # 路に出たので1000へ                                                      28 -> 1000
        elif role == 28:
            next_move = do_state_28(g, i)


        # under2 x=26まで行く                                                  50,51 -> 52,53
        elif role in (50, 51):
            next_move = do_state_50_51(g, i, role)
        # role=50は左端,51は右端に移動                                          52,53 -> 54,55
        elif role in (52, 53):
            next_move = do_state_52_53(g, i, role)
        # 上下に壁を置きながら中央まで行く機                                      54,55 -> 56,57
        elif role in (54, 55):
            next_move = do_state_54_55(g, i, role)
        # y=23に移動して58へ       　　　　　　　　　　　　　　　　　　　　　　　　   56 -> 58
        elif role == 56:
            next_move = do_state_56(g, i)
        # 中央の人はすぐ1000へ　　　　                        　　　　　　　　　　  57 -> 1000
        elif role == 57:
            next_move = do_state_57(g, i)
        # 路に出たので1000へ                                                      58 -> 1000
        elif role == 58:
            next_move = do_state_58(g, i)


        # 余り,縦目的地row_xに移動       　                                    　100 -> 101,1000
        elif role == 100:
            next_move = do_state_100(g, i)
        # 余り,左右目的地col_yに移動       　                                    101 -> 1000
        elif role == 101:
            next_move = do_state_101(g, i)


        # 上下に個々が動いてokなら壁で動物を塞ぐ
        elif role == 200:
            next_move = do_state_200(g, i)


        # 200に飛ばす
        elif role == 1000:
            next_move = do_state_1000(g, i)

        # それ以外は一旦何もしない                                               1000 ~
        else:
            next_move = '.'

        res[i] = next_move

    return ''.join(res)


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


# pets : i, human : -i, 1-indexed
def erase_place(g, x, y, i):
    g.place_all[(x, y)].remove(i)
    if not g.place_all[(x, y)]:
        del g.place_all[(x, y)]


# pets : i, human : -i, 1-indexed
def update_place(g, x, y, i):
    if i > 0:
        g.pets_place[i - 1] = (x, y)
    else:
        g.human_place[-i - 1] = (x, y)
    g.place_all[(x, y)].append(i)


def move_human(g):
    for i, dir in g.move_human_later:
        x, y = g.human_place[i]
        erase_place(g, x, y, -(i + 1))
        nx, ny = get_next_xy(x, y, dir)
        update_place(g, nx, ny, -(i + 1))


def change_human_roles(g):
    for i, new_role in g.new_human_roles:
        pre_role = g.roles[i]
        g.done_roles_count[pre_role] -= 1
        g.roles[i] = new_role
        g.done_roles.add(new_role)
        g.done_roles_count[new_role] += 1


def update_no_human_place(g):
    for x, y in g.no_human_later:
        g.no_human.add((x, y))


def update_put_wall(g):
    for x, y in g.put_wall_later:
        g.place_all[(x, y)].append('#')


def move_pets(g, next_pets_move):
    for i, dir in enumerate(next_pets_move):
        x, y = g.pets_place[i]
        erase_place(g, x, y, i + 1)
        for d in dir:
            x, y = get_next_xy(x, y, d)
        update_place(g, x, y, i + 1)


# old ----------------------------------------------------------------
import random
class Global_3:
    def __init__(self, n, pets_xyk, m, human_xy):
        self.n = n
        self.pets_xyk = pets_xyk
        self.m = m
        self.human_xy = human_xy

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

    def get_next_xy(self, x, y, dir):
        if dir == 'U':
            return x - 1, y
        elif dir == 'D':
            return x + 1, y
        elif dir == 'L':
            return x, y - 1
        else:
            return x, y + 1

    def erase_place(self, x, y, i):
        self.place_all[(x, y)].remove(i)
        if not self.place_all[(x, y)]:
            del self.place_all[(x, y)]

    def update_place(self, x, y, i):
        if i > 0:
            self.pets_place[i] = (x, y)
        else:
            self.human_place[-i] = (x, y)
        self.place_all[(x, y)].append(i)

    def is_pets_adjacent(self, x, y):
        for dx, dy in zip((0, 1, 0, -1), (1, 0, -1, 0)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < W):
                continue
            for i in range(1, self.n + 1):
                if i in self.place_all[(nx, ny)]:
                    return True
        return False

    def move_human(self):
        res = [None] * self.m
        if not self.is_all_human_reach_the_row:
            human_xi = sorted((x, i) for i, (x, _) in enumerate(self.human_place[1:], 1))

            for (now_x, i), dest_x in zip(human_xi, self.human_row_destination[1:]):
                if now_x == dest_x:
                    res[i - 1] = '.'
                    continue
                if now_x < dest_x:
                    res[i - 1] = 'D'
                    dir = 'D'
                else:
                    res[i - 1] = 'U'
                    dir = 'U'
                x, y = self.human_place[i]
                self.erase_place(x, y, -i)
                x, y = self.get_next_xy(x, y, dir)
                self.update_place(x, y, -i)

            h_now_xs = sorted(x for x, _ in self.human_place[1:])
            if h_now_xs == self.human_row_destination[1:]:
                self.is_all_human_reach_the_row = True

        else:
            for i, (x, y) in enumerate(self.human_place[1:], 1):
                if y == 0 and '#' in self.place_all[(x - 1, y)]:
                    self.is_human_col_left[i] = True

                if y == W - 1 and '#' in self.place_all[(x - 1, y)]:
                    self.is_human_col_right[i] = True

                if self.is_human_col_left[i] and self.is_human_col_right[i]:
                    res[i - 1] = '.'
                    continue

                if not self.is_human_col_left[i]:
                    if self.place_all[(x - 1, y)]:
                        if '#' not in self.place_all[(x - 1, y)]:
                            res[i - 1] = '.'
                        else:
                            res[i - 1] = 'L'
                            self.erase_place(x, y, -i)
                            x, y = self.get_next_xy(x, y, 'L')
                            self.update_place(x, y, -i)
                    else:
                        if self.is_pets_adjacent(x - 1, y):
                            res[i - 1] = '.'
                        else:
                            res[i - 1] = 'u'
                            self.place_all[(x - 1, y)].append('#')
                    continue

                if self.place_all[(x - 1, y)]:
                    if '#' not in self.place_all[(x - 1, y)]:
                        res[i - 1] = '.'
                    else:
                        res[i - 1] = 'R'
                        self.erase_place(x, y, -i)
                        x, y = self.get_next_xy(x, y, 'R')
                        self.update_place(x, y, -i)
                else:
                    if self.is_pets_adjacent(x - 1, y):
                        res[i - 1] = '.'
                    else:
                        res[i - 1] = 'u'
                        self.place_all[(x - 1, y)].append('#')
        return ''.join(res)

    def move_pets(self, nxt_pets_move):
        for i, dir in enumerate(nxt_pets_move, 1):
            x, y = self.pets_place[i]
            self.erase_place(x, y, i)
            for d in dir:
                x, y = self.get_next_xy(x, y, d)
            self.update_place(x, y, i)


# old ----------------------------------------------------------------


def main():
    n = int(input())
    pets_xyk = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(n)]
    m = int(input())
    human_xy = [tuple(map(lambda x: int(x) - 1, input().split())) for _ in range(m)]
    if n / m >= 2.4:
        g = Global_3(n, pets_xyk, m, human_xy)
        g.set_place()
        for _ in range(T):
            res = g.move_human()
            print(res, flush=True)

            nxt_pets_move = input().split()
            g.move_pets(nxt_pets_move)
        return

    # don't erase------------------------------------------------------
    g = Global_4(n, pets_xyk, m, human_xy)
    g.set_all_place()
    g.initial_set_roles()
    for _ in range(T):
        g.reset_for_next()

        res = do_each_roles(g)

        move_human(g)
        change_human_roles(g)
        update_no_human_place(g)
        update_put_wall(g)

        print(res, flush=True)
        next_pets_move = input().split()
        move_pets(g, next_pets_move)
    # don't erase------------------------------------------------------


if __name__ == '__main__':
    main()