"""멈춘 지형: 굳은 폭포와 허공에 머문 바위 (시험 한 장, 가제)"""
import numpy as np, cv2
from base import *
from shapes import *
W, H = 900, 1350
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); u, v = xx / W, yy / H
SUN = (.80, .16); LIGHT = (.7, -.55, .45)

def put(img, col, m):
    return img * (1 - m[..., None]) + (col if np.ndim(col) == 3 else np.array(col, np.float32)) * m[..., None]

# 1. 하늘: 밝고 맑은 새벽 하늘
top, mid, hor = map(lambda h: np.array(hexc(h)), ('#7f98b4', '#c3cfd9', '#f1e7d6'))
t = smooth(v, 0, .5)[..., None]
img = top * (1 - t) + mid * t
img = mix(img, hor, smooth(v, .3, .58) * .85)
d = np.hypot(u - SUN[0], (v - SUN[1]) * 1.4)
img += np.array(hexc('#ffe9c4')) * (np.exp(-d * 4.5) * .5)[..., None]
img += np.array(hexc('#fffaf0')) * (np.exp(-d * 45) * 1.)[..., None]
cl = vnoise(H, W, 2.5, 21, 6)
img = mix(img, hexc('#f6f1e8'), smooth(cl, .52, .68) * smooth(v, .0, .15) * (1 - smooth(v, .42, .55)) * .6)
img = mix(img, hexc('#8696aa'), smooth(cl, .64, .78) * (1 - smooth(v, .35, .5)) * .3)

# 2. 먼 바위 기둥들 (아주 옅게)
r = np.random.default_rng(5)
for k in range(9):
    x = r.uniform(.05, .98); hgt = r.uniform(.1, .26); wd = r.uniform(.02, .05); base = r.uniform(.56, .62)
    P = rough([(x - wd * 1.8, base + .04), (x - wd * .4, base - hgt), (x + wd * .15, base - hgt * 1.08), (x + wd * 1.6, base + .04)], 4, .25, 100 + k)
    P[:, 0] *= W; P[:, 1] *= H
    m = mask_poly(H, W, P, 1)
    img = put(img, np.full((H, W, 3), hexc('#a7b3c1'), np.float32) * (.92 + .16 * r.random()), m * (1 - smooth(v, base - hgt * .4, base + .02)) * .9 + m * .05)
img = mix(img, hexc('#e9e4da'), smooth(v, .5, .6) * (1 - smooth(v, .62, .7)) * (.4 + .6 * vnoise(H, W, 3, 6, 4)) * .7)

midP = rough([(.5, .9), (.58, .72), (.68, .69), (.8, .71), (.92, .66), (1.05, .68), (1.05, .9)], 5, .06, 91)
midP[:, 0] *= W; midP[:, 1] *= H; mdm = mask_poly(H, W, midP)
img = put(img, facets(H, W, mdm, (.8, -.4, .3), '#6d7888', '#a9b3bf', n=25, seed=92, stretch=2), mdm)
img = mix(img, hexc('#e3e1da'), mdm * smooth(v, .72, .86) * .6)
# 3. 가운데: 왼쪽 큰 절벽, 폭포가 시작되는 턱
cliffP = rough([(-.05, .22), (.14, .18), (.30, .27), (.47, .29), (.56, .33), (.6, .45), (.57, .62), (.62, .8), (.6, .92), (-.05, .92)], 5, .08, 7)
cliffP[:, 0] *= W; cliffP[:, 1] *= H
cm = mask_poly(H, W, cliffP)
rock = facets(H, W, cm, (.8, -.4, .15), '#171a21', '#5d6573', n=70, seed=3, rim='#f2d9a8', rimw=7, stretch=4)
# 폭포 뒤 움푹한 그늘
rock = rock * (1 - .45 * np.exp(-(((u - .44) / .1) ** 2 + ((v - .55) / .25) ** 2)))[..., None]
rock = rock * (.85 + .3 * vnoise(H, W, 30, 8, 3))[..., None]
img = put(img, rock, cm)
gold = cracks(H, W, cm, n=2, seed=4, length=40, step=7)

# 4. 굳은 폭포: 턱에서 휘어 떨어지는 가닥들. 끝은 끊겨 허공에 멈춘 물방울
fall = np.zeros((H, W), np.float32); hi = np.zeros((H, W), np.float32)
r = np.random.default_rng(9)
for k in range(150):
    s = r.uniform(0, 1)
    x0 = (.36 + .1 * s) * W; y0 = (.285 + .012 * s) * H
    L = r.uniform(.42, .53) * H; brk = r.random() < .35
    pts = []
    for i in range(60):
        t = i / 59; yy_ = y0 + L * t
        if brk and t > r.uniform(.55, .9): break
        xx_ = x0 + (W * .03) * (1 - (1 - t) ** 2) * (1 + .5 * s) + np.sin(t * 6 + k) * 2
        pts.append((xx_, yy_))
    th = int(r.integers(3, 10))
    cv2.polylines(fall, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, float(r.uniform(.55, 1)), th, cv2.LINE_AA)
    if r.random() < .4: cv2.polylines(hi, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, 1., 1, cv2.LINE_AA)
    if brk and len(pts) > 2:
        ex, ey = pts[-1]
        for j in range(int(r.integers(2, 6))):
            dy = r.uniform(8, 60); cv2.ellipse(fall, (int(ex + r.normal() * 3), int(ey + dy)), (int(r.integers(2, 4)), int(r.integers(3, 6))), 0, 0, 360, .95, -1, cv2.LINE_AA)
fall = cv2.GaussianBlur(fall, (0, 0), .8)
iceC = mix(np.full((H, W, 3), hexc('#e4f1f6'), np.float32), hexc('#7fa7bf'), (1 - smooth(u, .35, .45)) * .6)
img = put(img, iceC, np.clip(fall, 0, 1))
img = put(img, np.full((H, W, 3), hexc('#ffffff'), np.float32), hi * .9)
# 굳은 물보라 왕관 (아래)
crown = np.zeros((H, W), np.float32)
for k in range(40):
    a = r.uniform(np.pi * 1.05, np.pi * 1.95); rr = r.uniform(30, 120)
    cx_, cy_ = .45 * W, .80 * H
    p0 = (cx_ + np.cos(a) * 15, cy_); p1 = (cx_ + np.cos(a) * rr, cy_ + np.sin(a) * rr * .8)
    cv2.line(crown, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), float(r.uniform(.5, 1)), int(r.integers(2, 6)), cv2.LINE_AA)
    cv2.circle(crown, (int(p1[0]), int(p1[1] - r.uniform(5, 30))), int(r.integers(2, 5)), 1., -1, cv2.LINE_AA)
mist = np.exp(-(((u - .45) / .14) ** 2 + ((v - .81) / .045) ** 2)) * (.5 + .6 * vnoise(H, W, 8, 44, 4))
img = mix(img, hexc('#eef3f4'), np.clip(mist, 0, 1) * .85)
img = put(img, np.full((H, W, 3), hexc('#f4f8f8'), np.float32), cv2.GaussianBlur(crown, (0, 0), .8))

# 5. 허공에 머문 바위들 (오른쪽, 떨어지다 멈춤)
floats = [(.66, .34, .09, .07, 1), (.82, .46, .06, .05, 2), (.58, .55, .045, .04, 3), (.74, .62, .035, .03, 4), (.9, .28, .03, .03, 5), (.52, .40, .022, .02, 6)]
fm_all = np.zeros((H, W), np.float32)
for (fx, fy, rw, rh, sd) in floats:
    rr_ = np.random.default_rng(sd)
    n = 7; ang = np.sort(rr_.uniform(0, 6.283, n))
    P = [(fx + np.cos(a) * rw * rr_.uniform(.6, 1.1), fy + np.sin(a) * rh * (1.6 if np.sin(a) > 0 else .8) * rr_.uniform(.6, 1.1)) for a in ang]
    P = rough(P, 4, .22, 200 + sd); P[:, 0] *= W; P[:, 1] *= H
    m = mask_poly(H, W, P)
    fr = facets(H, W, m, LIGHT, '#1b1e26', '#858b97', n=10, seed=sd, rim='#f6d79c', rimw=3, stretch=1.5)
    img = put(img, fr, m); fm_all = np.maximum(fm_all, m)
    gold = np.maximum(gold, cracks(H, W, m, n=1 + (sd < 3), seed=sd + 50, length=20, step=5))
    # 부스러기
    for j in range(int(rr_.integers(2, 6))):
        dx, dy = rr_.normal() * rw * W * 1.3, rr_.normal() * rh * H * 1.6
        q = rough([(0, -1), (rr_.uniform(.4, 1.2), rr_.uniform(-.3, .3)), (rr_.uniform(-.3, .3), rr_.uniform(.6, 1.4)), (-rr_.uniform(.4, 1), .1)], 3, .5, 300 + sd * 10 + j) * rr_.uniform(2, 6)
        q[:, 0] += fx * W + dx; q[:, 1] += fy * H + dy
        mm = mask_poly(H, W, q, .6); img = put(img, np.full((H, W, 3), hexc('#262a33'), np.float32), mm)

# 6. 앞: 오른쪽 아래 큰 검은 바위, 왼쪽 아래 바위, 굳은 웅덩이
gndP = rough([(-.05, .86), (.25, .84), (.55, .87), (.8, .83), (1.05, .85), (1.05, 1.05), (-.05, 1.05)], 5, .05, 31)
gndP[:, 0] *= W; gndP[:, 1] *= H; gm = mask_poly(H, W, gndP)
img = put(img, np.full((H, W, 3), hexc('#1a1d24'), np.float32), gm)
pool = gm * np.clip(1 - (((u - .47) / .26) ** 2 + ((v - .895) / .03) ** 2), 0, 1) ** .5 * (.7 + .3 * vnoise(H, W, 20, 61, 3))
refl = cv2.flip(img, 0); refl = np.roll(refl, int(-.27 * H), 0)
img = put(img, refl * .55 + np.array(hexc('#7f97a8')) * .25, pool * .8)
fgR = rough([(.62, 1.05), (.74, .9), (.8, .78), (.86, .88), (.95, .74), (1.05, .8), (1.05, 1.05)], 5, .1, 41)
fgR[:, 0] *= W; fgR[:, 1] *= H; fmr = mask_poly(H, W, fgR)
img = put(img, facets(H, W, fmr, LIGHT, '#0d0f14', '#3a3f4a', n=20, seed=8, rim='#c9a46a', rimw=3), fmr)
fgL = rough([(-.05, 1.05), (-.05, .86), (.06, .9), (.12, .82), (.2, .95), (.3, 1.05)], 5, .1, 42)
fgL[:, 0] *= W; fgL[:, 1] *= H; fml = mask_poly(H, W, fgL)
img = put(img, facets(H, W, fml, LIGHT, '#0b0d11', '#2c313b', n=14, seed=9), fml)
gold = np.maximum(gold, cracks(H, W, fmr, n=1, seed=77, length=30, step=6))

np.save('/tmp/fz_img.npy', np.clip(img, 0, 1)); np.save('/tmp/fz_gold.npy', gold)
o = (np.clip(img, 0, 1) * 255).astype(np.uint8)
cv2.imwrite('/tmp/frozen_base.png', cv2.cvtColor(o, cv2.COLOR_RGB2BGR)); cv2.imwrite('/tmp/frozen_value.png', cv2.cvtColor(o, cv2.COLOR_RGB2GRAY))
