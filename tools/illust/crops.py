"""땅 그림에서 세로 그림 (peek, card) 잘라내기"""
import cv2
FOC = {0: .62, 1: .5, 2: .66, 3: .64, 4: .6, 5: .62, 6: .7}
def tall(k, fx=None, dark=1.0):
    im = cv2.imread(f'out/land{k}.png'); H, W = im.shape[:2]
    cw = int(H * 720 / 1080); x = int((fx if fx is not None else FOC[k]) * W - cw / 2); x = max(0, min(W - cw, x))
    c = cv2.resize(im[:, x:x + cw], (720, 1080), interpolation=cv2.INTER_AREA)
    return (c * dark).astype('uint8')
for k in range(7): cv2.imwrite(f'out/peek{k}.png', tall(k))
G = {0: 5, 1: 1, 2: 0, 3: 2, 4: 3, 5: 4, 6: 6}
cv2.imwrite('out/card0-0.png', tall(2, .45)); cv2.imwrite('out/card0-1.png', tall(3, .3))
cv2.imwrite('out/card3-0.png', tall(4, .55))
print('ok')
