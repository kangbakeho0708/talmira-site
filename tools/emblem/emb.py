"""갈래 문장 2판 (가제): 아이콘이 아니라 문장. 선이 아닌 면, 비운 자리(네거티브 스페이스), 굵기가 변하는 칼날 모양, 공통 틀(일곱 마디 고리)"""
import json, math
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

C = (50, 50)
def circ(c, r, n=96): return Point(c).buffer(r, n // 4)
def ring(c, r1, r2): return circ(c, r2).difference(circ(c, r1))
def kite(c, ang, r0, r1, w, mid=.35):
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    p0 = (c[0] + ux * r0, c[1] + uy * r0); p2 = (c[0] + ux * r1, c[1] + uy * r1)
    m = (c[0] + ux * (r0 + (r1 - r0) * mid), c[1] + uy * (r0 + (r1 - r0) * mid))
    return Polygon([p0, (m[0] + nx * w / 2, m[1] + ny * w / 2), p2, (m[0] - nx * w / 2, m[1] - ny * w / 2)])
def sector(c, r1, r2, a0, a1, n=40):
    pts = [(c[0] + math.cos(math.radians(a0 + (a1 - a0) * t / n)) * r2, c[1] + math.sin(math.radians(a0 + (a1 - a0) * t / n)) * r2) for t in range(n + 1)]
    pts += [(c[0] + math.cos(math.radians(a1 - (a1 - a0) * t / n)) * r1, c[1] + math.sin(math.radians(a1 - (a1 - a0) * t / n)) * r1) for t in range(n + 1)]
    return Polygon(pts)
def crescent(c, r, dx, dy, k=.85): return circ(c, r).difference(circ((c[0] + dx, c[1] + dy), r * k))
def star4(c, r, w=.3, rot=0):
    pts = []
    for i in range(8):
        a = math.radians(rot + i * 45 - 90); rr = r if i % 2 == 0 else r * w
        pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
    return Polygon(pts)
def tear(c, r, h):  # 물방울 (불꽃)
    body = circ((c[0], c[1]), r)
    tip = Polygon([(c[0] - r * .96, c[1] - r * .3), (c[0], c[1] - h), (c[0] + r * .96, c[1] - r * .3)])
    return unary_union([body, tip])
def cut(shape, by, gap): return shape.difference(by.buffer(gap))

def frame(hour):
    """공통 틀: 일곱 마디로 끊긴 고리, 그 땅의 시각 자리에 작은 마름모"""
    parts = []
    for i in range(7):
        a0 = -90 + i * 360 / 7 + 4; a1 = -90 + (i + 1) * 360 / 7 - 4
        parts.append(sector(C, 43, 45.5, a0, a1))
    f = unary_union(parts)
    if hour is not None:
        a = -90 + hour * 360 / 7 + 360 / 14
        p = (C[0] + math.cos(math.radians(a)) * 44.2, C[1] + math.sin(math.radians(a)) * 44.2)
        d = affinity.rotate(box(p[0] - 3.2, p[1] - 3.2, p[0] + 3.2, p[1] + 3.2), 45, origin=p)
        f = unary_union([f.difference(d.buffer(1.2)), d])
    return f

def merhan():
    sun = ring(C, 9.5, 15)
    rays = unary_union([kite(C, a, 17, 31 if k % 2 == 0 else 24, 5 if k % 2 == 0 else 3.6) for k, a in enumerate(range(0, 360, 30))])
    spire = unary_union([kite((50, 50), -90, 0, 40, 7, .1), kite((50, 50), 90, 0, 38, 7, .1)])
    core = circ(C, 6)
    body = unary_union([cut(unary_union([sun, rays, core]), spire, 1.6), spire])
    return unary_union([body, frame(0)])

def karad():
    pillar = Polygon([(46, 82), (47.5, 40), (52.5, 40), (54, 82)])
    cap = box(42, 36, 58, 40); base = box(38, 82, 62, 86)
    beam = unary_union([kite((50, 43), 180, 0, 28, 3.4, .15), kite((50, 43), 0, 0, 28, 3.4, .15)])
    def pan(x): return unary_union([crescent((x, 62), 9, 0, -4, .95).intersection(box(x - 10, 60, x + 10, 75)), Polygon([(x - .6, 45), (x + .6, 45), (x + 7, 62), (x + 5.6, 62)]), Polygon([(x - .6, 45), (x + .6, 45), (x - 5.6, 62), (x - 7, 62)])])
    sun = unary_union([circ((50, 22), 5)] + [kite((50, 22), a, 7, 12, 2.6) for a in range(0, 360, 45)])
    body = unary_union([cut(unary_union([pillar, cap, base, pan(22), pan(78)]), beam, 1.4), beam, sun])
    return unary_union([body, frame(1)])

def arha():
    sun = circ((50, 60), 22).intersection(box(0, 0, 100, 60))
    sun = sun.difference(circ((50, 60), 15))
    hub = circ((50, 50), 4)
    sails = unary_union([kite((50, 50), a, 3, 30, 8, .7) for a in (-135, -45, 45, 135)])
    body = unary_union([cut(sun, sails, 1.8), sails, hub])
    hor = box(16, 62, 84, 64.5)
    def ear(side):
        leaves = []
        for k in range(4):
            t = k / 3; x = 50 + side * (12 + 16 * t); y = 85 - 15 * t
            leaves.append(kite((x, y), -90 - side * 40, 0, 9, 3.4, .45))
            leaves.append(kite((x, y), -90 + side * 70, 0, 7, 3, .45))
        stem = Polygon([(50 + side * 9, 88), (50 + side * 10.6, 88), (50 + side * 29, 68), (50 + side * 27.4, 68)])
        return unary_union(leaves + [stem])
    body = unary_union([body, cut(hor, sails, 1.8), ear(-1), ear(1)])
    return unary_union([body, frame(2)])

def seira():
    sun = circ((44, 56), 18).intersection(box(0, 0, 100, 56)).difference(circ((44, 56), 12))
    rays = unary_union([kite((44, 56), a, 20, 28, 3) for a in (-160, -135, -110, -90, -70, -45, -20)])
    waves = unary_union([crescent((x, y), 9, 0, 5, .92).intersection(box(0, 0, 100, y + 1)) for (x, y) in [(26, 66), (44, 66), (62, 66), (35, 76), (53, 76), (44, 86)]])
    sail = Polygon([(64, 18), (64, 62), (82, 58), (76, 40)])
    mast = box(62.5, 16, 64, 66)
    body = unary_union([cut(unary_union([sun, rays, waves]), unary_union([sail, mast]), 1.6), sail, mast])
    return unary_union([body, frame(3)])

def mure():
    disc = circ(C, 22)
    left = disc.intersection(box(0, 0, 50, 100))
    right = ring(C, 19, 22).intersection(box(50, 0, 100, 100))
    spire = unary_union([kite((50, 52), -90, 0, 42, 8, .12), kite((50, 52), 90, 0, 34, 8, .12)])
    moon = crescent((72, 24), 8, -4, 2, .9)
    window = circ((50, 40), 1.8)
    body = unary_union([cut(unary_union([left, right]), spire, 1.8), spire.difference(window.buffer(.4)), moon])
    return unary_union([body, frame(4)])

def dorn():
    gear = ring(C, 26, 31)
    teeth = unary_union([affinity.rotate(box(48, 15, 52, 20), a, origin=C) for a in range(0, 360, 30)])
    flame = tear((50, 56), 10, 26)
    inner = tear((50, 59), 5, 14)
    cage = unary_union([box(38.5, 34, 40.5, 70), box(59.5, 34, 61.5, 70), box(37, 70, 63, 73), sector((50, 36), 9.5, 11.5, 180, 360)])
    body = unary_union([cut(unary_union([gear, teeth]), unary_union([cage, flame]), 1.6), cage, flame.difference(inner)])
    return unary_union([body, frame(5)])

def nei():
    eye = circ((50, 74), 34).intersection(circ((50, 26), 34))
    iris = circ(C, 11)
    eyering = eye.difference(eye.buffer(-3.2))
    pupil = star4(C, 9, .28)
    spikes = unary_union([kite(C, a, 41, 27, 5, .2) for a in range(0, 360, 45) if a not in (0, 180)])
    body = unary_union([eyering, ring(C, 11, 13.5), pupil, cut(spikes, eye, 1.5)])
    return unary_union([body, frame(6)])

def unknown():
    c2 = (45, 55)
    r = unary_union([ring(c2, 25, 30)] + [kite(c2, -90 + i * 360 / 7, 30, 39, 5.5, .3) for i in range(7)])
    inner = ring(c2, 15, 17)
    st = star4((74, 25), 23, .2, 15)
    body = unary_union([cut(unary_union([r, inner]), st, 2), st])
    return body

def bond():
    pts = [(50, 22), (25, 66), (75, 66)]
    lamps = unary_union([tear((x, y + 3), 6, 13) for x, y in pts])
    cord = ring(C, 26, 29.5)
    knots = unary_union([ring((x, y + 3), 8.5, 10.5) for x, y in pts])
    inner = unary_union([tear((x, y + 4.5), 2.6, 6) for x, y in pts])
    body = unary_union([cut(cord, knots, 1.4), knots, lamps.difference(inner)])
    return affinity.scale(body, 1.3, 1.3, origin=C)

def mirase():
    dia = affinity.rotate(box(18, 18, 82, 82), 45, origin=C)
    frame_ = dia.difference(dia.buffer(-5))
    inner_d = affinity.rotate(box(30, 30, 70, 70), 45, origin=C)
    inner_f = inner_d.difference(inner_d.buffer(-1.8))
    flame = tear((50, 58), 10, 26).difference(tear((50, 61), 4.6, 13))
    coins = unary_union([ring(p, 2.4, 4.4) for p in [(50, 9), (91, 50), (50, 91), (9, 50)]])
    body = unary_union([frame_, cut(inner_f, flame, 1.8), flame, coins])
    return body

def to_d(g):
    def ring_d(coords): return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in coords[:-1]) + 'Z'
    geoms = getattr(g, 'geoms', [g]); out = []
    for p in geoms:
        out.append(ring_d(list(p.exterior.coords)))
        for i in p.interiors: out.append(ring_d(list(i.coords)))
    return ''.join(out)

ALL = dict(unknown=unknown, merhan=merhan, karad=karad, arha=arha, seira=seira, mure=mure, dorn=dorn, nei=nei, bond=bond, mirase=mirase)
res = {k: to_d(f().simplify(.15)) for k, f in ALL.items()}
json.dump(res, open('emblems.json', 'w'))
print({k: len(v) for k, v in res.items()})
