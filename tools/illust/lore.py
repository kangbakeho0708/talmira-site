"""정보 그림 열 장 (가제). python3 lore.py 0 1 ... → out/loreN.png (720x1080)"""
import sys, numpy as np, cv2
from kit import *
W, H = 720, 1080

def still_sun():  # 0 멈춘 해
    cv = Canvas(W, H, 10)
    cv.sky('#16224a', '#c0605a', '#ffbf80', horiz=.72, sun=(.5, .3), sunc='#fff6dc', halo='#ffd29a', halo_k=3, sun_k=28, sun_amt=1.2, cloud=.55, cloudc='#ffcf9a', cloud_dark='#5a3050')
    for a in np.linspace(0, 2 * np.pi, 13)[:-1]:  # 멈춘 빛줄기 (굳은 결)
        cv.beam(.5, .3, .5 + np.cos(a) * .9, .3 + np.sin(a) * .9 * W / H, .01, '#fff0c8', .22)
    # 해를 두른 가는 금 고리 (멈춤)
    ring = np.zeros((H, W), np.float32); cv2.circle(ring, (int(.5 * W), int(.3 * H)), int(.16 * W), 1., 1, cv2.LINE_AA); cv.gold += ring * .7
    cv.ridge(.74, .07, 3, 11, '#4a2a3a', '#c9786a', light=(0, -.2, .6), fog='#f0a070', fogamt=.6)
    cv.ridge(.82, .08, 4, 12, '#2a1828', '#7a4448', light=(0, -.2, .6), fog='#c06a5a', fogamt=.35)
    cv.ridge(.94, .1, 3, 13, '#140c16', '#3a2028', light=(0, -.2, .6))
    return cv, dict(dust=80, dust_c=(.5, .3), dust_s=(.2, .1))

def seven_hours():  # 1 일곱 시각: 높은 곳에서 내려다본 땅. 해 바로 아래(한낮)를 중심으로 동심원 띠
    cv = Canvas(W, H, 11); u, v = cv.u, cv.v
    HZ = .2
    cv.sky('#05081a', '#2a2a4a', '#6a5a7a', horiz=HZ, cloud=0); cv.stars(250, .2, 11)
    below = v > HZ + .003
    z = 1.0 / np.maximum(v - HZ, 1e-3); xg = (u - .5) * z * 1.1
    zc = 1.0 / (.29 - HZ)  # 해 바로 아래 지점 (멀리)
    d = np.hypot(xg * .55, (z - zc) * .5) / 5.2
    cols = ['#fffaf0', '#f6dea0', '#f2c08c', '#e07a50', '#4f6fa0', '#22304e', '#070b18']
    edges = [0, .09, .2, .33, .48, .64, .82, 9]
    col = np.zeros((H, W, 3), np.float32)
    for i in range(7):
        a0, a1 = edges[i], edges[i + 1]
        w = smooth(d, a0 - .02, a0 + .02) * (1 - smooth(d, a1 - .02, a1 + .02))
        col += C(cols[i]) * w[..., None]
    terr = vnoise(H, W, 30, 12, 6); terr2 = vnoise(H, W, 8, 13, 5)
    shade = .75 + .45 * (terr * .6 + terr2 * .4)
    col *= shade[..., None]
    # 띠 경계의 가는 금선
    ring = np.zeros((H, W), np.float32)
    for e in edges[1:-1]: ring += np.exp(-((d - e) / .004) ** 2)
    far = smooth(v, HZ + .06, HZ)
    col = mix(col, C('#c9b8a8'), far * .5)
    cv.put(col, below.astype(np.float32))
    cv.gold += np.clip(ring, 0, 1) * below * (1 - far) * .5
    # 해: 위에서 내려다보는 눈높이 위쪽
    cv.glow += C('#fff6dc')[None, None] * (np.exp(-np.hypot(u - .5, (v - .06) * 1.4) * 9) * 1.0 + np.exp(-np.hypot(u - .5, v - .06) * 3) * .25)[..., None]
    cv.beam(.5, .06, .5, .29, .015, '#fff0c8', .45)
    cv.glow += C('#fffaf0')[None, None] * (np.exp(-np.hypot((u - .5), (v - .29) * 3) * 25) * .7)[..., None]
    r = np.random.default_rng(14)
    for i in range(55):
        x, y = r.random(), r.uniform(.45, 1)
        dd = d[int(y * (H - 1)), int(x * (W - 1))]
        if dd > .48: cv.lamp(x, y, r.uniform(.08, .2) * (.5 + y), '#ffc070')
    return cv, dict(dust=50, dust_c=(.5, .4), dust_s=(.25, .2))

def falling_stars():  # 2 떨어지는 별 + 등불 축제
    cv = Canvas(W, H, 12)
    cv.sky('#040814', '#14224a', '#3a4a7a', horiz=.68, cloud=.25, cloudc='#2a3a66', cloud_dark='#060a18')
    cv.stars(700, .7, 12)
    for (x0, y0, L) in [(.85, .05, .45), (.6, .12, .3), (.95, .25, .25)]:
        cv.beam(x0, y0, x0 - L * .55, y0 + L, .004, '#e8f0ff', .9); cv.lamp(x0 - L * .55, y0 + L, .6, '#f0f6ff')
    cv.ridge(.7, .08, 3, 21, '#0c1426', '#2a3a5c', light=(0, -.5, .5), fog='#24345a', fogamt=.4)
    hill = cv.ridge(.82, .1, 2, 22, '#080d18', '#1c2840', light=(0, -.5, .5), sharp=False)
    r = np.random.default_rng(3)
    for i in range(70):  # 축제 등불
        x = r.normal(.5, .2); y = .78 + r.random() * .2 + abs(x - .5) * -.05
        if 0 < x < 1: cv.lamp(x, y, r.uniform(.25, .6), r.choice(['#ffc46e', '#ffb050', '#ffd890']))
    for i in range(12):  # 떠오르는 풍등
        cv.lamp(r.uniform(.2, .8), r.uniform(.5, .75), .35, '#ffcf80')
    cv.ridge(.97, .06, 3, 23, '#04060c', '#101624', light=(0, -.5, .5))
    return cv, dict(dust=0)

def guardian():  # 3 수호자: 금 고리들에 붙잡힌 해
    cv = Canvas(W, H, 13)
    cv.sky('#1e3a6e', '#8fb0d8', '#f4e6c8', horiz=.8, sun=(.5, .42), sunc='#fffaf0', halo='#ffe6b0', halo_k=4, sun_k=24, sun_amt=1.3, cloud=.6)
    g = np.zeros((H, W), np.float32)
    for i, (rx, ry, a) in enumerate([(.3, .1, 15), (.26, .16, -30), (.34, .07, 60), (.22, .22, -70)]):
        cv2.ellipse(g, (int(.5 * W), int(.42 * H)), (int(rx * W), int(ry * W)), a, 0, 360, 1., 2, cv2.LINE_AA)
    cv.gold += g * .8
    cv.ridge(.84, .08, 3, 31, '#3a4a66', '#c9d2dc', light=(0, -.6, .4), fog='#e8e2d4', fogamt=.5)
    cv.ridge(.95, .1, 4, 32, '#141a26', '#4a5468', light=(0, -.6, .4))
    return cv, dict(dust=140, dust_c=(.5, .42), dust_s=(.18, .14))

def stillness():  # 4 멈춤: 부서지다 멈춘 파도
    cv = Canvas(W, H, 14); L = (.6, -.6, .4)
    cv.sky('#6f8fb8', '#c9d6e2', '#eef0ec', horiz=.5, sun=(.8, .12), halo='#fff4dc', halo_k=4, sun_k=40, cloud=.4)
    cv.sea(.5, '#5a7896', '#1a2e44', sunx=.8, refc='#fff4dc')
    # 굽은 파도 몸통
    wave = rough([(-.05, .9), (-.05, .62), (.2, .5), (.45, .38), (.62, .34), (.74, .38), (.7, .45), (.6, .44), (.52, .5), (.5, .62), (.62, .78), (.8, .9), (1.05, .95), (1.05, 1.05), (-.05, 1.05)], 5, .05, 41)
    m = mask_poly(H, W, cv.P(wave))
    body = facets(H, W, m, L, '#123048', '#6fa7c0', n=40, seed=42, stretch=1.5, rim='#e9f6fa', rimw=4)
    cv.put(body, m)
    # 굳은 물마루 거품
    crest = np.zeros((H, W), np.float32); r = np.random.default_rng(4)
    for i in range(160):
        t = r.random(); x = .45 + .3 * t; y = .36 + .06 * np.sin(t * 3) + r.normal() * .015
        cv2.circle(crest, (int(x * W), int(y * H)), int(r.integers(3, 12)), float(r.uniform(.6, 1)), -1, cv2.LINE_AA)
    cv.put(C('#f6fbfb'), cv2.GaussianBlur(crest, (0, 0), 1.5))
    # 허공에 걸린 물방울
    drops = np.zeros((H, W), np.float32)
    for i in range(90):
        x, y = r.normal(.66, .1), r.normal(.3, .09)
        cv2.ellipse(drops, (int(x * W), int(y * H)), (int(r.integers(2, 6)), int(r.integers(3, 8))), 0, 0, 360, 1., -1, cv2.LINE_AA)
    cv.put(C('#e4f2f6'), cv2.GaussianBlur(drops, (0, 0), .8)); cv.glow += C('#ffffff')[None, None] * (cv2.GaussianBlur(drops, (0, 0), 3) * .25)[..., None]
    return cv, dict(dust=0, radii=(12, 6, 3))

def slip():  # 5 미끄러짐: 굳은 땅 틈에서 돋는 풀
    cv = Canvas(W, H, 15); L = (-.5, -.7, .4)
    cv.sky('#7e8a9a', '#b8bcbe', '#d9d4c8', horiz=.35, cloud=.3)
    gr = rough([(-.05, .38), (.3, .36), (.7, .4), (1.05, .37), (1.05, 1.05), (-.05, 1.05)], 4, .04, 51)
    m = mask_poly(H, W, cv.P(gr))
    cv.put(facets(H, W, m, L, '#38383d', '#8f8b84', n=220, seed=52, stretch=.7), m)
    cv.img = cv.img * (1 - .25 * smooth(cv.v, .4, 1)[..., None])
    # 큰 틈
    crack = np.zeros((H, W), np.float32)
    pts = cv.P([(.1, .55), (.3, .6), (.42, .7), (.5, .68), (.62, .78), (.8, .74), (1, .82)]).astype(np.int32)
    for i in range(len(pts) - 1): cv2.line(crack, tuple(pts[i]), tuple(pts[i + 1]), 1., 7 if i in (2, 3) else 4, cv2.LINE_AA)
    cv.put(C('#141416'), cv2.GaussianBlur(crack, (0, 0), 1))
    # 풀 (주인공): 틈에서 돋는 푸른 잎들, 밝게
    r = np.random.default_rng(5); leaf = np.zeros((H, W), np.float32)
    bx, by = .47 * W, .69 * H
    for i in range(18):
        a = -np.pi / 2 + r.normal() * .45; Lh = r.uniform(.12, .3) * H
        tip = (bx + np.cos(a) * Lh * .6 + r.normal() * 6, by + np.sin(a) * Lh)
        mid = ((bx + tip[0]) / 2 + r.normal() * 10, (by + tip[1]) / 2)
        w = r.uniform(6, 13)
        poly = np.array([(bx - w, by), (mid[0] - w * .8, mid[1]), tip, (mid[0] + w * .8, mid[1]), (bx + w, by)], np.int32)
        cv2.fillPoly(leaf, [poly], 1., cv2.LINE_AA)
    lcol = mix(np.full((H, W, 3), C('#3f7a3a')), C('#bfe39a'), smooth(cv.u, .4, .55) * .7)
    cv.put(lcol, cv2.GaussianBlur(leaf, (0, 0), .8))
    cv.glow += C('#e8ffc8')[None, None] * (np.exp(-np.hypot(cv.u - .48, (cv.v - .6) * 1.2) * 9) * .45)[..., None]
    return cv, dict(dust=70, dust_c=(.48, .58), dust_s=(.08, .08), gold_col='#e8ffb0', radii=(12, 6, 3))

def delayed():  # 6 밀린 시간: 왼쪽 핀 꽃, 오른쪽 무너지는 바위
    cv = Canvas(W, H, 16); L = (-.4, -.7, .4)
    cv.sky('#20304e', '#6a7fa6', '#d8c8b0', horiz=.62, sun=(.3, .5), halo='#ffd8a8', halo_k=4, sun_k=40, sun_amt=.7, cloud=.4)
    cv.ridge(.66, .06, 4, 61, '#3a4560', '#9aa4b8', light=L, fog='#c9bca8', fogamt=.5)
    gnd = cv.ridge(.8, .05, 3, 62, '#1e2430', '#5a6070', light=L, sharp=False)
    # 오른쪽 바위, 위에서부터 부서져 흩어짐
    rock = rough([(.55, .82), (.6, .5), (.72, .38), (.86, .42), (.95, .6), (.97, .82)], 4, .1, 63)
    m = mask_poly(H, W, cv.P(rock)); keep = m * smooth(cv.v, .42, .55)
    cv.put(facets(H, W, m, L, '#2a2e38', '#8a8e98', n=20, seed=64, rim='#f0d8b0', rimw=3), keep)
    r = np.random.default_rng(6)
    for i in range(140):
        x, y = r.uniform(.58, .97), r.uniform(.2, .55) - r.random() * .1
        q = rough([(0, -1), (1, 0), (0, 1), (-1, 0)], 2, .5, 700 + i) * r.uniform(2, 9); q[:, 0] += x * W; q[:, 1] += y * H
        cv.put(C('#3a3e48') * r.uniform(.8, 1.6), mask_poly(H, W, q, .6))
    cv.gold += cracks(H, W, keep, n=3, seed=65, length=30, step=5)
    # 왼쪽 꽃 (활짝)
    fx, fy = .27, .62
    stem = np.zeros((H, W), np.float32); cv2.line(stem, (int(fx * W), int(fy * H)), (int(.25 * W), int(.82 * H)), 1., 4, cv2.LINE_AA)
    cv.put(C('#3a6a3a'), stem)
    pet = np.zeros((H, W), np.float32)
    for k in range(8):
        a = k * np.pi / 4; cx, cy = fx * W + np.cos(a) * 34, fy * H + np.sin(a) * 30
        cv2.ellipse(pet, (int(cx), int(cy)), (34, 16), np.degrees(a), 0, 360, 1., -1, cv2.LINE_AA)
    cv.put(mix(np.full((H, W, 3), C('#f0a6a0')), C('#fff0e0'), smooth(-np.hypot(cv.u - fx, cv.v - fy), -.08, -.01)), cv2.GaussianBlur(pet, (0, 0), 1))
    cv.lamp(fx, fy, 1.2, '#ffe0a0')
    return cv, dict(dust=120, dust_c=(.5, .5), dust_s=(.25, .15), radii=(12, 6, 3))

def manifest():  # 7 발현자: 빛의 고리 (시각판 디자인 전이라 상징만)
    cv = Canvas(W, H, 17)
    cv.sky('#0a0f1e', '#1d2a4a', '#3a3050', horiz=.9, cloud=.3, cloudc='#2a3a5e', cloud_dark='#070a14')
    cv.stars(250, 1, 17)
    g = np.zeros((H, W), np.float32); c = (int(.5 * W), int(.45 * H)); R = int(.3 * W)
    cv2.circle(g, c, R, 1., 2, cv2.LINE_AA); cv2.circle(g, c, int(R * .7), .6, 1, cv2.LINE_AA)
    cols = ['#fbf6e6', '#f1d89a', '#f2c79a', '#e8875a', '#4f6f9e', '#24314d', '#7fb0ff']
    for i in range(7):
        a = -np.pi / 2 + i * 2 * np.pi / 7
        p0 = (int(c[0] + np.cos(a) * R), int(c[1] + np.sin(a) * R)); p1 = (int(c[0] + np.cos(a) * R * 1.12), int(c[1] + np.sin(a) * R * 1.12))
        cv2.line(g, p0, p1, 1., 3, cv2.LINE_AA)
        cv.lamp(p1[0] / W, p1[1] / H, .6, cols[i])
    cv.gold += g
    cv.glow += C('#ffe0a0')[None, None] * (np.exp(-np.hypot(cv.u - .5, (cv.v - .45) * H / W) * 14) * .6)[..., None]
    return cv, dict(dust=200, dust_c=(.5, .45), dust_s=(.15, .12))

def old_name():  # 9 옛 이름: 읽을 수 없는 문자가 새겨진 돌문
    cv = Canvas(W, H, 19); L = (.5, -.5, .5)
    cv.sky('#05040c', '#151026', '#2a2040', horiz=.9, cloud=0)
    door = rough([(.15, .95), (.15, .35), (.25, .2), (.5, .14), (.75, .2), (.85, .35), (.85, .95)], 4, .03, 91)
    m = mask_poly(H, W, cv.P(door)); cv.put(facets(H, W, m, L, '#1a1820', '#5a5460', n=40, seed=92, stretch=1.2, rim='#9a8ab0', rimw=3), m)
    inner = rough([(.28, .95), (.28, .42), (.36, .3), (.5, .26), (.64, .3), (.72, .42), (.72, .95)], 3, .02, 93)
    mi = mask_poly(H, W, cv.P(inner)); cv.put(facets(H, W, mi, L, '#0e0d12', '#34303c', n=20, seed=94, stretch=1), mi)
    # 알아볼 수 없는 옛 문자 (긁힌 자국 무늬, 실제 문자 아님)
    r = np.random.default_rng(9); gl = np.zeros((H, W), np.float32)
    for row in range(9):
        y = .38 + row * .055
        for col in range(5):
            x = .33 + col * .085 + r.normal() * .005
            for s in range(r.integers(2, 5)):
                a = r.uniform(0, np.pi); l = r.uniform(.008, .02)
                p0 = (int((x + np.cos(a) * l) * W), int((y + np.sin(a) * l) * H)); p1 = (int((x - np.cos(a) * l) * W), int((y - np.sin(a) * l) * H))
                cv2.line(gl, p0, p1, 1., 2, cv2.LINE_AA)
    gl = cv2.GaussianBlur(gl, (0, 0), 1.2) * mi
    cv.gold += gl * .55
    cv.glow += C('#b9a0ff')[None, None] * (np.exp(-np.hypot(cv.u - .5, (cv.v - .6) * .8) * 5) * .12)[..., None]
    cv.block([(-.02, .95), (1.02, .94), (1.02, 1.02), (-.02, 1.02)], '#0a090e', '#2a2630', n=6, seed=95)
    return cv, dict(dust=60, dust_c=(.5, .6), dust_s=(.2, .2), gold_col='#d8c4ff')

SC = {0: still_sun, 1: seven_hours, 2: falling_stars, 3: guardian, 4: stillness, 5: slip, 6: delayed, 7: manifest, 9: old_name}
if __name__ == '__main__':
    for k in map(int, sys.argv[1:]):
        if k == 8:
            im = cv2.imread('/tmp/frozen_final.png') if __import__('os').path.exists('/tmp/frozen_final.png') else cv2.imread('out/frozen-test-v1.png')
            cv2.imwrite('out/lore8.png', cv2.resize(im, (720, 1080), interpolation=cv2.INTER_AREA)); continue
        cv, fo = SC[k](); save(finish(cv, **fo), f'out/lore{k}.png'); print('ok', k)
