"""모양 도구: 거친 다각형, 면 나눔 바위, 금빛 균열"""
import numpy as np, cv2
from base import hexc, vnoise

def rough(pts, depth=5, amp=.18, seed=0):
    r = np.random.default_rng(seed); P = [np.array(p, np.float32) for p in pts]
    for d in range(depth):
        Q = []
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            m = (a + b) / 2; n = np.array([-(b - a)[1], (b - a)[0]])
            m = m + n * (r.random() - .5) * amp
            Q += [a, m]
        P = Q; amp *= .55
    return np.array(P, np.float32)

def mask_poly(H, W, P, blur=.8):
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(P).astype(np.int32)], 255, lineType=cv2.LINE_AA)
    m = m.astype(np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m

def facets(H, W, m, light, base_dark, base_lit, n=60, seed=0, rim=None, rimw=6, bands=4, stretch=2.5, jit=.18):
    """덩어리 형태 빛 (마스크에서 법선) + 길쭉한 면 나눔 + 명암 단계 묶기 = 칠한 바위 면"""
    r = np.random.default_rng(seed)
    ys, xs = np.nonzero(m > .5)
    if len(xs) == 0: return np.zeros((H, W, 3), np.float32)
    x0, x1, y0, y1 = max(0, xs.min() - 2), min(W, xs.max() + 3), max(0, ys.min() - 2), min(H, ys.max() + 3)
    sz = max(x1 - x0, y1 - y0)
    mm = m[y0:y1, x0:x1]
    bl = cv2.GaussianBlur(mm, (0, 0), max(2, sz * .12))
    nx = -cv2.Sobel(bl, cv2.CV_32F, 1, 0, ksize=5); ny = -cv2.Sobel(bl, cv2.CV_32F, 0, 1, ksize=5)
    sc = np.percentile(np.hypot(nx, ny)[mm > .5], 90) + 1e-6
    nx, ny = nx / sc, ny / sc; nz = np.sqrt(np.clip(1 - np.clip(nx * nx + ny * ny, 0, .95), 0, 1))
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    form = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # 길쭉한 면
    yi, xi = np.nonzero(mm > .5)
    k = min(n, len(xi)); idx = r.choice(len(xi), size=k, replace=False)
    sx, sy = xi[idx].astype(np.float32), yi[idx].astype(np.float32)
    gy, gx = np.mgrid[0:y1 - y0, 0:x1 - x0].astype(np.float32)
    lab = np.argmin((gx[..., None] - sx) ** 2 + ((gy[..., None] - sy) / stretch) ** 2, -1)
    off = (r.random(k) - .5) * 2 * jit
    s = np.clip(form + off[lab], 0, 1)
    s = np.round(s * (bands - 1)) / (bands - 1) * .75 + s * .25
    out = np.zeros((H, W, 3), np.float32)
    dk, lt = np.array(hexc(base_dark)), np.array(hexc(base_lit))
    out[y0:y1, x0:x1] = dk * (1 - s[..., None]) + lt * s[..., None]
    if rim is not None:
        dist = cv2.distanceTransform((mm > .5).astype(np.uint8), cv2.DIST_L2, 5)
        face = np.clip(nx * L[0] + ny * L[1], 0, 1)
        rr = np.clip(face * 1.8, 0, 1) * smooth_(dist, rimw * 1.4, 0)
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - rr[..., None]) + np.array(hexc(rim)) * rr[..., None]
    return out

def smooth_(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def cracks(H, W, m, n=6, seed=0, length=60, step=4):
    """바위 안쪽에 금빛 균열 선 (마스크 안에서만)"""
    r = np.random.default_rng(seed); out = np.zeros((H, W), np.float32)
    ys, xs = np.nonzero(m > .8)
    if len(xs) == 0: return out
    for k in range(n):
        i = r.integers(len(xs)); x, y = float(xs[i]), float(ys[i]); a = r.random() * 6.283
        pts = [(x, y)]
        for s in range(length):
            a += (r.random() - .5) * .45
            x += np.cos(a) * step; y += np.sin(a) * step
            xi, yi = int(x), int(y)
            if not (0 <= xi < W and 0 <= yi < H) or m[yi, xi] < .7: break
            pts.append((x, y))
            if r.random() < .06:
                # 가지
                bx, by, ba = x, y, a + (r.random() - .5) * 2.4
                bp = [(bx, by)]
                for t in range(int(length * .3)):
                    ba += (r.random() - .5) * .9; bx += np.cos(ba) * step; by += np.sin(ba) * step
                    if not (0 <= int(bx) < W and 0 <= int(by) < H) or m[int(by), int(bx)] < .7: break
                    bp.append((bx, by))
                if len(bp) > 1: cv2.polylines(out, [np.array(bp, np.int32).reshape(-1, 1, 2)], False, .8, 1, cv2.LINE_AA)
        if len(pts) > 1: cv2.polylines(out, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, 1., int(r.integers(1, 3)), cv2.LINE_AA)
    return out
