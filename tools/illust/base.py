"""그림 기초 도구: 잡음, 실루엣, 붓질. 강백호 사이트 일러스트용 (가제)."""
import numpy as np, cv2
rng = np.random.default_rng(7)

def vnoise(h, w, scale, seed=0, oct=5, gain=.5):
    r = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        s = max(2, int(scale * 2 ** o))
        g = r.random((int(h / (w / s)) + 3, s + 3)).astype(np.float32)
        up = cv2.resize(g, (w + int(w / s) * 2, h + int(w / s) * 2), interpolation=cv2.INTER_CUBIC)
        ox, oy = r.integers(0, max(1, int(w / s))), r.integers(0, max(1, int(w / s)))
        out += amp * up[oy:oy + h, ox:ox + w]; tot += amp; amp *= gain
    return out / tot

def ridge1d(w, scale, seed, oct=6):
    n = vnoise(8, w, scale, seed, oct)[4]
    return (n - n.min()) / (n.max() - n.min() + 1e-6)

def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def mix(c, col, m):
    m = m[..., None] if m.ndim == 2 else m
    return c * (1 - m) + np.array(col, np.float32) * m

def hexc(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

def paint(img, radii=(14, 7, 3), thr=.035, seed=3, maxlen=14):
    """Hertzmann 식 겹 붓질. img: float RGB 0..1"""
    r = np.random.default_rng(seed)
    H, W = img.shape[:2]
    canvas = cv2.GaussianBlur(img, (0, 0), radii[0] * 1.5).copy()
    lum = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    for R in radii:
        ref = cv2.GaussianBlur(img, (0, 0), R * .5)
        gl = cv2.GaussianBlur(lum, (0, 0), R * .6)
        gx = cv2.Sobel(gl, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(gl, cv2.CV_32F, 0, 1, ksize=3)
        diff = np.sqrt(((canvas - ref) ** 2).sum(-1))
        g = max(2, int(R * .9))
        pts = []
        for y in range(0, H, g):
            for x in range(0, W, g):
                blk = diff[y:y + g, x:x + g]
                if blk.mean() > thr:
                    iy, ix = np.unravel_index(np.argmax(blk), blk.shape)
                    pts.append((x + ix, y + iy))
        r.shuffle(pts)
        layer = (canvas * 255).astype(np.uint8)
        for (x0, y0) in pts:
            col = ref[y0, x0]
            jit = 1 + (r.random(3) - .5) * .06
            c = tuple(int(v) for v in np.clip(col * jit * 255, 0, 255))
            path = [(x0, y0)]; x, y = float(x0), float(y0); dxp, dyp = 0., 0.
            for i in range(maxlen):
                xi, yi = int(np.clip(x, 0, W - 1)), int(np.clip(y, 0, H - 1))
                if i > 2 and np.abs(ref[yi, xi] - col).sum() > .12: break
                ggx, ggy = gx[yi, xi], gy[yi, xi]
                if ggx * ggx + ggy * ggy < 1e-6: break
                dx, dy = -ggy, ggx
                if dxp * dx + dyp * dy < 0: dx, dy = -dx, -dy
                n = np.hypot(dx, dy); dx, dy = dx / n, dy / n
                dx, dy = .6 * dx + .4 * dxp, .6 * dy + .4 * dyp; n = np.hypot(dx, dy) + 1e-6; dx, dy = dx / n, dy / n
                x += R * dx; y += R * dy; path.append((int(x), int(y))); dxp, dyp = dx, dy
            p = np.array(path, np.int32).reshape(-1, 1, 2)
            cv2.polylines(layer, [p], False, c, thickness=max(1, int(R * (.8 + .5 * r.random()))), lineType=cv2.LINE_AA)
        canvas = layer.astype(np.float32) / 255
    return canvas

def paper(img, seed=11, amt=.05):
    n = vnoise(img.shape[0], img.shape[1], 220, seed, 2)
    f = vnoise(img.shape[0], img.shape[1], 30, seed + 1, 3)
    t = (n * .6 + f * .4 - .5) * amt
    return np.clip(img * (1 + t[..., None]), 0, 1)
