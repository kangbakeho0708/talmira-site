"""따로 그리는 카드 (가제): 이음회, 일곱 간부, 온기 등불. 위에 사이트 상징이 얹힌다"""
import sys, numpy as np, cv2
from kit import *
W, H = 720, 1080
HC = ['#fbf6e6', '#f1d89a', '#f2c79a', '#e8875a', '#7f9fd8', '#5a74b0', '#7fb0ff']

def bond():  # 이음회: 여러 마을 등불이 빛 실로 이어짐
    cv = Canvas(W, H, 31)
    cv.sky('#0c1328', '#3a3a66', '#c87a6a', horiz=.62, cloud=.4, cloudc='#7a5a7a', cloud_dark='#141a34')
    cv.stars(200, .4, 31)
    cv.ridge(.64, .08, 3, 32, '#24203a', '#6a5470', light=(0, -.5, .5), fog='#a06a70', fogamt=.5)
    cv.ridge(.76, .1, 2.5, 33, '#151426', '#3a3048', light=(0, -.5, .5), sharp=False)
    r = np.random.default_rng(3); pts = []
    for i in range(9):
        x, y = r.uniform(.1, .9), r.uniform(.6, .92); pts.append((x, y)); cv.lamp(x, y, r.uniform(.6, 1.1), '#ffc46e')
        for j in range(r.integers(3, 8)): cv.lamp(x + r.normal() * .03, y + r.normal() * .015, .25, '#ffb860')
    thr = np.zeros((H, W), np.float32)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if np.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) < .38:
                a, b = pts[i], pts[j]; mid = ((a[0] + b[0]) / 2, max(a[1], b[1]) + .025)
                curve = [(a[0] + (b[0] - a[0]) * t, (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * mid[1] + t * t * b[1]) for t in np.linspace(0, 1, 30)]
                cv2.polylines(thr, [cv.P(curve).astype(np.int32).reshape(-1, 1, 2)], False, .7, 1, cv2.LINE_AA)
    cv.gold += thr
    cv.ridge(.96, .08, 3, 34, '#08080f', '#1a1626', light=(0, -.5, .5))
    return cv, dict(dust=80, dust_c=(.5, .75), dust_s=(.25, .1))

def seven():  # 일곱 간부: 일곱 시각 색 등불이 한 줄로
    cv = Canvas(W, H, 32); L = (0, -.4, .6)
    cv.sky('#07090f', '#141622', '#221c22', horiz=.9, cloud=0)
    cv.block([(-.02, .7), (1.02, .7), (1.02, 1.02), (-.02, 1.02)], '#0a0809', '#221a18', light=L, n=14, seed=5, stretch=.6)
    for i, c in enumerate(HC):
        x = .14 + i * .12; y = .62 + .02 * abs(i - 3) * 0
        cv.block([(x - .025, .7), (x - .02, .66), (x + .02, .66), (x + .025, .7)], '#0d0a0a', '#5a463a', light=L, n=1, seed=10 + i)
        cv.block([(x - .018, .66), (x - .022, .58), (x, .555), (x + .022, .58), (x + .018, .66)], '#141012', '#3a2e28', light=L, n=2, seed=20 + i)
        cv.img = mix(cv.img, C(c) * .8, np.exp(-np.hypot((cv.u - x) * 3, cv.v - .615) * 60) * .9)
        cv.lamp(x, .615, 1.6, c); cv.lamp(x, .615, .5, c)
        p = cv.P([(x, .555), (x, .5)]).astype(np.int32); cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), .5, 1, cv2.LINE_AA)
    refl = np.zeros_like(cv.glow)
    cv.glow += np.roll(cv2.flip(cv.glow, 0), int(-H * (1 - 2 * .7)), 0) * (cv.v > .7)[..., None] * .25
    return cv, dict(dust=50, dust_c=(.5, .6), dust_s=(.3, .06))

def warm_lamp():  # 온기 등불: 차가운 눈밤과 등불 하나 (등불 모양은 사이트 상징이 그림, 여기선 빛과 자리만)
    cv = Canvas(W, H, 33); L = (0, -.4, .6)
    cv.sky('#03060e', '#0d1830', '#24385a', horiz=.7, cloud=.3, cloudc='#1c2c4a', cloud_dark='#03060e')
    cv.stars(300, .55, 33)
    cv.ridge(.72, .08, 3, 34, '#141e30', '#5a6c8a', light=(.2, -.8, .4), fog='#24385a', fogamt=.4)
    cv.put(C('#40506e') * 1, (cv.v > .78).astype(np.float32))
    cv.img = mix(cv.img, C('#16203a'), smooth(cv.v, .78, 1) * .7)
    r = np.random.default_rng(4); snow = np.zeros((H, W), np.float32)
    for i in range(500): cv2.circle(snow, (int(r.random() * W), int(r.random() * H)), int(r.integers(1, 3)), float(r.uniform(.3, .9)), -1, cv2.LINE_AA)
    cv.glow += C('#cfdcf0')[None, None] * cv2.GaussianBlur(snow, (0, 0), .8)[..., None] * .5
    cv.glow += C('#ffb860')[None, None] * (np.exp(-np.hypot(cv.u - .5, (cv.v - .6) * 1.4) * 4) * .45)[..., None]
    cv.img = mix(cv.img, C('#c9925a'), np.exp(-np.hypot(cv.u - .5, (cv.v - .82) * 3) * 6) * (cv.v > .78) * .6)
    return cv, dict(dust=0)

SC = {'card2-0': bond, 'card3-1': seven, 'card3-2': warm_lamp}
for k in [a for a in sys.argv[1:] if a in SC and not a.startswith('card1-')]:
    cv, fo = SC[k](); save(finish(cv, **fo), f'out/{k}.png'); print('ok', k)

# 수호자 일곱: 그 시각의 하늘만 (가운데는 비워 사이트의 고리 상징이 잘 보이게)
HOURSKY = [
    ('#2a66c0', '#9cc2ea', '#f4ecd8', (.5, -.05), '#fff6e0', 0, '#b9b2a4', '#ece4d2'),
    ('#3a74c4', '#a9c8e8', '#eef0ee', (.7, .02), '#fff6e0', 0, '#a6aeb8', '#e2e6ea'),
    ('#6f93c4', '#d4dce4', '#f6dcb8', (.2, .7), '#ffe2b0', 0, '#5a7050', '#c9cf98'),
    ('#2a1f45', '#b0507a', '#ffaa66', (.55, .8), '#ffd090', 0, '#4a2438', '#b8605a'),
    ('#0b1430', '#34558a', '#8fb0d8', (.3, .86), '#a8c4f0', 120, '#1d2d48', '#4c6890'),
    ('#03060f', '#0f1d38', '#2d4a72', None, None, 300, '#141e30', '#5a6c8a'),
    ('#000105', '#05091a', '#111c36', None, None, 700, '#04060c', '#141a2c'),
]
def gsky(h):
    top, mid, hor, sun, sc, st, d, l = HOURSKY[h]
    cv = Canvas(W, H, 40 + h)
    cv.sky(top, mid, hor, horiz=.82, sun=sun, sunc=sc or '#ffffff', halo=sc or '#ffffff', halo_k=3, sun_k=30, sun_amt=1. if sun else 0, cloud=[.4, .45, .4, .55, .35, .3, .2][h], cloudc=['#f6f2ea', '#f6f2ea', '#fbf1e2', '#ffc28a', '#6f8fbc', '#22385a', '#0c1428'][h], cloud_dark=['#8696aa', '#8696aa', '#9aa6ba', '#6a3a5a', '#1b2a4a', '#050a14', '#000000'][h], cseed=50 + h)
    if st: cv.stars(st, .8, 60 + h)
    cv.ridge(.84, .05, 4, 70 + h, d, l, light=(.3, -.6, .4), fog=hor, fogamt=.5)
    cv.ridge(.93, .07, 3, 80 + h, d, l, light=(.3, -.6, .4))
    return cv, dict(dust=40 if h < 5 else 0, dust_c=(.5, .5), dust_s=(.3, .2))
for h in range(7): SC[f'card1-{h}'] = (lambda hh: (lambda: gsky(hh)))(h)
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'g':
    for h in range(7):
        cv, fo = gsky(h); save(finish(cv, **fo), f'out/card1-{h}.png'); print('ok', h)
