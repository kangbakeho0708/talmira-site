"""메인 그림 (붓질판). 해 자리 (.645, .603) 는 사이트 계산과 맞춰 고정"""
import numpy as np, cv2
from kit import *
W, H = 2133, 1000
SX, SY = .64502, .60259
cv = Canvas(W, H, 88); u, v = cv.u, cv.v
L = (.6, .15, .5)
cv.sky('#03050f', '#3a2a52', '#ff9a5a', horiz=.62, sun=(SX, SY), sunc='#fff2cc', halo='#ffb070', halo_k=2.2, sun_k=26, sun_amt=1.25, cloud=.55, cloudc='#ffb27a', cloud_dark='#40284a', cseed=31)
cv.img = mix(cv.img, C('#05070f'), smooth(u, .45, 0) * smooth(v, .7, .0) * .55)  # 글씨 쪽 (왼쪽) 하늘을 어둡게
cv.stars(900, .45, 5)
cv.glow *= (1 - smooth(v, .2, .5))[..., None] ** 1 + 0
# 먼 산 (옅은 보라, 해 쪽 테 빛). 해 자리는 골짜기로 비워 해가 보이게
skyc = cv.img.copy()
cv.ridge(.6, .1, 5, 101, '#6a4a6a', '#e8a07a', light=L, fog='#ffb27a', fogamt=.6, n=60, rim='#ffd8a0')
notch = np.exp(-((u - SX) / .045) ** 2) * (1 - smooth(v, SY + .005, SY + .03))
cv.img = cv.img * (1 - notch[..., None]) + skyc * notch[..., None]
cv.fogband(.56, .66, '#ffc890', .7, 7, 3)
# 오른쪽 큰 산 (해 옆 주인공 실루엣)
mt = rough([(.62, .7), (.72, .52), (.78, .4), (.81, .36), (.84, .4), (.9, .5), (.97, .58), (1.05, .62), (1.05, .75), (.62, .75)], 5, .05, 102)
m = mask_poly(H, W, cv.P(mt)); cv.put(facets(H, W, m, (-.7, -.2, .4), '#3a2232', '#c9705a', n=60, seed=103, stretch=2.5, rim='#ffd49a', rimw=5), m)
cv.img = mix(cv.img, C('#ffb27a'), m * smooth(v, .55, .72) * .55)
cv.ridge(.68, .1, 6, 104, '#3a2234', '#b8645a', light=L, fog='#f09868', fogamt=.55, n=60, rim='#ffcf94')
cv.fogband(.64, .74, '#ffb880', .75, 9, 4)   # 골짜기 구름 바다
cv.ridge(.76, .1, 5, 105, '#22141f', '#7a3c40', light=L, fog='#c86a58', fogamt=.45, n=50, rim='#ffb878')
cv.fogband(.72, .82, '#e08a68', .5, 11, 5)
cv.ridge(.88, .12, 4, 106, '#120a10', '#4a2428', light=L, fog='#8a4a48', fogamt=.25, n=40)
# 앞 왼쪽 낮은 검은 언덕 (옛 쐐기 대신, 글씨 바닥을 받쳐줌)
fg = rough([(-.02, .78), (.12, .8), (.26, .86), (.4, .94), (.5, 1.02), (-.02, 1.02)], 5, .04, 107)
fm = mask_poly(H, W, cv.P(fg)); cv.put(facets(H, W, fm, L, '#07040a', '#2a1620', n=30, seed=108, rim='#ff9a6a', rimw=3), fm)
cv.ridge(1.0, .07, 4, 109, '#07040a', '#22121a', light=L, n=30)
# 해에서 바다처럼 깔린 구름 위로 비치는 빛 길
cv.glow += C('#ffcf8a')[None, None] * (np.exp(-(((u - SX) / .05) ** 2 + ((v - .68) / .02) ** 2)) * .35)[..., None]
p = finish(cv, radii=(16, 8, 4), thr=.026, detail=.25, dust=0)
for w_, h_ in [(2560, 1200), (1920, 900), (1280, 600)]:
    o = (np.clip(p, 0, 1) * 255).astype(np.uint8); o = cv2.resize(o, (w_, h_), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(f'out/hero-{w_}.png', cv2.cvtColor(o, cv2.COLOR_RGB2BGR))
print('ok')
