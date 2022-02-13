from random import randint

W = 30


def get_random_dir():
    return randint(0, 3)


# visualizer用 pets移動先 random生成(犬猫の追いかけはなし)
def create_nxt_pets_move(g):
    direction = 'UDLR'
    dx = (-1, 1, 0, 0)
    dy = (0, 0, -1, 1)
    
    res = []
    for (x, y), k in zip(g.pets_place[1:], g.pets_kind[1:]):
        if k == 0:
            times = 1
        elif k == 2:
            times = 3
        else:
            times = 2

        move = ''
        while times:
            i = get_random_dir()
            nx, ny = x + dx[i], y + dy[i]
            if  not (0 <= nx < W and 0 <= ny < W) or '#' in g.place_all[(nx, ny)]:
                continue
            move += direction[i]
            x += dx[i]
            y += dy[i]
            times -= 1
        res.append(move)

    return ' '.join(res)