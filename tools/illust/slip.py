"""미끄러짐 (2판): 낮게 엎드린 눈높이에서 본 갈라진 굳은 땅, 틈에서 돋은 새싹"""
import numpy as np, cv2
from scipy.spatial import cKDTree
from kit import *
W, H = 720, 1080
cv = Canvas(W, H, 15); u, v = cv.u, cv.v
HZ = .34
# 하늘: 뒤에서 낮게 비치는 따뜻한 빛, 흐림 (얕은 초점)
cv.sky('#8a9bb2', '#e2d6c2', '#f7dfb4', horiz=HZ, sun=(.26, .27), halo='#ffd9a0', halo_k=3, sun_k=30, sun_amt=1.1, cloud=.35)
cv.img = cv2.GaussianBlur(cv.img, (0, 0), 6)
# 땅 좌표 (원근)
below = v > HZ + .002
z = 1.0 / np.maximum(v - HZ, 1e-3); xg = (u - .5) * z
r = np.random.default_rng(5)
seeds = np.stack([r.uniform(-60, 60, 9000), r.uniform(0, 200, 9000) ** 1.0], 1)
seeds[:, 1] = r.uniform(1, 160, 9000)
tree = cKDTree(seeds)
pts = np.stack([xg[below], z[below]], 1)
d, idx = tree.query(pts, k=2)
edge = np.zeros((H, W), np.float32); cell = np.zeros((H, W), np.int32); dd = np.zeros((H, W), np.float32)
dd[below] = d[:, 1] - d[:, 0]; cell[below] = idx[:, 0]
crack_w = .12
crack = (dd < crack_w) & below
# 판 색: 셀마다 조금 다른 흙빛, 가장자리가 들려 밝음
tone = r.uniform(.85, 1.1, len(seeds))
base = mix(np.full((H, W, 3), C('#8a7c6c')), C('#b9a68c'), smooth(v, HZ, .9) * 0 + .5)
plate = base * tone[cell][..., None]
lift = smooth(dd, crack_w, crack_w + .5) * (1 - smooth(dd, crack_w + .5, 2.5))
plate = plate * (1 + .18 * (1 - lift[..., None]) * (dd < 2.5)[..., None])  # 가장자리 들림 밝음
grain = vnoise(H, W, 90, 6, 3) * .6 + vnoise(H, W, 300, 7, 2) * .4; plate *= (.82 + .36 * grain[..., None])
pits = (vnoise(H, W, 260, 8, 2) > .72).astype(np.float32); plate *= (1 - pits[..., None] * .18)
plate = mix(plate, C('#6f6050'), smooth(vnoise(H, W, 12, 9, 4), .55, .75) * .35)
# 낮은 해: 판 왼쪽 위 테가 밝고, 틈 오른쪽은 그림자
plate = mix(plate, C('#f2d6a6'), (smooth(dd, crack_w, crack_w + .15) * (1 - smooth(dd, crack_w + .15, crack_w + .45)) * .55))
cv.put(plate, below.astype(np.float32))
cv.put(C('#1c140f'), crack.astype(np.float32) * 1.0)
face = ((dd >= crack_w) & (dd < crack_w * 2.2) & below).astype(np.float32)
gy_ = cv2.Sobel(dd, cv2.CV_32F, 0, 1, ksize=3)
cv.put(C('#4a3c30'), face * (gy_ < 0) * .7)
# 먼 곳은 옅고 흐리게 (공기, 얕은 초점)
far = smooth(v, HZ + .12, HZ).astype(np.float32)
blur = cv2.GaussianBlur(cv.img, (0, 0), 5)
cv.img = cv.img * (1 - far[..., None]) + blur * far[..., None]
cv.img = mix(cv.img, C('#e8d4b4'), smooth(v, HZ + .15, HZ) * .6)
near = smooth(v, .9, 1.0)
cv.img = cv.img * (1 - near[..., None]) + cv2.GaussianBlur(cv.img, (0, 0), 3) * near[..., None]
# 새싹: 틈에서 돋음. 비치는 잎 (뒤에서 빛)
bx, by = .52 * W, .7 * H
sprout = np.zeros((H, W), np.float32); vein = np.zeros((H, W), np.float32)
stem = [(bx, by), (bx + 4, by - 50), (bx - 2, by - 110)]
cv2.polylines(sprout, [np.array(stem, np.int32).reshape(-1, 1, 2)], False, 1., 7, cv2.LINE_AA)
leaves = [((bx - 2, by - 108), -2.3, 120, 46), ((bx - 1, by - 110), -.6, 110, 40), ((bx + 3, by - 60), -2.8, 80, 28), ((bx + 3, by - 62), -.25, 70, 26)]
for (ox, oy), a, L, wd in leaves:
    tip = (ox + np.cos(a) * L, oy + np.sin(a) * L * .7 - L * .25)
    n = np.array([-np.sin(a), np.cos(a)])
    ctrl = [(ox, oy)]
    for t in np.linspace(0, 1, 16)[1:]:
        px = ox + (tip[0] - ox) * t; py = oy + (tip[1] - oy) * t - np.sin(t * np.pi) * L * .12
        ctrl.append((px + n[0] * wd * np.sin(t * np.pi) ** .8 * .5, py + n[1] * wd * np.sin(t * np.pi) ** .8 * .5))
    back = [(ox + (tip[0] - ox) * t - n[0] * wd * np.sin(t * np.pi) ** .8 * .5, oy + (tip[1] - oy) * t - np.sin(t * np.pi) * L * .12 - n[1] * wd * np.sin(t * np.pi) ** .8 * .5) for t in np.linspace(1, 0, 16)]
    cv2.fillPoly(sprout, [np.array(ctrl + back, np.int32)], 1., cv2.LINE_AA)
    mid = [(ox + (tip[0] - ox) * t, oy + (tip[1] - oy) * t - np.sin(t * np.pi) * L * .12) for t in np.linspace(0, 1, 16)]
    cv2.polylines(vein, [np.array(mid, np.int32).reshape(-1, 1, 2)], False, 1., 1, cv2.LINE_AA)
sprout = cv2.GaussianBlur(sprout, (0, 0), .8)
dl = np.hypot(u - .26, v - .27)
leafc = mix(np.full((H, W, 3), C('#3c7a2a')), C('#c8f07a'), smooth(-v, -.66, -.52) * .8)
leafc = leafc + C('#e8ff9a') * (np.exp(-np.hypot(u - .5, v - .6) * 7) * .35)[..., None]
fold = np.zeros((H, W), np.float32)
for (ox, oy), a, L, wd in leaves:
    tip = (ox + np.cos(a) * L, oy + np.sin(a) * L * .7 - L * .25)
    n = np.array([-np.sin(a), np.cos(a)])
    half = [(ox + (tip[0] - ox) * t + n[0] * wd * np.sin(t * np.pi) ** .8 * .5, oy + (tip[1] - oy) * t - np.sin(t * np.pi) * L * .12 + n[1] * wd * np.sin(t * np.pi) ** .8 * .5) for t in np.linspace(0, 1, 16)]
    mid = [(ox + (tip[0] - ox) * t, oy + (tip[1] - oy) * t - np.sin(t * np.pi) * L * .12) for t in np.linspace(1, 0, 16)]
    cv2.fillPoly(fold, [np.array(half + mid, np.int32)], 1., cv2.LINE_AA)
leafc = leafc * (1 - fold[..., None] * .28)
er = sprout - cv2.erode(sprout, np.ones((3, 3), np.uint8))
leafc = mix(leafc, C('#f4ffc8'), np.clip(er * 2, 0, 1) * .8)
cv.put(leafc, sprout)
cv.put(C('#eaffb0'), vein * sprout * .5)
# 그림자 (해 반대쪽, 길게)
sh = np.roll(np.roll(sprout, 24, 0), 30, 1) * below * (1 - sprout)
cv.img = cv.img * (1 - cv2.GaussianBlur(sh, (0, 0), 4)[..., None] * .35)
# 틈에서 새어 나오는 금빛 (멈춤이 약해지는 곳)
glowcrack = crack.astype(np.float32) * np.exp(-np.hypot((u - .52) * 1.2, (v - .72) * 2.2) * 9)
cv.gold += cv2.GaussianBlur(glowcrack, (0, 0), .7) * .9
# 이슬 한 방울
cv2.circle(cv.glow, (int(bx + 52), int(by - 140)), 3, (1., 1., .95), -1, cv2.LINE_AA)
cv.glow += C('#ffffff')[None, None] * (np.exp(-np.hypot((u - (bx + 52) / W) * W, (v - (by - 140) / H) * H) / 6) * .5)[..., None]
cv.lamp(.26, .27, 1.5, '#fff0d0')
save(finish(cv, radii=(10, 5, 2), thr=.022, detail=.45, dust=120, dust_c=(.4, .4), dust_s=(.25, .15), gold_col='#ffd27a'), 'out/lore5.png')
print('ok')
