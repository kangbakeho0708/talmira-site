"""멈춤: 부서지다 멈춘 파도 (2판). 얇은 물마루는 비치고, 두꺼운 몸통은 어둡고, 골은 가장 어둡다"""
import numpy as np, cv2
from kit import *
W, H = 720, 1080

def voronoi_edges(H, W, n, seed, thick=1):
    r = np.random.default_rng(seed); pts = np.full((H, W), 255, np.uint8)
    for i in range(n): pts[r.integers(H), r.integers(W)] = 0
    _, lab = cv2.distanceTransformWithLabels(pts, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    e = (np.abs(np.diff(lab, axis=0, prepend=lab[:1])) > 0) | (np.abs(np.diff(lab, axis=1, prepend=lab[:, :1])) > 0)
    e = e.astype(np.float32)
    if thick > 1: e = cv2.dilate(e, np.ones((thick, thick), np.uint8))
    return e

def flow_noise(H, W, ang, stretch, sc, seed):
    big = vnoise(int(H * 1.6), int(W * 1.6), sc, seed, 4)
    big = cv2.resize(big, (int(W * 1.6), int(H * 1.6 / stretch)))
    big = cv2.resize(big, (int(W * 1.6), int(H * 1.6)))
    M = cv2.getRotationMatrix2D((W * .8, H * .8), ang, 1)
    rot = cv2.warpAffine(big, M, (int(W * 1.6), int(H * 1.6)), borderMode=cv2.BORDER_REFLECT)
    return rot[int(H * .3):int(H * .3) + H, int(W * .3):int(W * .3) + W]

def scene():
    cv = Canvas(W, H, 14)
    u, v = cv.u, cv.v
    cv.sky('#5f82ad', '#c3d2df', '#eef1ee', horiz=.52, sun=(.82, .14), halo='#fff4dc', halo_k=4, sun_k=40, cloud=.45)
    cv.sea(.52, '#5c7c99', '#1b3046', sunx=.82, refc='#fff4dc')
    # 파도 몸통: 왼쪽 아래에서 솟아 오른쪽으로 말린 입술. 입술 아래는 통 (빈 곳)
    outer = [(-.05, 1.0), (-.05, .7), (.1, .6), (.25, .5), (.4, .4), (.52, .33), (.62, .29), (.71, .29), (.79, .32), (.84, .37), (.85, .42), (.82, .45)]
    inner = [(.78, .44), (.74, .41), (.68, .4), (.62, .42), (.58, .48), (.6, .56), (.7, .6), (.8, .585), (.87, .56), (.94, .6), (1.05, .65), (1.05, 1.0)]
    P = rough(outer + inner, 4, .02, 41); m = mask_poly(H, W, cv.P(P), 1.2)
    # 통 안: 어둡고 푸른 물 (빛이 약함)
    tube = rough([(.59, .48), (.64, .41), (.7, .4), (.77, .42), (.84, .45), (.88, .52), (.86, .58), (.78, .6), (.68, .6), (.6, .56)], 3, .015, 46)
    tm = mask_poly(H, W, cv.P(tube), 2)
    tcol = mix(np.full((H, W, 3), C('#5cc4bc')), C('#12475a'), smooth(v, .42, .6))
    cv.put(tcol * (.85 + .3 * flow_noise(H, W, -10, 5, 30, 47)[..., None]), tm * (1 - m))
    dist = cv2.distanceTransform((m > .5).astype(np.uint8), cv2.DIST_L2, 5)
    thick = np.clip(dist / 110, 0, 1)
    t = np.clip(thick * .5 + smooth(v, .32, .8) * .65, 0, 1)
    thin_c, mid_c, deep_c = C('#b4f4e2'), C('#2b98a0'), C('#0a2033')
    col = np.where(t[..., None] < .45, thin_c * (1 - t[..., None] / .45) + mid_c * (t[..., None] / .45), mid_c * (1 - (t[..., None] - .45) / .55) + deep_c * ((t[..., None] - .45) / .55))
    backlit = np.exp(-np.hypot(u - .72, (v - .33) * 1.4) * 5.5) * (1 - t)
    col = col + C('#e0fff2') * backlit[..., None] * .6
    fl = flow_noise(H, W, -55, 8, 40, 43)
    col = col * (.88 + .24 * fl[..., None])
    col = mix(col, C('#d2e2ea'), smooth(fl, .64, .82) * (1 - t) * .3)
    cv.put(col, m)
    cv.glow *= (1 - np.maximum(m, tm))[..., None]
    lipglow = tm * (1 - m) * np.exp(-((v - .43) / .025) ** 2) * smooth(u, .6, .7)
    cv.put(C('#c8fff0'), np.clip(lipglow, 0, 1) * .7)
    cv.put(C('#0e3a4a'), tm * (1 - m) * np.exp(-((u - .6) / .03) ** 2) * .5)
    # 거품 결: 흐름 따라 늘어진 가는 줄기 (갈라진 유리처럼 안 되게, 드문드문)
    f2 = flow_noise(H, W, -55, 10, 18, 48); f3 = flow_noise(H, W, -40, 4, 60, 49)
    vein = smooth(1 - np.abs(f2 - .5) * 30, .3, 1) * smooth(f3, .5, .62)
    lace = vein * smooth(v, .5, .85) * m
    cv.put(C('#e4f2f2'), np.clip(lace, 0, 1) * .55)
    seaf = smooth(1 - np.abs(flow_noise(H, W, 0, 12, 20, 50) - .5) * 12, .3, 1) * smooth(v, .82, .97) * (1 - m)
    cv.put(C('#d4e3e8'), np.clip(seaf, 0, 1) * .6)
    # 입술 가장자리 거품 띠 (굳은 흰 덩어리, 위는 밝고 아래는 그늘)
    r = np.random.default_rng(4); crest = np.zeros((H, W), np.float32); csh = np.zeros((H, W), np.float32)
    path = [(.5, .345), (.58, .31), (.66, .29), (.74, .295), (.8, .32), (.84, .37), (.845, .42), (.82, .45)]
    path = np.array(path)
    for i in range(420):
        s = r.random() ** .8; k = s * (len(path) - 1); j = min(len(path) - 2, int(k)); f_ = k - j
        x, y = path[j] * (1 - f_) + path[j + 1] * f_
        x += r.normal() * .008; y += r.normal() * .006 - .004
        rr = int(r.integers(2, 6 + int(8 * s)))
        cv2.circle(crest, (int(x * W), int(y * H)), rr, 1., -1, cv2.LINE_AA)
        cv2.circle(csh, (int(x * W) + rr // 3, int(y * H) + rr // 2), rr, 1., -1, cv2.LINE_AA)
    crest = cv2.GaussianBlur(crest, (0, 0), 1); csh = cv2.GaussianBlur(csh, (0, 0), 1.5) * (1 - crest)
    cv.put(C('#7fa8b8'), csh * .55)
    cv.put(mix(np.full((H, W, 3), C('#ffffff')), C('#c5dce6'), smooth(v, .3, .44) * .8), crest)
    # 멈춘 물보라: 물마루 앞으로 흩어진 방울 줄기, 반짝임
    drops = np.zeros((H, W), np.float32); spark = np.zeros((H, W), np.float32)
    for i in range(220):
        a = r.uniform(-.9, .3); d = r.gamma(2, .035)
        x, y = .84 + np.cos(a) * d * 1.1, .4 + np.sin(a) * d - d * .5
        L = int(r.integers(2, 9)); ang = np.degrees(a)
        cv2.ellipse(drops, (int(x * W), int(y * H)), (L, max(1, L // 3)), ang, 0, 360, float(r.uniform(.6, 1)), -1, cv2.LINE_AA)
        if r.random() < .3: cv2.circle(spark, (int(x * W) - 1, int(y * H) - 1), 1, 1., -1, cv2.LINE_AA)
    cv.put(C('#e6f6f8'), cv2.GaussianBlur(drops, (0, 0), .7))
    cv.glow += C('#ffffff')[None, None] * (cv2.GaussianBlur(spark, (0, 0), 1) * 1.2 + cv2.GaussianBlur(drops, (0, 0), 4) * .15)[..., None]
    return cv

cv = scene()
save(finish(cv, radii=(10, 5, 2), thr=.022, detail=.4, dust=0), 'out/lore4.png')
print('ok')
