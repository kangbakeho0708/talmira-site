"""마무리: 붓질 → 금빛 균열과 빛 → 금가루 → 종이 결"""
import sys, time, numpy as np, cv2
from base import *
name = sys.argv[1] if len(sys.argv) > 1 else 'frozen'
img = np.load('/tmp/fz_img.npy'); gold = np.load('/tmp/fz_gold.npy')
H, W = img.shape[:2]
t0 = time.time()
p = paint(img, radii=(14, 7, 3), thr=.028, seed=3, maxlen=10)
p = .8 * p + .2 * cv2.bilateralFilter((img * 255).astype(np.uint8), 7, 40, 7).astype(np.float32) / 255  # 세부 조금 되살림
print('paint', round(time.time() - t0, 1))
gcol = np.array(hexc('#ffcf7a'))
glow = cv2.GaussianBlur(gold, (0, 0), 6) * 1.6 + cv2.GaussianBlur(gold, (0, 0), 18) * 1.2
p = 1 - (1 - p) * (1 - np.clip(glow, 0, 1)[..., None] * gcol * .55)
p = p * (1 - gold[..., None] * .9) + np.array(hexc('#fff0c4')) * gold[..., None] * .9
# 금가루와 얼음 반짝임 (멈춘 채 떠 있음)
r = np.random.default_rng(12); dust = np.zeros((H, W), np.float32)
for k in range(260):
    x, y = r.normal(.68, .14) * W, r.normal(.42, .15) * H
    if 0 < x < W and 0 < y < H: cv2.circle(dust, (int(x), int(y)), int(r.integers(1, 3)), float(r.uniform(.3, 1)), -1, cv2.LINE_AA)
dg = cv2.GaussianBlur(dust, (0, 0), 1.2) + cv2.GaussianBlur(dust, (0, 0), 5) * .8
p = 1 - (1 - p) * (1 - np.clip(dg, 0, 1)[..., None] * gcol * .8)
p = paper(p, amt=.06)
o = (np.clip(p, 0, 1) * 255).astype(np.uint8)
cv2.imwrite(f'/tmp/{name}_final.png', cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
print('done', round(time.time() - t0, 1))
