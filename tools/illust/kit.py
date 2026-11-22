"""장면 도구 묶음 (가제). 모든 함수는 Canvas 위에 그린다."""
import numpy as np, cv2
from base import vnoise, ridge1d, smooth, mix, hexc, paint, paper
from shapes import rough, mask_poly, facets, cracks

def C(h): return np.array(hexc(h), np.float32)

class Canvas:
    def __init__(s, W, H, seed=0):
        s.W, s.H = W, H
        s.yy, s.xx = np.mgrid[0:H, 0:W].astype(np.float32)
        s.u, s.v = s.xx / W, s.yy / H
        s.img = np.zeros((H, W, 3), np.float32)
        s.gold = np.zeros((H, W), np.float32)   # 금빛 선 (마무리에서 빛남)
        s.glow = np.zeros((H, W, 3), np.float32) # 더하는 빛 (등불, 해)
        s.r = np.random.default_rng(seed); s.seed = seed
    def put(s, col, m):
        col = col if np.ndim(col) == 3 else np.asarray(col, np.float32)
        s.img = s.img * (1 - m[..., None]) + col * m[..., None]
    def P(s, pts):  # 0..1 좌표 → 화소
        a = np.array(pts, np.float32).copy(); a[:, 0] *= s.W; a[:, 1] *= s.H; return a

    # 하늘
    def sky(s, top, mid, hor, horiz=.6, sun=None, sunc='#fff4dc', halo='#ffe2b0', halo_k=4.5, sun_k=45, sun_amt=1., cloud=.5, cloudc='#f4efe6', cloud_dark='#8696aa', cseed=21):
        v, u = s.v, s.u
        t = smooth(v, 0, horiz * .85)[..., None]
        s.img = C(top) * (1 - t) + C(mid) * t
        s.img = mix(s.img, C(hor), smooth(v, horiz * .5, horiz) * .9)
        if sun is not None:
            d = np.hypot((u - sun[0]) * s.W / s.H, v - sun[1])
            s.img += C(halo) * (np.exp(-d * halo_k) * .55 * sun_amt)[..., None]
            s.img += C(sunc) * (np.exp(-d * sun_k) * sun_amt)[..., None]
        if cloud:
            cl = vnoise(s.H, s.W, 2.5, cseed, 6)
            band = smooth(v, 0, .12) * (1 - smooth(v, horiz * .7, horiz * .95))
            s.img = mix(s.img, C(cloudc), smooth(cl, .52, .68) * band * cloud)
            s.img = mix(s.img, C(cloud_dark), smooth(cl, .64, .78) * band * cloud * .5)
    def stars(s, n=500, maxv=.6, seed=3):
        r = np.random.default_rng(seed); m = np.zeros((s.H, s.W), np.float32)
        for i in range(n):
            x, y = r.random() * s.W, r.random() * s.H * maxv
            cv2.circle(m, (int(x), int(y)), 1 if r.random() < .9 else 2, float(r.uniform(.2, 1)), -1, cv2.LINE_AA)
        s.glow += C('#dfe8ff')[None, None] * (cv2.GaussianBlur(m, (0, 0), .7) * 1.2 + cv2.GaussianBlur(m, (0, 0), 3) * .5)[..., None]
    # 산줄기 띠: base 높이에서 amp 만큼 솟음. 면 나눈 바위로 칠함
    def ridge(s, base, amp, sc, seed, dark, lit, light=(.7, -.5, .3), sharp=True, fog=None, fogamt=0, n=40, stretch=2.5, rim=None, octv=6):
        rr = ridge1d(s.W, sc, seed, octv)
        if sharp: rr = 1 - np.abs(rr * 2 - 1)
        top = base - amp * rr
        pts = [(x / (s.W - 1), top[x]) for x in range(0, s.W, 6)] + [(1, top[-1]), (1, 1.05), (0, 1.05)]
        m = mask_poly(s.H, s.W, s.P(pts), 1)
        col = facets(s.H, s.W, m, light, dark, lit, n=n, seed=seed, stretch=stretch, rim=rim, rimw=3)
        s.put(col, m)
        if fog: s.img = mix(s.img, C(fog), m * smooth(s.v, base - amp * .3, base + .05) * fogamt)
        return m
    def fogband(s, y0, y1, col, amt=.6, seed=5, sc=3):
        n = vnoise(s.H, s.W, sc, seed, 4)
        s.img = mix(s.img, C(col), smooth(s.v, y0, (y0 + y1) / 2) * (1 - smooth(s.v, (y0 + y1) / 2, y1)) * (.5 + .6 * n) * amt)
    def haze(s, col, y0, y1, amt=.5):
        s.img = mix(s.img, C(col), smooth(s.v, y0, y1) * amt)
    # 바다: 가로 붓질 물결 + 해 반사 기둥
    def sea(s, y0, deep, near, sunx=None, refc='#ffd08a', seed=7):
        m = (s.v > y0).astype(np.float32)
        t = smooth(s.v, y0, 1)[..., None]
        col = C(deep) * (1 - t) + C(near) * t
        w = cv2.resize(vnoise(s.H, max(8, s.W // 40), 6, seed, 3), (s.W, s.H), interpolation=cv2.INTER_CUBIC)
        col = col * (.9 + .2 * w[..., None])
        s.put(col, m)
        if sunx is not None:
            wid = .015 + .12 * smooth(s.v, y0, 1)
            col2 = np.exp(-((s.u - sunx) / wid) ** 2) * m * smooth(w, .45, .7)
            s.glow += C(refc)[None, None] * col2[..., None] * .9
        return m
    # 숲: 뾰족한 나무 실루엣 줄
    def forest(s, base, h, dens, col, seed=1, jit=.03, lit=None):
        r = np.random.default_rng(seed); m = np.zeros((s.H, s.W), np.float32)
        x = -.02
        while x < 1.02:
            hh = h * r.uniform(.5, 1.2); ww = hh * r.uniform(.18, .3) * s.H / s.W
            b = base + r.uniform(-jit, jit)
            pts = [(x - ww, b), (x - ww * .45, b - hh * .45), (x - ww * .6, b - hh * .42), (x, b - hh), (x + ww * .6, b - hh * .42), (x + ww * .45, b - hh * .45), (x + ww, b)]
            cv2.fillPoly(m, [np.round(s.P(pts)).astype(np.int32)], 1., cv2.LINE_AA)
            x += ww * dens * r.uniform(.6, 1.4)
        m = np.maximum(m, (s.v > base + .005).astype(np.float32))
        m = cv2.GaussianBlur(m, (0, 0), .7)
        s.put(C(col), m); return m
    # 건물 실루엣 무리 (면 나눈 덩어리 + 창 불빛)
    def block(s, pts, dark, lit, light=(.7, -.5, .3), n=6, seed=0, stretch=4, rim=None, windows=0, wincol='#ffcf86'):
        m = mask_poly(s.H, s.W, s.P(pts), .8)
        s.put(facets(s.H, s.W, m, light, dark, lit, n=n, seed=seed, stretch=stretch, rim=rim, rimw=2), m)
        if windows:
            r = np.random.default_rng(seed + 9); ys, xs = np.nonzero(m > .9)
            if len(xs):
                for i in range(windows):
                    k = r.integers(len(xs)); x, y = xs[k], ys[k]
                    cv2.rectangle(s.glow, (int(x), int(y)), (int(x + 2), int(y + 3)), tuple(float(c) for c in C(wincol) * 1.5), -1)
        return m
    def lamp(s, x, y, size=1., col='#ffc46e'):
        d = np.hypot((s.u - x) * s.W, (s.v - y) * s.H)
        s.glow += C(col)[None, None] * (np.exp(-d / (3 * size)) * 1.2 + np.exp(-d / (22 * size)) * .35 + np.exp(-d / (80 * size)) * .12)[..., None]
    def beam(s, x0, y0, x1, y1, w, col, amt=.4):
        # 두 점 사이 빛기둥
        dx, dy = (x1 - x0) * s.W, (y1 - y0) * s.H; L = np.hypot(dx, dy) + 1e-6
        px, py = s.u * s.W - x0 * s.W, s.v * s.H - y0 * s.H
        tr = (px * dx + py * dy) / (L * L); t = np.clip(tr, 0, 1)
        dist = np.abs(px * dy - py * dx) / L
        s.glow += C(col)[None, None] * (np.exp(-(dist / (w * s.W)) ** 2) * (1 - t) ** .7 * (tr > 0) * (tr < 1) * amt)[..., None]

def finish(cv, radii=(14, 7, 3), thr=.028, gold_col='#ffcf7a', dust=0, dust_c=(.6, .45), dust_s=(.15, .15), paper_amt=.06, seed=3, detail=.2):
    img = np.clip(cv.img, 0, 1)
    p = paint(img, radii=radii, thr=thr, seed=seed, maxlen=10)
    p = (1 - detail) * p + detail * cv2.bilateralFilter((img * 255).astype(np.uint8), 7, 40, 7).astype(np.float32) / 255
    g = cv.gold
    if g.max() > 0:
        gl = cv2.GaussianBlur(g, (0, 0), 6) * 1.6 + cv2.GaussianBlur(g, (0, 0), 18) * 1.2
        p = 1 - (1 - p) * (1 - np.clip(gl, 0, 1)[..., None] * C(gold_col) * .55)
        p = p * (1 - g[..., None] * .9) + C('#fff0c4') * g[..., None] * .9
    p = 1 - (1 - p) * (1 - np.clip(cv.glow, 0, 1))
    if dust:
        r = np.random.default_rng(seed + 5); dm = np.zeros((cv.H, cv.W), np.float32)
        for k in range(dust):
            x, y = r.normal(dust_c[0], dust_s[0]) * cv.W, r.normal(dust_c[1], dust_s[1]) * cv.H
            if 0 < x < cv.W and 0 < y < cv.H: cv2.circle(dm, (int(x), int(y)), int(r.integers(1, 3)), float(r.uniform(.3, 1)), -1, cv2.LINE_AA)
        dg = cv2.GaussianBlur(dm, (0, 0), 1.2) + cv2.GaussianBlur(dm, (0, 0), 5) * .8
        p = 1 - (1 - p) * (1 - np.clip(dg, 0, 1)[..., None] * C(gold_col) * .8)
    return paper(p, amt=paper_amt)

def save(p, path, size=None):
    o = (np.clip(p, 0, 1) * 255).astype(np.uint8)
    if size: o = cv2.resize(o, size, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(path, cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
