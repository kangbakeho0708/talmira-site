"""문장 3판 (가제): 땅마다 동물 하나 (아르하 종달새, 카라드 사막여우, 세이라 바다새, 무레 부엉이, 도른 늑대, 메르한 매, 네이 고래). 2판 틀 위에"""
import json, math
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from emb import circ, ring, kite, sector, crescent, star4, tear, cut, frame, to_d, C, unknown, bond, mirase

def mir(half, cx=50):
    """오른쪽 반 점들 → 좌우 대칭 다각형 (위에서 아래로 순서)"""
    left = [(2 * cx - x, y) for x, y in reversed(half)]
    return Polygon(list(half) + left)
def feather(c, ang, L, w):  # 깃: 칼날과 같지만 끝이 둥근
    return kite(c, ang, 0, L, w, .55).buffer(.6)
def thick(pts, w): return LineString(pts).buffer(w / 2, cap_style=1, join_style=1)


def wing(shoulder, tip, back, n=5, depth=4.5, side=1):
    """한쪽 날개 (덩어리): 앞전은 매끈한 곡선, 뒷전은 깃 끝 n 개의 톱니"""
    sx, sy = shoulder; tx, ty = tip; bx, by = back
    lead = []
    for k in range(13):
        t = k / 12; x = sx + (tx - sx) * t; y = sy + (ty - sy) * t - math.sin(math.pi * t) * 6
        lead.append((x, y))
    trail = []
    for k in range(n * 2 + 1):
        t = k / (n * 2); x = tx + (bx - tx) * t; y = ty + (by - ty) * t + math.sin(math.pi * t) * 4
        if k % 2 == 1:  # 깃 사이 오목
            nx, ny = -(by - ty), (bx - tx); L = math.hypot(nx, ny); nx, ny = nx / L * depth, ny / L * depth
            x -= nx * side; y -= ny * side
        trail.append((x, y))
    pts = lead + trail[1:]
    if side < 0: pts = [(100 - x, y) for x, y in pts]
    return Polygon(pts).buffer(.4).buffer(-.4)

def merhan():  # 매: 정면, 날개를 활짝, 머리 뒤 해 고리, 꼬리는 첨탑처럼
    halo = ring((50, 30), 9, 11.5)
    rays = unary_union([kite((50, 30), a, 13, 18 if k % 2 else 21, 2.6) for k, a in enumerate(range(-180, 1, 30))])
    head = mir([(50, 22), (53, 24), (54.5, 29), (52.5, 34), (50, 37)])
    beak = Polygon([(48.6, 30), (51.4, 30), (50, 35)])
    body = mir([(50, 36), (56, 39), (58, 48), (55, 58), (50, 63)])
    wingS = unary_union([wing((53, 40), (86, 16), (60, 56), 6, 4.2, s) for s in (1, -1)])
    feathers = unary_union([thick([(60 + k * 4, 44 - k * 3.2), (70 + k * 3.4, 37 - k * 4)], .7) for k in range(4)] + [thick([(40 - k * 4, 44 - k * 3.2), (30 - k * 3.4, 37 - k * 4)], .7) for k in range(4)])
    wing_ = wingS.difference(feathers)
    tail = unary_union([kite((50, 60), 90 + d, 0, 24, 6, .25) for d in (-14, 0, 14)])
    eye = circ((52, 28.5), 1.1); eye2 = circ((48, 28.5), 1.1)
    bird = unary_union([head, body, tail, cut(wing_, unary_union([head, body]), 1.2)]).difference(unary_union([eye, eye2]))
    bird = unary_union([cut(bird, beak, .8), beak])
    sun = cut(unary_union([halo, rays]), bird, 1.5)
    return unary_union([sun, bird, frame(0)])

def karad():  # 사막여우: 정면 머리, 큰 귀, 귀 사이 짧은 그림자 해
    face = mir([(50, 44), (57, 45), (63, 52), (61, 60), (55, 68), (51, 76), (50, 77)])
    ear_r = Polygon([(55, 47), (71, 14), (66, 52)]); ear_l = affinity.scale(ear_r, -1, 1, origin=(50, 50))
    inner_r = Polygon([(58, 46), (69, 22), (64.5, 48)]); inner_l = affinity.scale(inner_r, -1, 1, origin=(50, 50))
    ears = unary_union([ear_r, ear_l]).difference(unary_union([inner_r, inner_l]).buffer(-.2))
    eye_r = Polygon([(53.5, 56), (59, 54), (57, 58.5)]); eye_l = affinity.scale(eye_r, -1, 1, origin=(50, 50))
    nose = mir([(50, 72), (52.2, 72.4), (50, 75)])
    blaze = mir([(50, 46), (51.6, 50), (51, 66), (50, 70)])
    head = unary_union([face, ears]).difference(unary_union([eye_r, eye_l, blaze.buffer(.4)]))
    head = unary_union([head.difference(nose.buffer(.8)), nose])
    sun = unary_union([circ((50, 26), 4.2)] + [kite((50, 26), a, 6, 9.5, 2.2) for a in range(0, 360, 45)])
    sun = cut(sun, head, 1.5)
    return unary_union([head, sun, frame(1)])

def arha():  # 종달새: 위로 솟는 새, 머리 깃, 뒤에 떠오르는 해, 아래 이삭
    sun = circ((50, 66), 20).intersection(box(0, 0, 100, 66)).difference(circ((50, 66), 14))
    body = mir([(50, 30), (54, 34), (55, 44), (53, 54), (50, 60)])
    head = circ((50, 30), 4.6)
    crest = Polygon([(48.5, 26.5), (50.5, 18), (52, 26.5)])
    beak = Polygon([(48.8, 25.4), (51.2, 25.4), (50, 21)])
    wing_ = unary_union([wing((52.5, 40), (74, 12), (56, 52), 5, 3.6, s) for s in (1, -1)])
    tail = unary_union([kite((50, 58), 90 + d, 0, 13, 4.6, .3) for d in (-16, 0, 16)])
    bird = unary_union([body, head, crest, tail, cut(wing_, unary_union([body, head]), 1.1)]).difference(circ((51.5, 29.5), .9)).difference(circ((48.5, 29.5), .9))
    bird = unary_union([cut(bird, beak, .6), beak])
    hor = box(18, 67, 82, 69.4)
    def ear(side):
        leaves = []
        for k in range(4):
            t = k / 3; x = 50 + side * (12 + 16 * t); y = 86 - 13 * t
            leaves.append(kite((x, y), -90 - side * 40, 0, 8, 3.2, .45)); leaves.append(kite((x, y), -90 + side * 70, 0, 6.5, 2.8, .45))
        return unary_union(leaves + [thick([(50 + side * 9.5, 88), (50 + side * 28.5, 72)], 1.5)])
    rest = cut(unary_union([sun, hor]), bird, 1.6)
    return unary_union([rest, bird, ear(-1), ear(1), frame(2)])

def seira():  # 바다새: 긴 날개로 미끄러지는 옆모습, 가라앉는 해와 물결
    sun = circ((50, 60), 16).intersection(box(0, 0, 100, 60)).difference(circ((50, 60), 10.5))
    waves = unary_union([crescent((x, y), 8.5, 0, 4.6, .92).intersection(box(0, 0, 100, y + 1)) for (x, y) in [(30, 70), (48, 70), (66, 70), (39, 80), (57, 80)]])
    wingL = Polygon([(48, 38), (34, 28), (20, 30), (10, 36), (24, 33), (36, 37), (46, 43)])
    wingR = Polygon([(52, 38), (64, 27), (78, 23), (90, 25), (77, 29), (64, 35), (54, 43)])
    body = Polygon([(40, 41), (46, 38), (56, 38.5), (62, 40), (56, 43), (46, 43.5)])
    head = circ((61, 39.6), 2.6); beak = Polygon([(63, 38.8), (68, 39.8), (63, 40.8)])
    tail = Polygon([(41, 41), (34, 39), (35, 43.5)])
    bird = unary_union([wingL, wingR, body, head, beak, tail]).difference(circ((61.6, 39), .7))
    rest = cut(unary_union([sun, waves]), bird, 1.6)
    return unary_union([rest, bird, frame(3)])

def mure():  # 부엉이: 정면, 귀깃, 한쪽 눈은 찬 원 · 한쪽은 빈 고리 (삶과 죽음 사이)
    body = mir([(50, 30), (56, 30), (60, 26), (63, 22), (63.5, 34), (66, 46), (64, 60), (58, 72), (50, 77)])
    eyeL = circ((43, 43), 7.5); eyeR = circ((57, 43), 7.5)
    owl = body.difference(eyeL.buffer(1.2)).difference(eyeR.buffer(1.2))
    eyeLf = eyeL.difference(circ((43, 43), 2.2))
    eyeRr = ring((57, 43), 5.6, 7.5)
    beak = Polygon([(48.4, 49), (51.6, 49), (50, 55)])
    owl = owl.difference(beak.buffer(1))
    breast = unary_union([crescent((50, 60 + k * 5), 6 - k, 0, 2.4, .9) for k in range(3)])
    owl = owl.difference(breast.buffer(.5))
    moon = crescent((76, 22), 7, -3.6, 1.6, .9)
    return unary_union([owl, eyeLf, eyeRr, beak, moon, frame(4)])

def dorn():  # 늑대: 정면 머리, 각진 주둥이, 이마에 등불 불꽃
    head = mir([(50, 34), (55, 36), (60, 32), (66, 18), (68, 40), (66, 50), (60, 58), (56, 68), (52, 76), (50, 78)])
    inner_ear = Polygon([(60, 34), (65, 23), (66, 38)]); inner_l = affinity.scale(inner_ear, -1, 1, origin=(50, 50))
    eye_r = Polygon([(54, 50), (61, 47), (58.5, 52)]); eye_l = affinity.scale(eye_r, -1, 1, origin=(50, 50))
    muzzle = mir([(50, 56), (53.5, 58), (54.5, 66), (50, 74)])
    nose = mir([(50, 69), (53, 69.5), (50, 73.5)])
    cheek = unary_union([Polygon([(58, 58), (66, 52), (63, 62)]), affinity.scale(Polygon([(58, 58), (66, 52), (63, 62)]), -1, 1, origin=(50, 50))])
    flame = tear((50, 44), 3.6, 10).difference(tear((50, 45), 1.5, 5))
    w = head.difference(unary_union([inner_ear, inner_l, eye_r, eye_l, cheek]).buffer(.3)).difference(muzzle.exterior.buffer(.7)).difference(flame.buffer(1.2))
    w = unary_union([w.difference(nose.buffer(.8)), nose, flame])
    gear = unary_union([ring(C, 34, 37)] + [affinity.rotate(box(48.5, 9, 51.5, 13), a, origin=C) for a in range(0, 360, 30)])
    gear = cut(gear, w, 1.6)
    return unary_union([w, gear, frame(5)])

def nei():  # 고래: 둥근 머리에서 꼬리로 가늘어지며 활처럼 휜 몸, 위에 별 하나
    pts, rad = [], []
    for k in range(60):
        t = k / 59
        x = 78 - 56 * t; y = 60 - 14 * math.sin(math.pi * t) - 10 * t * t
        pts.append((x, y)); rad.append(1.6 + 9.6 * (1 - t) ** .8 * (1 - math.exp(-t * 25)) + (2.6 if t < .05 else 0))
    body = unary_union([Point(p).buffer(r) for p, r in zip(pts, rad)])
    head = Point(pts[3]).buffer(9.4)
    tip = pts[-1]
    fluke = unary_union([kite(tip, -125, 0, 13, 5.6, .5), kite(tip, -30, 0, 12, 5.2, .5)])
    fin = kite((66, 64), 120, 0, 12, 4.6, .4)
    whale = unary_union([body, head, fluke, fin])
    grooves = unary_union([thick([(80 - k * 4, 66 + k * .2), (66 - k * 3, 67.5 + k * .3)], .8) for k in range(3)])
    whale = whale.difference(grooves).difference(circ((74, 58), 1.2))
    st = star4((44, 30), 11, .22)
    water = unary_union([thick([(16, 82), (30, 80), (42, 82), (58, 82), (70, 80), (84, 82)], 1.6), thick([(26, 87), (40, 85.5), (60, 85.5), (74, 87)], 1.2)])
    return unary_union([whale, st, cut(water, whale, 1.4), frame(6)])

ALL = dict(unknown=unknown, merhan=merhan, karad=karad, arha=arha, seira=seira, mure=mure, dorn=dorn, nei=nei, bond=bond, mirase=mirase)
res = {k: to_d(f().simplify(.12)) for k, f in ALL.items()}
json.dump(res, open('emblems3.json', 'w'))
print('ok')
