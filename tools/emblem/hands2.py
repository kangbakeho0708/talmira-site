"""일곱 손 2판: 한눈에 시각이 읽히게. 공통 수평선 + 해의 높이와 자리 + 손의 방향 (해를 들어 올림 / 받침 / 끌어올림 / 내려놓음 / 땅 밑에서 쥠 / 주먹 / 별)"""
import json, math
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from emb import circ, ring, kite, crescent, star4, tear, cut, to_d
from emb3 import wing, thick, mir
from hands import arcfinger, haru

def hand_local(r, open_=True):
    """해 가운데 (0,0), 반지름 r 을 아래에서 받치는 손. 손목은 +y 쪽"""
    palm = Polygon([(-8.5, r + 4), (-10.5, r + 12), (-7.5, r + 30), (-6, r + 36), (6, r + 36), (7.5, r + 30), (10.5, r + 12), (8.5, r + 4)])
    if open_:
        f = unary_union([arcfinger((0, 0), r + 3.4, 62, -24, 5), arcfinger((0, 0), r + 7.6, 72, -4, 4.6), arcfinger((0, 0), r + 3.4, 118, 204, 5), arcfinger((0, 0), r + 7.6, 108, 184, 4.6)])
    else:
        f = Point(0, 0).buffer(0)
    thumb = arcfinger((0, r + 18), 13, 160, 232, 5)
    cuff = box(-8, r + 32, 8, r + 36.5)
    h = unary_union([palm, f, thumb]).difference(thick([(0, r + 14), (0, r + 26)], .8))
    return unary_union([h.difference(cuff.buffer(1)), cuff])

def place(g, ang, pos):
    return affinity.translate(affinity.rotate(g, ang, origin=(0, 0)), pos[0], pos[1])

def sunshape(c, r, rays=12, long=9, kind='full', upper_only=False):
    core = circ(c, r) if kind == 'full' else ring(c, r - 3.6, r)
    rs = []
    for k in range(rays):
        a = k * 360 / rays
        if upper_only and not (180 <= a <= 360): continue
        rs.append(kite(c, a, r + 2.2, r + (long if k % 2 == 0 else long * .65), 3 if k % 2 == 0 else 2.2))
    return unary_union([core] + rs)

def horizon(y, x0=10, x1=90): return box(x0, y - 1.3, x1, y + 1.3)

def orn(kind, at, ang):
    s = []
    if kind == 'wing':
        for sd in (1, -1): s.append(affinity.scale(wing((52, 40), (76, 18), (56, 54), 4, 3, sd), .5, .5, origin=(50, 40)))
        g = affinity.translate(unary_union(s), -50, -40 + 2)
    elif kind == 'ear':
        g = unary_union([Polygon([(sd * 9, 2), (sd * 19, -17), (sd * 15, 4)]) for sd in (1, -1)])
    elif kind == 'tuft':
        g = unary_union([kite((sd * 9, 0), -90 + sd * 35, 0, 14, 4.4, .5) for sd in (1, -1)])
    elif kind == 'fur':
        g = unary_union([kite((sd * 8.5, k * 2), (-35 - 25 * k) if sd > 0 else (215 + 25 * k), 0, 9 - k * 2, 3.4, .3) for sd in (1, -1) for k in range(3)])
    else:  # fin
        g = unary_union([kite((sd * 8.5, 0), -20 if sd > 0 else 200, 0, 12, 4.8, .5) for sd in (1, -1)])
    return place(g, ang, at)

def h0():  # 한낮: 해가 맨 위, 손이 곧게 들어 올림. 빛살 열둘. 매 날개 크게
    r = 11; sc = (50, 22)
    hd = place(hand_local(r), 0, sc)
    sun = sunshape(sc, r, 12, 10)
    hz = horizon(86, 18, 82)
    o = orn('wing', (50, sc[1] + r + 34), 0)
    o = affinity.scale(o, 1.5, 1.5, origin=(50, sc[1] + r + 34))
    return unary_union([cut(unary_union([sun, hz, o]), hd, 1.6), hd])

def h1():  # 정오: 해가 높지만 기울어 있음, 손이 비스듬히 받침
    r = 10.5; sc = (62, 26)
    hd = place(hand_local(r), 28, sc)
    sun = sunshape(sc, r, 8, 8)
    hz = horizon(84, 14, 86)
    o = orn('ear', place(Point(0, r + 34), 28, sc).coords[0], 28)
    shadow = box(30, 85.5, 46, 87.5)  # 짧은 그림자
    return unary_union([cut(unary_union([sun, hz, o]), hd, 1.6), hd, shadow])

def h2():  # 아침: 수평선 왼쪽에서 반쯤 떠오르는 해, 손이 아래에서 밀어 올림
    r = 11; sc = (40, 59); hy = 56
    sun = sunshape(sc, r, 12, 9, upper_only=True).intersection(box(0, 0, 100, hy - 1.4))
    hd = place(hand_local(r), 0, sc)
    hz = horizon(hy)
    o = orn('wing', place(Point(0, r + 34), 0, sc).coords[0], 0)
    return unary_union([cut(unary_union([sun, hz]), hd, 1.6), hd, cut(o, hd, 1)])

def h3():  # 노을: 수평선 오른쪽에 반쯤 잠긴 해, 손이 위에서 내려 눌러 놓음
    r = 11; sc = (62, 58); hy = 58
    sun = sunshape(sc, r, 12, 9, kind='ring').intersection(box(0, 0, 100, hy - 1.4))
    hd = place(hand_local(r), 180, sc)
    hz = horizon(hy)
    o = orn('wing', place(Point(0, r + 34), 180, sc).coords[0], 180)
    refl = unary_union([box(sc[0] - 10 + k * 2, hy + 5 + k * 5, sc[0] + 10 - k * 2, hy + 6.6 + k * 5) for k in range(3)])
    return unary_union([cut(unary_union([sun, hz, refl]), hd, 1.6), hd, cut(o, hd, 1)])

def h4():  # 황혼: 해는 수평선 아래, 위로는 빛 띠만. 손이 위에서 수평선을 넘어 아래의 해를 쥠
    r = 10; sc = (50, 66); hy = 52
    glow = unary_union([kite((50, hy), a, 4, 16 if k % 2 == 0 else 11, 2.6) for k, a in enumerate(range(-170, -9, 20))])
    sun = ring(sc, r - 3.4, r)
    hd = place(hand_local(r), 180, sc)
    hz = horizon(hy)
    o = orn('tuft', place(Point(0, r + 34), 180, sc).coords[0], 180)
    moon = crescent((76, 22), 6, -3, 1.4, .9)
    return unary_union([cut(unary_union([glow, hz, sun]), hd, 1.6), hd, cut(o, hd, 1), moon])

def h5():  # 새벽: 해 없음. 수평선 위로 주먹, 손가락 틈으로 새는 가는 빛
    hy = 70
    fist = unary_union([Polygon([(38, 66), (38, 44), (62, 44), (62, 66)]).buffer(3)] + [circ((40.5 + k * 6.3, 44), 3.6) for k in range(4)])
    gaps = unary_union([thick([(43.6 + k * 6.3, 42), (43.6 + k * 6.3, 54)], 1) for k in range(3)])
    thumb = arcfinger((44, 60), 10, 150, 250, 5.2)
    f = unary_union([fist, thumb]).difference(gaps)
    wrist = box(42, 66, 58, 80); cuff = box(41, 76, 59, 80.5)
    f = unary_union([f, wrist.difference(cuff.buffer(1)), cuff])
    leak = unary_union([kite((43.6 + k * 6.3, 42), -90 + (k - 1) * 12, 0, 22 - abs(k - 1) * 4, 2.4, .2) for k in range(3)])
    hz = horizon(hy)
    o = orn('fur', (50, 78), 0)
    return unary_union([cut(hz, f, 1.6), f, leak, cut(o, f, 1)])

def h6():  # 자정: 해가 없는 하늘. 위에서 내려온 손이 별 하나를 받쳐 듦 (빈 해 고리는 땅 밑)
    r = 9; sc = (50, 50)
    st = star4(sc, 10, .22)
    hd = place(hand_local(r), 180, sc)
    hz = horizon(82, 14, 86)
    empty = ring((50, 92), 6.6, 8.6).intersection(box(0, 83.5, 100, 100))
    o = orn('fin', place(Point(0, r + 34), 180, sc).coords[0], 180)
    stars = unary_union([star4(p, 2.6, .3) for p in [(22, 30), (78, 34), (30, 66), (72, 68)]])
    return unary_union([cut(unary_union([st, hz, empty]), hd, 1.6), hd, cut(o, hd, 1), stars])

res = {f'hand{i}': to_d(f().simplify(.12)) for i, f in enumerate([h0, h1, h2, h3, h4, h5, h6])}
res['haru'] = to_d(haru().simplify(.12))
json.dump(res, open('hands.json', 'w'))
print('ok')
