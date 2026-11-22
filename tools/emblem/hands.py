"""일곱 손 (수호자) 상징 (가제): 문장식 손이 그 시각의 해를 쥔다. 손목 장식은 그 땅 문장의 동물. 하루 실루엣도 여기서"""
import json, math
from shapely.geometry import Point, Polygon, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from emb import circ, ring, kite, crescent, star4, tear, cut, to_d
from emb3 import wing, thick, mir

def finger(base, ang, L, w):
    a = math.radians(ang); tip = (base[0] + math.cos(a) * L, base[1] + math.sin(a) * L)
    return LineString([base, tip]).buffer(w / 2, cap_style=1)

def sun(hour, c=(50, 34), r=14):
    if hour == 5:  # 새벽: 해가 아직 없다. 주먹 사이로 새는 빛줄기만
        return unary_union([kite((50, 52), a, 6, 22 if k % 2 == 0 else 15, 2.6) for k, a in enumerate(range(-160, -19, 20))])
    if hour == 6:  # 자정: 빈 해 고리와 별
        return unary_union([ring(c, r - 2.4, r), star4(c, 8, .22)])
    rays = unary_union([kite(c, a, r + 2, r + (9 if k % 2 == 0 else 6), 3 if k % 2 == 0 else 2.2) for k, a in enumerate(range(0, 360, 30))])
    core = ring(c, r - 4.2, r) if hour in (3, 4) else circ(c, r - 1.5)
    inner = circ(c, 4) if hour in (3, 4) else Point(0, 0).buffer(0)
    return unary_union([core, inner, rays])

def arcfinger(c, R, a0, a1, w0, n=24):
    """해 둘레를 따라 휘어 오르는 가는 손가락 (끝으로 갈수록 가늘다)"""
    outer, inner = [], []
    for k in range(n + 1):
        t = k / n; a = math.radians(a0 + (a1 - a0) * t); w = w0 * (1 - t) + .7 * t
        outer.append((c[0] + math.cos(a) * (R + w / 2), c[1] + math.sin(a) * (R + w / 2)))
        inner.append((c[0] + math.cos(a) * (R - w / 2), c[1] + math.sin(a) * (R - w / 2)))
    return Polygon(outer + inner[::-1]).buffer(.3)

def hand(hour):
    sc = (50, 36); r = 13
    closed = hour == 5
    palm = mir([(50, 86), (55.5, 85), (58, 72), (61, 60), (59, 54), (50, 52.5)])
    if closed:  # 새벽: 손가락을 모아 쥔 주먹, 틈으로 빛
        fingers = unary_union([arcfinger((50, 50), 9 + k * 2.4, 95 - k * 8, -40 - k * 6, 4.6) for k in range(2)] + [arcfinger((50, 50), 9 + k * 2.4, 85 + k * 8, 220 + k * 6, 4.6) for k in range(2)])
    else:
        fingers = unary_union([
            arcfinger(sc, r + 3.6, 62, -28, 5.2), arcfinger(sc, r + 8, 70, -6, 4.8),
            arcfinger(sc, r + 3.6, 118, 208, 5.2), arcfinger(sc, r + 8, 110, 186, 4.8)])
    thumb = arcfinger((50, 58), 14, 150, 228, 5.4)
    h = unary_union([palm, fingers, thumb])
    lines = unary_union([thick([(46, 62), (50, 66), (54, 62)], .8), thick([(50, 70), (50, 80)], .8)])
    h = h.difference(lines)
    cuff = box(42, 78, 58, 82.5)
    h = unary_union([h.difference(cuff.buffer(1)), cuff])
    orn = []
    if hour in (0, 2, 3):
        for s in (1, -1): orn.append(affinity.translate(affinity.scale(wing((52, 40), (76, 18), (56, 54), 4, 3, s), .5, .5, origin=(50, 40)), 0, 41))
    elif hour == 1:
        for s in (1, -1): orn.append(Polygon([(50 + s * 10, 82), (50 + s * 21, 63), (50 + s * 16.5, 84)]))
    elif hour == 4:
        for s in (1, -1): orn.append(kite((50 + s * 10, 80), -90 + s * 35, 0, 15, 4.6, .5))
    elif hour == 5:
        for s in (1, -1): orn += [kite((50 + s * 9.5, 80 + k * 2.2), (-35 - 25 * k) if s > 0 else (215 + 25 * k), 0, 10 - k * 2, 3.6, .3) for k in range(3)]
    elif hour == 6:
        for s in (1, -1): orn.append(kite((50 + s * 9.5, 80.5), (-20) if s > 0 else 200, 0, 13, 5, .5))
    orn = unary_union(orn)
    sn = sun(hour, sc, r) if hour != 5 else sun(5)
    return unary_union([cut(sn, h, 1.6), h, cut(orn, h, 1.2)])

def haru():
    """하루 실루엣 (설정: 다리 없는 작고 둥근 짐승, 긴 꼬리, 귀). 세부 얼굴은 그리지 않음"""
    body = Point(42, 46).buffer(14)
    ears = unary_union([Polygon([(32, 38), (30, 22), (40, 34)]), Polygon([(46, 33), (52, 19), (54, 36)])])
    pts = []
    for k in range(70):
        t = k / 69
        if t < .75: x, y = 54 + 44 * t, 54 - 4 * math.sin(math.pi * t / .75) - 14 * t
        else:
            u = (t - .75) / .25; a = math.radians(90 + 260 * u); x, y = 82 + math.cos(a) * 7 * (1 - u * .4), 36.5 + 7 - 7 + math.sin(a) * 7 * (1 - u * .4) - 7
        pts.append((x, y))
    tail = unary_union([Point(p).buffer(4.4 * (1 - k / 76) + .5) for k, p in enumerate(pts)])
    print('tailtip', pts[-1])
    return unary_union([body, ears, tail])

res = {f'hand{h}': to_d(hand(h).simplify(.12)) for h in range(7)}
res['haru'] = to_d(haru().simplify(.12))
json.dump(res, open('hands.json', 'w'))
print('ok')
