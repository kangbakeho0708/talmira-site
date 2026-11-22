"""땅 일곱 장 (가제). python3 lands.py 5  → out/land5.png"""
import sys, numpy as np, cv2
from kit import *
W, H = 1600, 900

def tower(cv, x, base, h, w, dark, lit, seed, top='spire', gold=True, light=(.2, -.9, .5)):
    pts = [(x - w, base), (x - w * .8, base - h * .7), (x - w * .55, base - h * .92)]
    if top == 'spire': pts += [(x, base - h * 1.25)]
    elif top == 'dome': pts += [(x - w * .4, base - h * 1.0), (x, base - h * 1.07), (x + w * .4, base - h * 1.0)]
    else: pts += [(x - w * .5, base - h), (x + w * .5, base - h)]
    pts += [(x + w * .55, base - h * .92), (x + w * .8, base - h * .7), (x + w, base)]
    m = cv.block(pts, dark, lit, light=light, n=5, seed=seed, stretch=6, rim='#fff6e0')
    if gold and top == 'spire':
        p = cv.P([(x, base - h * 1.25), (x, base - h * .95)]).astype(np.int32)
        cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), .9, 2, cv2.LINE_AA)
    return m

def merhan():
    cv = Canvas(W, H, 5)
    L = (.25, -.9, .35)
    cv.sky('#3d78c6', '#9fc2e6', '#f2ead9', horiz=.6, sun=(.6, -.1), halo='#fff1cf', halo_k=3.5, sun_k=10, sun_amt=1.0, cloud=.35)
    cv.ridge(.6, .05, 5, 11, '#b7b3ab', '#ece6d8', light=L, fog='#f2ede2', fogamt=.7)
    cv.fogband(.55, .72, '#f6f1e6', .8, 6)
    # 먼 오른쪽 작은 고원 (옅게)
    fr = rough([(.86, .7), (.9, .56), (1.05, .55), (1.05, .7)], 4, .05, 61); fm = mask_poly(H, W, cv.P(fr)); cv.put(facets(H, W, fm, L, '#a9adb5', '#e9e6de', n=12, seed=62, stretch=3), fm)
    for i, x in enumerate(np.linspace(.9, 1.0, 6)): tower(cv, x, .56, .03 + .03 * np.random.default_rng(i).random(), .004, '#b9bcc4', '#fbf8f0', 400 + i, light=L)
    cv.fogband(.6, .74, '#f6f1e6', .6, 16)
    # 가운데 오른쪽: 하얀 도시가 올라앉은 큰 고원 절벽
    cl = rough([(.3, .95), (.36, .62), (.42, .5), (.55, .47), (.78, .48), (.9, .53), (.97, .7), (1.05, .95)], 5, .06, 51)
    m = mask_poly(H, W, cv.P(cl)); cv.put(facets(H, W, m, L, '#4a4f5c', '#b9b6ae', n=60, seed=52, stretch=4, rim='#fff3d6', rimw=4), m)
    cv.img = cv.img * (1 - m[..., None] * smooth(cv.v, .5, .75)[..., None] * .35)
    cv.img = mix(cv.img, C('#f1ede3'), m * smooth(cv.v, .74, .95) * .85)
    r = np.random.default_rng(8)
    xs = sorted(r.uniform(.43, .9, 46))
    for i, x in enumerate(xs):
        dc = abs(x - .62)
        h = (.06 + .16 * np.exp(-(dc / .12) ** 2)) * r.uniform(.6, 1.1)
        base = .49 + .01 * r.random() + (.03 if x > .82 or x < .47 else 0)
        tower(cv, x, base, h, r.uniform(.004, .009), '#7c7f88', '#fffaf0', 200 + i, top=r.choice(['spire', 'dome', 'flat'], p=[.6, .25, .15]), light=L)
    # 가장 높은 탑 + 빛기둥 (주인공)
    tower(cv, .62, .48, .34, .014, '#7d808a', '#fffdf6', 999, top='spire', light=L)
    cv.beam(.62, .055, .62, -.2, .01, '#fff6dc', 1.0); cv.beam(.62, .055, .62, -.2, .035, '#ffe9b8', .3)
    cv.lamp(.62, .056, 2.2, '#fff1c8')
    cv.fogband(.5, .62, '#fbf7ee', .35, 9, 6)
    # 앞 왼쪽: 따뜻한 돌 테라스와 금 난간 (틀)
    fg = cv.block([(-.02, .7), (.12, .69), (.3, .76), (.42, 1.02), (-.02, 1.02)], '#3e3328', '#b49a74', light=L, n=22, seed=77, stretch=2, rim='#ffe4b0')
    for x in np.linspace(.0, .27, 12):
        y = .69 + (x / .3) * .07
        cv.block([(x - .0025, y + .005), (x - .002, y - .07), (x + .002, y - .07), (x + .0025, y + .005)], '#3a3026', '#e0c99c', light=L, n=1, seed=int(x * 1000) + 3, stretch=3)
    cv.block([(-.02, .615), (.29, .685), (.29, .695), (-.02, .627)], '#3a3026', '#f0dcae', light=L, n=1, seed=5)
    p = cv.P([(0, .617), (.29, .687)]).astype(np.int32); cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), .9, 3, cv2.LINE_AA)
    return cv, dict(dust=160, dust_c=(.6, .3), dust_s=(.2, .15))

def windmill(cv, x, base, h, ang=.4, L=(-.8, -.4, .3)):
    w = h * .16
    cv.block([(x - w, base), (x - w * .55, base - h), (x + w * .55, base - h), (x + w, base)], '#4b3a2c', '#e8c99a', light=L, n=4, seed=31, stretch=5, rim='#fff0cc')
    cv.block([(x - w * .7, base - h), (x, base - h * 1.18), (x + w * .7, base - h)], '#5a3428', '#c97b55', light=L, n=2, seed=32)
    hx, hy = x, base - h * 1.02
    for k in range(4):
        a = ang + k * np.pi / 2; ex, ey = hx + np.cos(a) * h * .75 * cv.H / cv.W, hy + np.sin(a) * h * .75
        nx, ny = -np.sin(a) * h * .07 * cv.H / cv.W, np.cos(a) * h * .07
        cv.block([(hx, hy), (ex, ey), (ex + nx, ey + ny), (hx + nx * .3, hy + ny * .3)], '#6a5442', '#f3e2c2', light=L, n=1, seed=40 + k)
        p = cv.P([(hx, hy), (ex, ey)]).astype(np.int32); cv2.line(cv.img, tuple(p[0]), tuple(p[1]), tuple(float(c) for c in C('#3b2d22')), 2, cv2.LINE_AA)

def house(cv, x, base, w, h, L, seed, roof='#b5603f'):
    cv.block([(x - w, base), (x - w, base - h), (x + w, base - h), (x + w, base)], '#8b7a66', '#f5ead6', light=L, n=2, seed=seed, stretch=2)
    cv.block([(x - w * 1.15, base - h), (x, base - h - w * 1.1 * cv.W / cv.H * .55), (x + w * 1.15, base - h)], '#5e3326', roof, light=L, n=2, seed=seed + 1)

def arha():
    cv = Canvas(W, H, 0); L = (-.8, -.45, .35)
    cv.sky('#6f93c4', '#c9d9e6', '#f6e3c4', horiz=.58, sun=(.14, .36), halo='#ffe2b0', halo_k=3.2, sun_k=30, sun_amt=1.1, cloud=.45, cloudc='#fbf1e2', cloud_dark='#9aa6ba')
    cv.ridge(.58, .1, 4, 2, '#8d9bb0', '#d9d9d6', light=L, fog='#efe6d6', fogamt=.6)
    cv.fogband(.52, .64, '#f7ead6', .6, 3)
    cv.ridge(.66, .07, 3, 3, '#6f8a5e', '#c7cf8e', light=L, sharp=False, fog='#efe4c8', fogamt=.35, n=30)
    m = cv.ridge(.76, .1, 2.2, 4, '#4e6b3c', '#b9c56f', light=L, sharp=False, n=40)
    # 밭 줄무늬
    stripes = (np.sin((cv.u * 9 + cv.v * 30) * 3.1) > .2).astype(np.float32) * m * smooth(cv.v, .66, .8)
    cv.img = mix(cv.img, C('#d9c66d'), cv2.GaussianBlur(stripes, (0, 0), 1.5) * .35)
    windmill(cv, .66, .66, .26, .5, L)
    for i, (x, w) in enumerate([(.56, .012), (.59, .009), (.72, .011), (.75, .008), (.78, .012), (.53, .008)]):
        house(cv, x, .7 + .01 * (i % 2), w, .022, L, 60 + i * 3, roof=['#b5603f', '#a8563a', '#c06c46'][i % 3])
    # 길
    path = np.zeros((H, W), np.float32)
    pts = cv.P([(.2, 1.02), (.32, .9), (.45, .82), (.56, .76), (.63, .72)]).astype(np.int32)
    for i in range(len(pts) - 1): cv2.line(path, tuple(pts[i]), tuple(pts[i + 1]), 1., int(18 - i * 4), cv2.LINE_AA)
    cv.img = mix(cv.img, C('#e3cf9e'), cv2.GaussianBlur(path, (0, 0), 2) * .8)
    cv.ridge(.95, .12, 3, 5, '#2c3d24', '#7f9548', light=L, sharp=False, n=20)
    cv.forest(.95, .06, 1.6, '#26341f', seed=6, jit=.02)
    return cv, dict(dust=120, dust_c=(.2, .4), dust_s=(.15, .15))

def karad():
    cv = Canvas(W, H, 1); L = (.4, -.85, .35)
    cv.sky('#2f6cbf', '#8fb7e2', '#e8eef2', horiz=.55, sun=(.78, -.12), halo='#fff6e0', halo_k=3.5, sun_k=12, cloud=.35)
    cv.ridge(.55, .06, 4, 12, '#9aa6b4', '#dfe4ea', light=L, fog='#eef2f4', fogamt=.6)
    # 흰 도시 줄
    r = np.random.default_rng(2)
    for i in range(40):
        x = r.uniform(0, 1); w = r.uniform(.01, .03); h = r.uniform(.04, .1)
        cv.block([(x - w, .62), (x - w, .62 - h), (x + w, .62 - h), (x + w, .62)], '#8f96a2', '#fbf8f2', light=L, n=3, seed=300 + i, stretch=3)
    # 기록 보관소 (주인공): 큰 돔과 기둥 줄
    cx = .46
    cv.block([(cx - .2, .62), (cx - .2, .5), (cx + .2, .5), (cx + .2, .62)], '#8a909b', '#fffdf8', light=L, n=4, seed=401, stretch=2, rim='#fff6e0')
    for k in range(17):
        x = cx - .19 + k * .38 / 16
        cv.block([(x - .004, .6), (x - .004, .51), (x + .004, .51), (x + .004, .6)], '#c9ccd2', '#ffffff', light=L, n=1, seed=410 + k)
        cv.img = mix(cv.img, C('#6d7787'), ((np.abs(cv.u - (x + .012)) < .006) & (cv.v > .51) & (cv.v < .6)).astype(np.float32) * .55)
    cv.block([(cx - .2, .5), (cx - .2, .47), (cx + .2, .47), (cx + .2, .5)], '#9198a3', '#fffaf2', light=L, n=3, seed=430)
    # 계단처럼 쌓인 기록 탑 (비대칭) 과 곁탑
    for j, (w_, h_) in enumerate([(.09, .06), (.07, .05), (.05, .05), (.03, .06)]):
        y0_ = .47 - sum(hh for _, hh in [(.09, .06), (.07, .05), (.05, .05), (.03, .06)][:j]) 
        cv.block([(cx + .04 - w_, y0_), (cx + .04 - w_, y0_ - h_), (cx + .04 + w_, y0_ - h_), (cx + .04 + w_, y0_)], '#8a909b', '#fffdf8', light=L, n=3, seed=431 + j, stretch=2, rim='#fff3d6')
        for a in range(int(w_ * 120)):
            ax = cx + .04 - w_ + (a + .5) * (2 * w_) / int(w_ * 120)
            cv.img = mix(cv.img, C('#6d7787'), (((cv.u - ax) ** 2 * 4e4 + ((cv.v - (y0_ - h_ * .45)) / (h_ * .35)) ** 2 < 1) & (cv.v > y0_ - h_ * .6)).astype(np.float32) * .55)
    cv.block([(cx - .15, .47), (cx - .15, .34), (cx - .135, .3), (cx - .12, .34), (cx - .12, .47)], '#8a909b', '#fffdf8', light=L, n=3, seed=440, stretch=5, rim='#fff3d6')
    top_ = .47 - .22
    p = cv.P([(cx + .04, top_), (cx + .04, top_ - .05)]).astype(np.int32); cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), 1., 3, cv2.LINE_AA)
    # 수로와 둑
    cv.block([(-.02, .62), (1.02, .62), (1.02, .66), (-.02, .66)], '#a9a397', '#efe8da', light=L, n=10, seed=440, stretch=1)
    water = (cv.v > .66).astype(np.float32)
    refl = cv2.flip(cv.img, 0); sh = int(H * (1 - 2 * .66)); refl = np.roll(refl, -sh, 0) if sh < 0 else np.roll(refl, sh, 0)
    wv = cv2.resize(vnoise(H, W // 40, 6, 9, 3), (W, H), interpolation=cv2.INTER_CUBIC)
    refl = cv2.GaussianBlur(refl, (0, 0), 3)
    cv.put(mix(refl * .75 + C('#2d5d8f') * .25, C('#e9f1f6'), smooth(wv, .62, .75) * .6), water)
    cv.block([(-.02, .88), (.4, .86), (.6, .87), (1.02, .86), (1.02, 1.02), (-.02, 1.02)], '#6f6a62', '#e7dfcf', light=L, n=14, seed=450, stretch=2)
    p = cv.P([(0, .9), (1, .885)]).astype(np.int32); cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), .6, 2, cv2.LINE_AA)
    return cv, dict(dust=80, dust_c=(.6, .35), dust_s=(.2, .15))

def seira():
    cv = Canvas(W, H, 2); L = (.1, .2, .5)
    cv.sky('#2a1f45', '#a8507a', '#ffb36b', horiz=.56, sun=(.6, .54), sunc='#fff0c0', halo='#ffb066', halo_k=2.6, sun_k=22, sun_amt=1.2, cloud=.6, cloudc='#ffc28a', cloud_dark='#6a3a5a')
    cv.ridge(.565, .03, 6, 21, '#7a3d4a', '#d9776a', light=L, fog='#ff9a66', fogamt=.6)
    cv.sea(.565, '#d0705a', '#3a2238', sunx=.6, refc='#ffcf8a')
    # 오른쪽 항구 도시 실루엣 (등불)
    r = np.random.default_rng(4)
    for i in range(36):
        x = r.uniform(.66, 1.02); w = r.uniform(.006, .016); h = r.uniform(.02, .09)
        top = r.choice(['flat', 'dome', 'spire'])
        pts = [(x - w, .6), (x - w, .6 - h)] + ([(x, .6 - h - .03)] if top == 'spire' else [(x - w * .6, .6 - h - .015), (x + w * .6, .6 - h - .015)] if top == 'dome' else []) + [(x + w, .6 - h), (x + w, .6)]
        cv.block(pts, '#2a1a2c', '#7a4048', light=L, n=2, seed=500 + i, windows=3, wincol='#ffcf86')
    for i in range(10):
        x = r.uniform(.68, .98); cv.lamp(x, .6, .5, '#ffc070')
        p = cv.P([(x, .6), (x, .52)]).astype(np.int32); cv2.line(cv.img, tuple(p[0]), tuple(p[1]), tuple(float(c) for c in C('#2a1a2c')), 2, cv2.LINE_AA)
    cv.block([(.62, .63), (1.02, .6), (1.02, .64), (.62, .645)], '#20141f', '#5a3038', light=L, n=4, seed=560)
    # 배 한 척
    bx = .42
    cv.block([(bx - .04, .66), (bx + .04, .66), (bx + .03, .675), (bx - .033, .675)], '#22141e', '#5a3038', light=L, n=1, seed=570)
    cv.block([(bx - .002, .665), (bx - .002, .58), (bx + .03, .655)], '#3a2430', '#f3c79a', light=(.8, 0, .4), n=1, seed=571)
    cv.lamp(bx + .03, .662, .4, '#ffc070')
    cv.block([(-.02, .9), (.25, .87), (.5, .9), (.5, 1.02), (-.02, 1.02)], '#1c111a', '#4a2a32', light=L, n=8, seed=580)
    return cv, dict(dust=140, dust_c=(.6, .5), dust_s=(.2, .12), gold_col='#ffbf70')

def mure():
    cv = Canvas(W, H, 3); L = (-.5, -.6, .3)
    cv.sky('#0b1430', '#2f4f80', '#8fb0d8', horiz=.6, sun=(.2, .66), sunc='#c9dcf5', halo='#7f9fd0', halo_k=3, sun_k=30, sun_amt=.6, cloud=.35, cloudc='#6f8fbc', cloud_dark='#1b2a4a')
    cv.stars(300, .35)
    cv.ridge(.58, .14, 3.5, 31, '#2a3c5c', '#6f8ab4', light=L, fog='#7e9cc8', fogamt=.6)
    cv.fogband(.52, .68, '#8eaad0', .55, 4)
    cv.ridge(.66, .1, 4, 32, '#1d2d48', '#4c6890', light=L, fog='#6f8cb6', fogamt=.45)
    cv.forest(.7, .06, .8, '#1a2a42', seed=33)
    # 첨탑 (주인공) 언덕 위
    hill = cv.ridge(.8, .12, 1.6, 34, '#121d30', '#2e4466', light=L, sharp=False, n=20)
    sx = .64
    cv.block([(sx - .012, .7), (sx - .009, .5), (sx, .38), (sx + .009, .5), (sx + .012, .7)], '#151f33', '#5a77a6', light=L, n=4, seed=35, stretch=6, rim='#b9d0f0')
    cv.block([(sx - .03, .72), (sx - .03, .64), (sx + .03, .64), (sx + .03, .72)], '#151f33', '#45618d', light=L, n=3, seed=36)
    cv.lamp(sx, .55, .8, '#ffd38a'); cv.lamp(sx - .015, .67, .5, '#ffcf86')
    p = cv.P([(sx, .38), (sx, .35)]).astype(np.int32); cv2.line(cv.gold, tuple(p[0]), tuple(p[1]), .8, 2, cv2.LINE_AA)
    cv.forest(.86, .14, .7, '#0c1424', seed=37)
    cv.forest(.97, .2, .6, '#070c16', seed=38)
    return cv, dict(dust=100, dust_c=(.62, .55), dust_s=(.12, .15), gold_col='#ffd38a')

def dorn():
    cv = Canvas(W, H, 4); L = (0, -.3, .6)
    cv.sky('#03060f', '#0d1a33', '#2d4a72', horiz=.6, cloud=.25, cloudc='#22385a', cloud_dark='#050a14')
    cv.stars(500, .5, 41)
    cv.ridge(.6, .12, 4, 41, '#1c2a42', '#8ea4c4', light=(.2, -.8, .4), fog='#2a4062', fogamt=.4)
    # 눈 들판
    snow = (cv.v > .66).astype(np.float32)
    cv.put(C('#5d7194') * (1 - smooth(cv.v, .66, 1)[..., None] * .55) + C('#a9bad4') * .0, snow)
    cv.img = mix(cv.img, C('#8094b6'), snow * (1 - smooth(cv.v, .66, .95)) * .6 * (.8 + .3 * vnoise(H, W, 3, 43, 3)))
    # 철골 도시 (주인공): 탑과 굴뚝, 증기
    r = np.random.default_rng(5)
    for i in range(22):
        x = r.uniform(.4, .8); w = r.uniform(.01, .025); h = r.uniform(.07, .22)
        cv.block([(x - w, .67), (x - w * .8, .67 - h), (x + w * .8, .67 - h), (x + w, .67)], '#070a12', '#26324a', light=L, n=2, seed=600 + i, windows=4, wincol='#ffb860')
        # 철골 격자
        for k in range(4):
            p = cv.P([(x - w * .8, .67 - h * k / 4), (x + w * .8, .67 - h * (k + 1) / 4)]).astype(np.int32)
            cv2.line(cv.img, tuple(p[0]), tuple(p[1]), tuple(float(c) for c in C('#2b364c')), 1, cv2.LINE_AA)
    for i in range(5):
        x = r.uniform(.46, .74); h = r.uniform(.12, .2)
        cv.block([(x - .004, .67), (x - .004, .67 - h), (x + .004, .67 - h), (x + .004, .67)], '#06080e', '#1c2536', light=L, n=1, seed=650 + i)
        st = np.exp(-(((cv.u - x - (.67 - h - cv.v) * .15) / (.012 + (.67 - h - cv.v) * .12)) ** 2)) * (cv.v < .67 - h) * smooth(cv.v, .15, .67 - h) * (.5 + .6 * vnoise(H, W, 6, 660 + i, 4))
        cv.img = mix(cv.img, C('#4a5a78'), np.clip(st, 0, 1) * .6)
    # 등불 길
    pts = [(.2, 1.02), (.34, .88), (.47, .77), (.56, .7)]
    path = np.zeros((H, W), np.float32); pp = cv.P(pts).astype(np.int32)
    for i in range(3): cv2.line(path, tuple(pp[i]), tuple(pp[i + 1]), 1., int(26 - i * 7), cv2.LINE_AA)
    cv.img = mix(cv.img, C('#161e2e'), cv2.GaussianBlur(path, (0, 0), 2) * .85)
    for t in np.linspace(0, 1, 8):
        i = min(2, int(t * 3)); f0 = t * 3 - i
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f0 + .015 * (1 - t); y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f0
        cv.lamp(x, y - .03 * (1 - t * .7), 1.4 - t, '#ffb860')
        p = cv.P([(x, y), (x, y - .03 * (1 - t * .7))]).astype(np.int32); cv2.line(cv.img, tuple(p[0]), tuple(p[1]), tuple(float(c) for c in C('#0a0d14')), max(1, int(3 - 2 * t)), cv2.LINE_AA)
    cv.glow += C('#ff9e50')[None, None] * (np.exp(-(((cv.u - .6) / .15) ** 2 + ((cv.v - .65) / .05) ** 2)) * .25)[..., None]
    return cv, dict(dust=0)

def nei():
    cv = Canvas(W, H, 6); L = (0, -.5, .5)
    cv.sky('#000105', '#060b1c', '#152442', horiz=.6, cloud=.0)
    cv.stars(1400, .62, 61)
    # 은하 띠
    band = np.exp(-(((cv.v - .1 - cv.u * .45) / .09) ** 2)) * (.4 + .7 * vnoise(H, W, 5, 62, 6))
    cv.glow += C('#8fa8e0')[None, None] * (np.clip(band, 0, 1) * .22)[..., None]
    # 지평선의 낯선 빛
    cv.glow += C('#9fc4ff')[None, None] * (np.exp(-(((cv.u - .7) / .06) ** 2 + ((cv.v - .6) / .012) ** 2)) * .9 + np.exp(-(((cv.u - .7) / .25) ** 2 + ((cv.v - .6) / .06) ** 2)) * .25)[..., None]
    cv.ridge(.6, .015, 8, 63, '#04060c', '#121a2c', light=L, n=10)
    # 거울 같은 검은 물: 하늘을 비춘다
    water = (cv.v > .605).astype(np.float32)
    refl = cv2.flip(cv.img + cv.glow, 0); sh = int(H * (1 - 2 * .605)); refl = np.roll(refl, sh, 0)
    gl_r = cv2.flip(cv.glow, 0); gl_r = np.roll(gl_r, sh, 0)
    refl = cv2.GaussianBlur(refl, (0, 0), 2.5); gl_r = cv2.GaussianBlur(gl_r, (0, 0), 2.5)
    cv.put(refl * .35, water); cv.glow = cv.glow * (1 - water[..., None]) + gl_r * water[..., None] * .3
    # 앞의 검은 돌 몇 개
    for i, (x, y, s) in enumerate([(.18, .82, .05), (.3, .9, .03), (.86, .86, .06)]):
        pts = rough([(x - s, y + .01), (x - s * .5, y - s * .9), (x + s * .4, y - s * 1.1), (x + s, y + .01)], 4, .2, 640 + i)
        m = mask_poly(H, W, cv.P(pts)); cv.put(facets(H, W, m, (.6, -.3, .3), '#020308', '#1a2236', n=6, seed=650 + i, rim='#7f9fe0', rimw=2), m)
    return cv, dict(dust=60, dust_c=(.7, .58), dust_s=(.15, .05), gold_col='#9fc4ff')

SCENES = {0: arha, 1: karad, 2: seira, 3: mure, 4: dorn, 5: merhan, 6: nei}
if __name__ == '__main__':
    for k in map(int, sys.argv[1:]):
        cv, fo = SCENES[k]()
        save(np.clip(cv.img + cv.glow * .0, 0, 1), f'/tmp/land{k}_base.png')
        p = finish(cv, **fo)
        save(p, f'out/land{k}.png', (1920, 1080))
        print('ok', k)
