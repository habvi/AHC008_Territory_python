from collections import defaultdict

W = 30
T = 300

class Global_4:
    def __init__(self, n, pets_xyk, m, human_xy):
        self.n = n
        self.pets_xyk = pets_xyk
        self.m = m
        self.human_xy = human_xy
        self.roles = [0] * self.m
        self.top5_row_destination = [2, 6, 10, 14, 18]
        self.col_aisle = [7, 15, 23]
        self.move_human_later = {}
        self.new_human_roles = []
        self.done_roles = set()
        self.done_roles_count = defaultdict(int)

        self.top5_each_destination = {}
        self.state_1 = [False] * self.m
        self.state_2 = [False] * self.m
        self.state_4_left = [False] * self.m
        self.state_4_right = [False] * self.m
        self.state_6_roles = set()
        self.state_12_left = False
        self.state_12_right = False
        self.state_12_wall_y = set([6, 8, 14, 16, 22, 24])
        self.state_200_dir = ['U'] * self.m

        self.number_of_each_aisle = defaultdict(int)
        self.who_each_aisle = defaultdict(list)
        self.where_my_aisle = defaultdict(int)
        self.no_human = set()
        self.no_human_later = []
        self.put_wall_later = set()

        self.pair_left_number = 0
        self.pair_right_number = 0
        self.pair_list = []
        self.already_pair = set()
        self.pair_next_move = []
        self.pair_state = defaultdict(int)
        self.pair_meet_x = defaultdict(int)
        self.pair_dir = defaultdict(lambda : 'U')


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
        for i, (x, y, hi) in enumerate(human_xyi[:5]):
            my_destination = self.top5_row_destination[i]
            self.top5_each_destination[hi] = my_destination
            if x != my_destination:
                _set_roles(hi, 1)
                if y in (0, 29):
                    self.state_2[hi] = True
            else:
                self.state_1[hi] = True
                if y not in (0, 29):
                    _set_roles(hi, 2)
                else:
                    self.state_2[hi] = True
                    _set_roles(hi, 3)


        def _set_col_aisle(hi, place):
            self.number_of_each_aisle[place] += 1
            self.who_each_aisle[place].append(hi)
            self.where_my_aisle[hi] = place


        x, y, hi = human_xyi[0]
        left, middle, right = self.col_aisle
        if y < 15:
            _set_col_aisle(hi, left)
        else:
            _set_col_aisle(hi, right)


        def _assign_rest_human(hi, x, y, place):
            if x % 2 == 1:
                _set_roles(hi, 100)
                if y == place:
                    self.state_2[hi] = True
            else:
                self.state_1[hi] = True
                if y != place:
                    _set_roles(hi, 101)
                else:
                    self.state_2[hi] = True
                    _set_roles(hi, 1000)


        rest_human = human_xyi[5:]
        rest_human.sort(key=lambda x: x[1])
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
        elif len(rest_human) == 3:
            for place, (x, y, hi) in zip([left, middle, right], rest_human):
                _set_col_aisle(hi, place)
                _assign_rest_human(hi, x, y, place)
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
        self.move_human_later = {}
        self.new_human_roles = []
        self.no_human_later = []
        self.put_wall_later = set()
        self.pair_next_move = []


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


def do_state_1(g, hi):
    x, y = g.human_place[hi]
    dest_x = g.top5_each_destination[hi]

    if x == dest_x:
        g.state_1[hi] = True
        if y not in (0, 29):
            g.new_human_roles.append((hi, 2))
        else:
            g.state_2[hi] = True
            g.new_human_roles.append((hi, 3))
        return '.'

    if x < dest_x:
        dir = 'D'
    else:
        dir = 'U'
    g.move_human_later[hi] = dir
    return dir


def do_state_2(g, hi):
    _, y = g.human_place[hi]

    if y in (0, 29):
        g.state_2[hi] = True
        g.new_human_roles.append((hi, 3))
        return '.'

    if y < 15:
        dir =  'L'
    else:
        dir = 'R'
    g.move_human_later[hi] = dir
    return dir


def do_state_3(g, hi):
    if all(g.state_1):
        g.new_human_roles.append((hi, 4))
    return '.'


def do_state_4(g, hi):
    x, y = g.human_place[hi]
    wall_up = is_wall_up(g, x, y)
    wall_down = is_wall_down(g, x, y)

    if y == 0 and wall_up and wall_down:
        g.state_4_left[hi] = True

    if y == 29 and wall_up and wall_down:
        g.state_4_right[hi] = True

    l_fin, r_fin = g.state_4_left[hi], g.state_4_right[hi]
    if l_fin and r_fin:
        g.new_human_roles.append((hi, 5))
        return '.'

    if (wall_up and wall_down) or (y in g.col_aisle):
        if l_fin:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later[hi] = dir
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


def do_state_5(g, hi):
    x, y = g.human_place[hi]
    if y in (7, 23):
        g.new_human_roles.append((hi, 6))
        return '.'

    if y < 7:
        dir = 'R'
    elif 23 < y:
        dir = 'L'
    g.move_human_later[hi] = dir
    return dir


def do_state_6(g, hi):
    x, y = g.human_place[hi]

    for py in (6, 8, 14, 16, 22, 24):
        g.no_human_later.append((x, py))

    if x == 2:
        g.new_human_roles.append((hi, 10))
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


def do_state_10(g, hi):
    x, y = g.human_place[hi]
    if x == 28:
        g.new_human_roles.append((hi, 11))
        res = '.'
    else:
        res = 'D'
        g.move_human_later[hi] = res
    return res


def do_state_11(g, hi):
    x, y = g.human_place[hi]
    if y in (6, 24):
        g.new_human_roles.append((hi, 12))
        res = '.'
    else:
        if y == 7:
            res = 'L'
        else:
            res = 'R'
        g.move_human_later[hi] = res
    return res


def do_state_12(g, hi):
    x, y = g.human_place[hi]

    wall_down = is_wall_down(g, x, y)
    if y == 6 and wall_down:
        g.state_12_left = True
    if y == 24 and wall_down:
        g.state_12_right = True

    if g.state_12_left and g.state_12_right:
        g.new_human_roles.append((hi, 13))
        return '.'

    if (wall_down) or (y not in g.state_12_wall_y):
        if g.state_12_left:
            dir = 'R'
        else:
            dir = 'L'
        g.move_human_later[hi] = dir
        return dir

    something_down = g.place_all[(x + 1, y)]
    if not something_down and not is_pets_adjacent(g, x + 1, y):
        res = 'd'
        g.put_wall_later.add((x + 1, y))
    else:
        res = '.'
    return res


def do_state_13(g, hi):
    x, y = g.human_place[hi]
    if y == 6:
        dir = 'R'
    else:
        dir = 'L'
    g.move_human_later[hi] = dir
    g.new_human_roles.append((hi, 14))
    return dir


def do_state_14(g, hi):
    x, y = g.human_place[hi]

    for py in (6, 8, 14, 16, 22, 24):
        g.no_human_later.append((x, py))

    g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------


def do_state_20_21(g, hi, role):
    x, y = g.human_place[hi]
    if x == 22:
        g.new_human_roles.append((hi, role + 2))
        return '.'

    dir = 'D'
    g.move_human_later[hi] = dir
    return dir


def do_state_22_23(g, hi, role):
    x, y = g.human_place[hi]

    if y in (0, 29):
        g.new_human_roles.append((hi, role + 2))
        return '.'

    if role == 22:
        dir = 'L'
    else:
        dir = 'R'
    g.move_human_later[hi] = dir
    return dir


def do_state_24_25(g, hi, role):
    x, y = g.human_place[hi]

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
        g.move_human_later[hi] = dir
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


def do_state_26(g, hi):
    x, y = g.human_place[hi]
    if y == 7:
        g.new_human_roles.append((hi, 28))
        return '.'
    dir = 'L'
    g.move_human_later[hi] = dir
    return dir


def do_state_27(g, hi):
    g.new_human_roles.append((hi, 1000))
    return '.'


def do_state_28(g, hi):
    x, y = g.human_place[hi]
    if (26 in g.done_roles) and (27 in g.done_roles):
        for py in (6, 8, 14, 16, 22, 24):
            g.no_human_later.append((x, py))
        g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------


def do_state_50_51(g, hi, role):
    x, y = g.human_place[hi]
    if x == 26:
        g.new_human_roles.append((hi, role + 2))
        return '.'
    dir = 'D'
    g.move_human_later[hi] = dir
    return dir


def do_state_52_53(g, hi, role):
    x, y = g.human_place[hi]
    if y in (0, 29):
        g.new_human_roles.append((hi, role + 2))
        return '.'
    if role == 52:
        dir = 'L'
    else:
        dir = 'R'
    g.move_human_later[hi] = dir
    return dir


def do_state_54_55(g, hi, role):
    x, y = g.human_place[hi]

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
        g.move_human_later[hi] = dir
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


def do_state_56(g, hi):
    x, y = g.human_place[hi]
    if y == 23:
        g.new_human_roles.append((hi, 58))
        return '.'
    dir = 'R'
    g.move_human_later[hi] = dir
    return dir


def do_state_57(g, hi):
    g.new_human_roles.append((hi, 1000))
    return '.'


def do_state_58(g, hi):
    x, y = g.human_place[hi]
    if (56 in g.done_roles) and (57 in g.done_roles):
        for py in (6, 8, 14, 16, 22, 24):
            g.no_human_later.append((x, py))
        g.new_human_roles.append((hi, 1000))
    return '.'


# ----------------------------------------------------------------------------------------------------


def do_state_100(g, hi):
    x, y = g.human_place[hi]

    if x % 2 == 0:
        g.state_1[hi] = True
        if y != g.where_my_aisle[hi]:
            g.new_human_roles.append((hi, 101))
        else:
            g.state_2[hi] = True
            g.new_human_roles.append((hi, 1000))
        return '.'

    dir = 'U'
    g.move_human_later[hi] = dir
    return dir


def do_state_101(g, hi):
    _, y = g.human_place[hi]
    my_destination = g.where_my_aisle[hi]
    if y == my_destination:
        g.state_2[hi] = True
        g.new_human_roles.append((hi, 1000))
        return '.'

    if y < my_destination:
        dir =  'R'
    else:
        dir = 'L'
    g.move_human_later[hi] = dir
    return dir


# ----------------------------------------------------------------------------------------------------


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
    if x == 0:
        res = is_row_x_wall_done(g, x + 1, ly, ry)
    elif x == 28:
        res = is_row_x_wall_done(g, x - 1, ly, ry)
    else:
        res = is_row_x_wall_done(g, x - 1, ly, ry) and \
            is_row_x_wall_done(g, x + 1, ly, ry)
    return res


def check_space_left(g, x, y):
    if is_wall_left(g, x, y):
        return False

    if is_pets_left(g, x, y):
        return False

    if is_pets_adjacent(g, x, y - 1):
        return False

    if (x, y - 1) in g.put_wall_later:
        return False

    ly, ry = both_side_left(y)
    if not is_updown_wall_done(g, x, ly, ry):
        return False

    return True


def check_space_right(g, x, y):
    if is_wall_right(g, x, y):
        return False

    if is_pets_right(g, x, y):
        return False

    if is_pets_adjacent(g, x, y + 1):
        return False

    if (x, y + 1) in g.put_wall_later:
        return False

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

    if x % 2 == 1:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    wall_left = is_wall_left(g, x, y)
    wall_right = is_wall_right(g, x, y)

    next_put_wall_left = (x, y - 1) in g.put_wall_later
    next_put_wall_right = (x, y + 1) in g.put_wall_later

    if (wall_left or next_put_wall_left) and (wall_right or next_put_wall_right):
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, y - 1) not in g.no_human:
            dir = g.state_200_dir[hi]
            g.move_human_later[hi] = dir
            return dir

    can_put_left = check_space_left(g, x, y)
    can_put_right = check_space_right(g, x, y)

    if (not can_put_left) and (not can_put_right):
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    number_pet_left = count_space_pet_left(g, x, y)
    number_pet_right = count_space_pet_right(g, x, y)

    if can_put_left and can_put_right:
        if (not number_pet_left) and (not number_pet_right):
            if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
                return '.'
            dir = g.state_200_dir[hi]
            g.move_human_later[hi] = dir
            return dir

        elif number_pet_left and number_pet_right:
            if number_pet_left >= number_pet_right:
                res = 'l'
                g.put_wall_later.add((x, y - 1))
            else:
                res = 'r'
                g.put_wall_later.add((x, y + 1))
            return res

        elif number_pet_left:
            res = 'l'
            g.put_wall_later.add((x, y - 1))
            return res

        elif number_pet_right:
            res = 'r'
            g.put_wall_later.add((x, y + 1))
            return res

    if can_put_left:
        if number_pet_left:
            res = 'l'
            g.put_wall_later.add((x, y - 1))
            return res

        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    if can_put_right:
        if number_pet_right:
            res = 'r'
            g.put_wall_later.add((x, y + 1))
            return res

        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    return '.'



# ----------------------------------------------------------------------------------------------------


def do_pair_state_0(g, h1, h2):
    x1, y1 = g.human_place[h1]
    x2, y2 = g.human_place[h2]

    if x1 == x2 and 7 in (y1, y2):
        assign_pair_state_left(g, h1, h2)
        return
    if x1 == x2 and 23 in (y1, y2):
        assign_pair_state_right(g, h1, h2)
        return

    mx = g.pair_meet_x[h1]

    for x, hi in zip((x1, x2), (h1, h2)):
        if x == mx:
            continue
        if x < mx:
            dir = 'D'
        elif x > mx:
            dir = 'U'
        g.pair_next_move.append((hi, dir))
        g.move_human_later[hi] = dir


# yet
def do_pair_state_1(g, h1, h2):
    return


def check_space_middle(g, x, l, r):
    if is_wall_xy(g, x, l) or is_wall_xy(g, x, r):
        return False
    if is_pets_xy(g, x, l) or is_pets_xy(g, x, r):
        return False
    if is_pets_adjacent(g, x, l) or is_pets_adjacent(g, x, r):
        return False
    if (x, l) in g.put_wall_later or (x, r) in g.put_wall_later:
        return False
    if not is_updown_wall_done(g, x, l, r):
        return False
    return True


def count_space_pet_middle(g, x, m, r):
    count_ = 0
    for sy in range(m + 2, m + 5):
        count_ += count_pets_xy(g, x, sy)
    if x == 28:
        for sy in range(m + 1, m + 6):
            count_ += count_pets_xy(g, x + 1, sy)
    return count_


def pair_put_wall_left(g, x, y1, h1, h2):
    if y1 == 7:
        g.pair_next_move.append((h1, 'l'))
    else:
        g.pair_next_move.append((h2, 'l'))
    g.put_wall_later.add((x, 6))


def pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r):
    if 7 in (y1, y2):
        if y1 == 7:
            g.pair_next_move.append((h1, 'r'))
            g.pair_next_move.append((h2, 'l'))
        else:
            g.pair_next_move.append((h1, 'l'))
            g.pair_next_move.append((h2, 'r'))
    else:
        if y1 == 15:
            g.pair_next_move.append((h1, 'r'))
            g.pair_next_move.append((h2, 'l'))
        else:
            g.pair_next_move.append((h1, 'l'))
            g.pair_next_move.append((h2, 'r'))
    g.put_wall_later.add((x, l))
    g.put_wall_later.add((x, r))


def pair_put_wall_right(g, x, y1, h1, h2):
    if y1 == 23:
        g.pair_next_move.append((h1, 'r'))
    else:
        g.pair_next_move.append((h2, 'r'))
    g.put_wall_later.add((x, 24))


def check_both_left(g, x, h1, h2):
    l, m, r = 6, 8, 14
    x1, y1 = g.human_place[h1]
    x2, y2 = g.human_place[h2]
    wall_left = is_wall_xy(g, x, l)
    wall_middle = is_wall_xy(g, x, m) and is_wall_xy(g, x, r)
    next_put_wall_left = (x, l) in g.put_wall_later
    next_put_wall_middle = (x, m) in g.put_wall_later and (x, r) in g.put_wall_later
    if (wall_left or next_put_wall_left) and (wall_middle or next_put_wall_middle):
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, l) not in g.no_human:
            dir = g.pair_dir[h1]
            for hi in (h1, h2):
                g.pair_next_move.append((hi, dir))
                g.move_human_later[hi] = dir
            return

    can_put_left = check_space_left(g, x, l + 1)
    can_put_middle = check_space_middle(g, x, m, r)
    if (not can_put_left) and (not can_put_middle):
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    number_pet_left = count_space_pet_left(g, x, l)
    number_pet_middle = count_space_pet_middle(g, x, m, r)
    if can_put_left and can_put_middle:
        if (not number_pet_left) and (not number_pet_middle):
            if is_pets_xy(g, x, 7) or is_pets_xy(g, x, 15) or \
                is_pets_adjacent(g, x, 7) or is_pets_adjacent(g, x, 15):
                return
            dir = g.pair_dir[h1]
            for hi in (h1, h2):
                g.pair_next_move.append((hi, dir))
                g.move_human_later[hi] = dir
            return
        elif number_pet_left and number_pet_middle:
            if number_pet_left >= number_pet_middle:
                pair_put_wall_left(g, x, y1, h1, h2)
            else:
                pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return
        elif number_pet_left:
            pair_put_wall_left(g, x, y1, h1, h2)
            return
        elif number_pet_middle:
            pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return

    if can_put_left:
        if number_pet_left:
            pair_put_wall_left(g, x, y1, h1, h2)
            return
        if is_pets_xy(g, x, 7) or is_pets_adjacent(g, x, 7):
            return
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    if can_put_middle:
        if number_pet_middle:
            pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return
        if is_pets_xy(g, x, 7) or is_pets_xy(g, x, 15) or \
            is_pets_adjacent(g, x, 7) or is_pets_adjacent(g, x, 15):
            return
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return


def check_both_right(g, x, h1, h2):
    l, m, r = 16, 22, 24
    x1, y1 = g.human_place[h1]
    x2, y2 = g.human_place[h2]
    wall_middle = is_wall_xy(g, x, l) and is_wall_xy(g, x, m)
    wall_right =  is_wall_xy(g, x, r)
    next_put_wall_middle = (x, l) in g.put_wall_later and (x, m) in g.put_wall_later
    next_put_wall_right = (x, r) in g.put_wall_later
    if (wall_middle or next_put_wall_middle) and (wall_right or next_put_wall_right):
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, l) not in g.no_human:
            dir = g.pair_dir[h1]
            for hi in (h1, h2):
                g.pair_next_move.append((hi, dir))
                g.move_human_later[hi] = dir
            return

    can_put_right = check_space_right(g, x, r - 1)
    can_put_middle = check_space_middle(g, x, m, r)
    if (not can_put_right) and (not can_put_middle):
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    number_pet_middle = count_space_pet_middle(g, x, m, r)
    number_pet_right = count_space_pet_right(g, x, l)
    if can_put_right and can_put_middle:
        if (not number_pet_right) and (not number_pet_middle):
            if is_pets_xy(g, x, 15) or (is_pets_xy(g, x, 23)) or \
                is_pets_adjacent(g, x, 15) or is_pets_adjacent(g, x, 23):
                return
            dir = g.pair_dir[h1]
            for hi in (h1, h2):
                g.pair_next_move.append((hi, dir))
                g.move_human_later[hi] = dir
            return
        elif number_pet_right and number_pet_middle:
            if number_pet_right >= number_pet_middle:
                pair_put_wall_right(g, x, y1, h1, h2)
            else:
                pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return
        elif number_pet_right:
            pair_put_wall_right(g, x, y1, h1, h2)
            return
        elif number_pet_middle:
            pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return

    if can_put_right:
        if number_pet_right:
            pair_put_wall_right(g, x, y1, h1, h2)
            return
        if is_pets_xy(g, x, 23) or is_pets_adjacent(g, x, 23):
            return
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    if can_put_middle:
        if number_pet_middle:
            pair_put_wall_middle(g, x, y1, y2, h1, h2, l, r)
            return
        if is_pets_xy(g, x, 15) or is_pets_xy(g, x, 23) or \
            is_pets_adjacent(g, x, 15) or is_pets_adjacent(g, x, 23):
            return
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return


def do_pair_state_2(g, h1, h2):
    x1, y1 = g.human_place[h1]
    x2, y2 = g.human_place[h2]
    x = x1
    if x == 0:
        for hi in (h1, h2):
            g.pair_dir[hi] = 'D'
    if x in (28, 29):
        for hi in (h1, h2):
            g.pair_dir[hi] = 'U'
    if x % 2 == 1:
        dir = g.pair_dir[h1]
        for hi in (h1, h2):
            g.pair_next_move.append((hi, dir))
            g.move_human_later[hi] = dir
        return

    if 7 in (y1, y2):
        check_both_left(g, x, h1, h2)
        return

    if 23 in (y1, y2):
        check_both_right(g, x, h1, h2)


def move_pair(g):
    for h1, h2 in g.pair_list:
        if g.pair_state[h1] == 1:
            do_pair_state_1(g, h1, h2)
        elif g.pair_state[h1] == 2:
            do_pair_state_2(g, h1, h2)
        elif g.pair_state[h1] == 0:
            do_pair_state_0(g, h1, h2)


# ----------------------------------------------------------------------------------------------------


def is_200_in_left(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 7 and hi not in g.already_pair:
                return True
    return False


def is_200_in_middle(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 15 and hi not in g.already_pair:
                return True
    return False


def is_200_in_right(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 23 and hi not in g.already_pair:
                return True
    return False


def get_200_id_in_left(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 7 and hi not in g.already_pair:
                return hi


def get_200_id_in_middle(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 15 and hi not in g.already_pair:
                return hi

def get_200_id_in_right(g):
    for hi, role in enumerate(g.roles):
        if role == 200:
            _, y = g.human_place[hi]
            if y == 23 and hi not in g.already_pair:
                return hi


def is_210_in_left(g):
    for hi, role in enumerate(g.roles):
        if role == 210:
            _, y = g.human_place[hi]
            if y == 7 and hi not in g.already_pair:
                return True
    return False


def is_210_in_right(g):
    for hi, role in enumerate(g.roles):
        if role == 210:
            _, y = g.human_place[hi]
            if y == 23 and hi not in g.already_pair:
                return True
    return False


def assign_pair_state_left(g, li, mi):
    if is_210_in_left(g):
        g.pair_state[li] = 1
        g.pair_state[mi] = 1
    else:
        g.pair_state[li] = 2
        g.pair_state[mi] = 2


def assign_pair_state_right(g, ri, mi):
    if is_210_in_right(g):
        g.pair_state[ri] = 1
        g.pair_state[mi] = 1
    else:
        g.pair_state[ri] = 2
        g.pair_state[mi] = 2


def set_pair_state_left(g, h1, h2):
    if h1 > h2:
        h1, h2 = h2, h1
    g.pair_list.append((h1, h2))
    g.already_pair.add(h1)
    g.already_pair.add(h2)
    g.pair_left_number += 1


def set_pair_state_right(g, h1, h2):
    if h1 > h2:
        h1, h2 = h2, h1
    g.pair_list.append((h1, h2))
    g.already_pair.add(h1)
    g.already_pair.add(h2)
    g.pair_right_number += 1


def make_pair_left(g):
    li = get_200_id_in_left(g)
    mi = get_200_id_in_middle(g)
    if li is None or mi is None:
        return

    lx, _ = g.human_place[li]
    mx, _ = g.human_place[mi]

    if lx == mx:
        g.pair_meet_x[li] = lx
        g.pair_meet_x[mi] = mx
        assign_pair_state_left(g, li, mi)
        g.new_human_roles.append((li, 280))
        g.new_human_roles.append((mi, 280))
        set_pair_state_left(g, li, mi)
        return

    x = min(lx, mx) + abs(lx - mx) // 2
    g.pair_meet_x[li] = x
    g.pair_meet_x[mi] = x

    g.new_human_roles.append((li, 250))
    g.new_human_roles.append((mi, 250))

    set_pair_state_left(g, li, mi)


def make_pair_right(g):
    ri = get_200_id_in_right(g)
    mi = get_200_id_in_middle(g)
    if ri is None or mi is None:
        return

    rx, _ = g.human_place[ri]
    mx, _ = g.human_place[mi]

    if rx == mx:
        g.pair_meet_x[ri] = rx
        g.pair_meet_x[mi] = mx
        assign_pair_state_right(g, ri, mi)
        g.new_human_roles.append((ri, 280))
        g.new_human_roles.append((mi, 280))
        set_pair_state_right(g, ri, mi)
        return

    x = min(rx, mx) + abs(rx - mx) // 2
    g.pair_meet_x[ri] = x
    g.pair_meet_x[mi] = x

    g.new_human_roles.append((ri, 250))
    g.new_human_roles.append((mi, 250))

    set_pair_state_right(g, ri, mi)


def can_make_pair(g):
    if not is_200_in_middle(g):
        return

    if (g.pair_left_number == g.pair_right_number == 0) or \
        (g.pair_left_number >= 1 and g.pair_right_number == 0):
        if is_200_in_right(g):
            make_pair_right(g)

    if g.pair_left_number == 0 and g.pair_right_number >= 1:
        if is_200_in_left(g):
            make_pair_left(g)

    if g.pair_left_number >= g.pair_right_number:
        if is_200_in_right(g):
            make_pair_right(g)
    elif g.pair_left_number < g.pair_right_number:
        if is_200_in_left(g):
            make_pair_left(g)


def merge_pair_next_move(g, res):
    for hi, next_move in g.pair_next_move:
        res[hi] = next_move
    return res


def pair_move(g, res):
    can_make_pair(g)

    if not g.pair_list:
        return res

    move_pair(g)
    res = merge_pair_next_move(g, res)

    # yet 200 -> 210 

    return res


# ----------------------------------------------------------------------------------------------------


def do_state_210_left(g, hi, x, y):
    wall_left = is_wall_left(g, x, y)
    next_put_wall_left = (x, y - 1) in g.put_wall_later

    if wall_left or next_put_wall_left:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, y - 1) not in g.no_human:
            dir = g.state_200_dir[hi]
            g.move_human_later[hi] = dir
            return dir

    can_put_left = check_space_left(g, x, y)
    if not can_put_left:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    number_pet_left = count_space_pet_left(g, x, y)
    if can_put_left:
        if number_pet_left:
            res = 'l'
            g.put_wall_later.add((x, y - 1))
            return res

        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    return '.'


def do_state_210_right(g, hi, x, y):
    wall_right = is_wall_right(g, x, y)
    next_put_wall_right = (x, y + 1) in g.put_wall_later

    if wall_right or next_put_wall_right:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    if x in (2, 6, 10, 14, 18, 22, 26, 28):
        if (x, y + 1) not in g.no_human:
            dir = g.state_200_dir[hi]
            g.move_human_later[hi] = dir
            return dir

    can_put_right = check_space_right(g, x, y)
    if not can_put_right:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    number_pet_right = count_space_pet_right(g, x, y)
    if can_put_right:
        if number_pet_right:
            res = 'r'
            g.put_wall_later.add((x, y + 1))
            return res

        if is_pets_xy(g, x, y) or is_pets_adjacent(g, x, y):
            return '.'

        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    return '.'


def do_state_210(g, hi):
    x, y = g.human_place[hi]
    if x == 0:
        g.state_200_dir[hi] = 'D'
    if x in (28, 29):
        g.state_200_dir[hi] = 'U'

    if x % 2 == 1:
        dir = g.state_200_dir[hi]
        g.move_human_later[hi] = dir
        return dir

    if y == 7:
        return do_state_210_left(g, hi, x, y)
    elif y == 23:
        return do_state_210_right(g, hi, x, y)

    return '.'


def do_state_1000(g, hi):
    g.new_human_roles.append((hi, 200))
    return '.'


# ----------------------------------------------------------------------------------------------------


def do_each_roles(g):
    res = ['.'] * g.m

    for i in range(g.m):
        role = g.roles[i]
        if role == 0:
            next_move = '.'

        elif role == 1:
            next_move = do_state_1(g, i)
        elif role == 2:
            next_move = do_state_2(g, i)
        elif role == 3:
            next_move = do_state_3(g, i)
        elif role == 4:
            next_move = do_state_4(g, i)
        elif role == 5:
            next_move = do_state_5(g, i)
        elif role == 6:
            next_move = do_state_6(g, i)
        elif role == 10:
            next_move = do_state_10(g, i)
        elif role == 11:
            next_move = do_state_11(g, i)
        elif role == 12:
            next_move = do_state_12(g, i)
        elif role == 13:
            next_move = do_state_13(g, i)
        elif role == 14:
            next_move = do_state_14(g, i)
        elif role in (20, 21):
            next_move = do_state_20_21(g, i, role)
        elif role in (22, 23):
            next_move = do_state_22_23(g, i, role)
        elif role in (24, 25):
            next_move = do_state_24_25(g, i, role)
        elif role == 26:
            next_move = do_state_26(g, i)
        elif role == 27:
            next_move = do_state_27(g, i)
        elif role == 28:
            next_move = do_state_28(g, i)
        elif role in (50, 51):
            next_move = do_state_50_51(g, i, role)
        elif role in (52, 53):
            next_move = do_state_52_53(g, i, role)
        elif role in (54, 55):
            next_move = do_state_54_55(g, i, role)
        elif role == 56:
            next_move = do_state_56(g, i)
        elif role == 57:
            next_move = do_state_57(g, i)
        elif role == 58:
            next_move = do_state_58(g, i)
        elif role == 100:
            next_move = do_state_100(g, i)
        elif role == 101:
            next_move = do_state_101(g, i)
        elif role == 200:
            next_move = do_state_200(g, i)
        elif role == 1000:
            next_move = do_state_1000(g, i)
        else:
            next_move = '.'
        res[i] = next_move

    return res


# ----------------------------------------------------------------------------------------------------


def erase_place(g, x, y, i):
    g.place_all[(x, y)].remove(i)
    if not g.place_all[(x, y)]:
        del g.place_all[(x, y)]


def update_place(g, x, y, i):
    if i > 0:
        g.pets_place[i - 1] = (x, y)
    else:
        g.human_place[-i - 1] = (x, y)
    g.place_all[(x, y)].append(i)


def move_human(g):
    for i, dir in g.move_human_later.items():
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
        return res

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

    # if n / m >= 2.6:
    #     g = Global_3(n, pets_xyk, m, human_xy)
    #     g.set_place()
    #     for _ in range(T):
    #         res = g.move_human()
    #         print(res, flush=True)

    #         nxt_pets_move = input().split()
    #         g.move_pets(nxt_pets_move)
    #     return

    g = Global_4(n, pets_xyk, m, human_xy)
    g.set_all_place()
    g.initial_set_roles()
    for i in range(T):
        g.reset_for_next()

        res = do_each_roles(g)

        res = pair_move(g, res)
        res = ''.join(res)

        move_human(g)
        change_human_roles(g)
        update_no_human_place(g)
        update_put_wall(g)

        print(res, flush=True)
        next_pets_move = input().split()
        move_pets(g, next_pets_move)


if __name__ == '__main__':
    main()