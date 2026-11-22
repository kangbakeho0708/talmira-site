/* 사람 그림 없이 사람을 보여 주는 세 가지 방법. 전부 2D 선과 면으로 그린다 (AI 그림 아님) */
var TalFigure = (function () {
  /* 뒷모습 외투 사람. 단위: 발 y=1, 머리 꼭대기 y=0, 가운데 x=0 */
  /* 외곽선 한 번 만들어 두고 채우기와 테두리 빛에 같이 쓴다 */
  const outline = (c) => {
    c.beginPath();
    c.moveTo(0, -.005);
    c.bezierCurveTo(.045, -.005, .07, .03, .066, .075);   /* 머리 오른쪽 */
    c.bezierCurveTo(.064, .1, .05, .12, .04, .13);
    c.bezierCurveTo(.09, .15, .15, .17, .19, .23);      /* 오른 어깨 */
    c.bezierCurveTo(.2, .3, .19, .4, .17, .5);          /* 팔 · 허리 */
    c.bezierCurveTo(.2, .68, .27, .86, .33, 1.0);       /* 외투 자락 */
    c.bezierCurveTo(.22, .985, .1, 1.0, 0, .99);
    c.bezierCurveTo(-.1, 1.0, -.22, .985, -.33, 1.0);
    c.bezierCurveTo(-.27, .86, -.2, .68, -.17, .5);
    c.bezierCurveTo(-.19, .4, -.2, .3, -.19, .23);
    c.bezierCurveTo(-.15, .17, -.09, .15, -.04, .13);
    c.bezierCurveTo(-.05, .12, -.064, .1, -.066, .075);
    c.bezierCurveTo(-.07, .03, -.045, -.005, 0, -.005);
    c.closePath();
  };
  const body = (c, kind, rim) => {
    outline(c); c.fill();
    if (rim) { c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = rim; c.lineWidth = .011; c.lineJoin = 'round'; outline(c); c.stroke(); c.restore(); }
    c.lineCap = 'round';
    if (kind === 'wanderer') {
      /* 땋은 머리 한 줄 (살짝 밝게), 허리에 찬 한손검의 칼집 */
      c.strokeStyle = 'rgba(40,36,48,1)'; c.lineWidth = .03; c.beginPath(); c.moveTo(.0, .1); c.bezierCurveTo(.03, .24, -.02, .36, .01, .52); c.stroke();
      c.strokeStyle = 'rgba(16,14,22,1)'; c.lineWidth = .024; c.beginPath(); c.moveTo(-.13, .58); c.lineTo(-.3, .92); c.stroke();
      c.strokeStyle = 'rgba(150,120,80,.7)'; c.lineWidth = .004; c.beginPath(); c.moveTo(-.135, .585); c.lineTo(-.3, .915); c.stroke();
      c.strokeStyle = 'rgba(190,160,110,.9)'; c.lineWidth = .012; c.beginPath(); c.moveTo(-.19, .585); c.lineTo(-.08, .61); c.stroke();
    }
    if (kind === 'guardian') {
      c.lineWidth = .065; c.beginPath(); c.moveTo(.15, .27); c.bezierCurveTo(.24, .2, .3, .1, .33, -.03); c.stroke();
      c.lineWidth = .05; c.beginPath(); c.moveTo(.33, -.03); c.lineTo(.35, -.09); c.stroke();
    }
    if (kind === 'merchant') {
      c.beginPath(); c.moveTo(-.23, .24); c.lineTo(.23, .24); c.lineTo(.2, .34); c.lineTo(-.2, .34); c.closePath(); c.fill();
      c.lineWidth = .06; c.beginPath(); c.moveTo(.18, .3); c.bezierCurveTo(.26, .42, .29, .52, .3, .62); c.stroke();
      c.lineWidth = .012; c.beginPath(); c.moveTo(.3, .62); c.lineTo(.3, .68); c.stroke();
    }
  };
  const glow = (c, x, y, r, col, a) => { const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col.replace('A', a)); g.addColorStop(1, col.replace('A', 0)); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2); };

  /* 가. 실루엣: 역광 속 뒷모습. sunX 0..1 은 해가 있는 쪽 */
  const silhouette = (c, w, h, o) => {
    const H = h * (o.size || .5), fx = w * (o.x == null ? .5 : o.x), fy = h * (o.feet == null ? .8 : o.feet), sunX = o.sunX == null ? .5 : o.sunX;
    glow(c, fx + (sunX - .5) * w * .3, fy - H * .55, H * .8, 'rgba(255,214,160,A)', .16);
    c.save(); c.translate(fx, fy - H); c.scale(H, H);
    c.fillStyle = 'rgba(0,0,0,.45)'; c.beginPath(); c.ellipse(0, 1.0, .38, .03, 0, 0, 6.29); c.fill();
    const side = sunX < .5 ? -1 : 1;
    const g = c.createLinearGradient(side * .3, 0, -side * .05, 0); g.addColorStop(0, o.rim || 'rgba(255,205,150,.85)'); g.addColorStop(1, 'rgba(255,205,150,0)');
    c.fillStyle = c.strokeStyle = o.ink || 'rgba(10,9,14,.96)'; body(c, o.kind, g);
    c.restore();
    if (o.kind === 'guardian') { glow(c, fx + .35 * H, fy - H * 1.09, H * .24, 'rgba(255,236,200,A)', .95); glow(c, fx + .35 * H, fy - H * 1.09, H * .05, 'rgba(255,255,255,A)', 1); }
    if (o.kind === 'merchant') { glow(c, fx + .3 * H, fy - H * .3, H * .24, 'rgba(255,170,90,A)', .8); glow(c, fx + .3 * H, fy - H * .3, H * .035, 'rgba(255,230,190,A)', 1); }
  };

  /* 나. 그림자: 멀리 선 작은 사람과, 그에게서 이쪽으로 길게 늘어진 그림자 */
  const shadow = (c, w, h, o) => {
    const H = h * (o.size || .2), fx = w * (o.x == null ? .5 : o.x), fy = h * (o.feet == null ? .64 : o.feet);
    /* 긴 그림자 (발에서 화면 아래로 넓어지며) */
    const g = c.createLinearGradient(0, fy, 0, h); g.addColorStop(0, 'rgba(0,0,0,.7)'); g.addColorStop(1, 'rgba(0,0,0,.05)');
    c.fillStyle = g; c.beginPath(); c.moveTo(fx - H * .12, fy); c.lineTo(fx + H * .12, fy);
    c.bezierCurveTo(fx + H * .6, fy + (h - fy) * .4, fx + w * .18, h, fx + w * .26, h);
    c.lineTo(fx - w * .26, h); c.bezierCurveTo(fx - w * .18, h, fx - H * .6, fy + (h - fy) * .4, fx - H * .12, fy); c.closePath(); c.fill();
    glow(c, fx, fy - H * .5, H * 1.6, 'rgba(255,214,160,A)', .3);
    c.save(); c.translate(fx, fy - H); c.scale(H, H); c.fillStyle = c.strokeStyle = 'rgba(8,8,12,.96)'; body(c, o.kind, 'rgba(255,205,150,.6)'); c.restore();
  };

  /* 다. 상징: 사람 대신 그 사람을 뜻하는 표식 하나 */
  const symbol = (c, w, h, o) => {
    const cx = w * .5, cy = h * .42, R = Math.min(w, h) * .26;
    c.save(); c.lineCap = 'round';
    if (o.kind === 'wanderer') {
      /* 일곱 눈금 고리, 자정 눈금만 켜짐 */
      c.strokeStyle = 'rgba(240,220,174,.6)'; c.lineWidth = Math.max(1, R * .012); c.beginPath(); c.arc(cx, cy, R, 0, 6.29); c.stroke();
      for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + i * Math.PI * 2 / 7, on = i === 6; c.strokeStyle = on ? '#8fbcff' : 'rgba(240,220,174,.7)'; c.lineWidth = R * (on ? .035 : .018); c.beginPath(); c.moveTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); c.lineTo(cx + Math.cos(a) * R * 1.16, cy + Math.sin(a) * R * 1.16); c.stroke(); if (on) glow(c, cx + Math.cos(a) * R * 1.08, cy + Math.sin(a) * R * 1.08, R * .35, 'rgba(140,180,255,A)', .7); }
    }
    if (o.kind === 'guardian') {
      /* 고리 위 제 시각 눈금 하나에 해가 붙잡혀 있다 */
      const a = -Math.PI / 2 + (o.hour || 0) * Math.PI * 2 / 7;
      c.strokeStyle = 'rgba(240,220,174,.45)'; c.lineWidth = Math.max(1, R * .012); c.beginPath(); c.arc(cx, cy, R, 0, 6.29); c.stroke();
      for (let i = 0; i < 7; i++) { const b = -Math.PI / 2 + i * Math.PI * 2 / 7; c.strokeStyle = 'rgba(240,220,174,.5)'; c.lineWidth = R * .016; c.beginPath(); c.moveTo(cx + Math.cos(b) * R, cy + Math.sin(b) * R); c.lineTo(cx + Math.cos(b) * R * 1.12, cy + Math.sin(b) * R * 1.12); c.stroke(); }
      /* 손: 중심에서 눈금까지 뻗은 굵은 선 */
      c.strokeStyle = 'rgba(14,12,18,.95)'; c.lineWidth = R * .11; c.beginPath(); c.moveTo(cx, cy + R * .9); c.lineTo(cx + Math.cos(a) * R * .9, cy + Math.sin(a) * R * .9); c.stroke();
      glow(c, cx + Math.cos(a) * R, cy + Math.sin(a) * R, R * .6, 'rgba(255,230,180,A)', .9); glow(c, cx + Math.cos(a) * R, cy + Math.sin(a) * R, R * .12, 'rgba(255,255,255,A)', 1);
    }
    if (o.kind === 'merchant' || o.kind === 'seven') {
      const n = o.kind === 'seven' ? 7 : 1;
      for (let i = 0; i < n; i++) { const x = n === 1 ? cx : w * (.15 + .7 * i / 6), y = n === 1 ? cy : cy + Math.sin(i * 1.3) * h * .04, r = n === 1 ? R * .9 : R * .45; glow(c, x, y, r, 'rgba(255,170,90,A)', .75); glow(c, x, y, r * .12, 'rgba(255,235,200,A)', 1); c.strokeStyle = 'rgba(20,14,10,.9)'; c.lineWidth = r * .06; c.beginPath(); c.moveTo(x, y - r * .4); c.lineTo(x, y - r * .9); c.stroke(); }
    }
    if (o.kind === 'bond') {
      /* 세 가닥 실이 한 매듭으로 */
      c.strokeStyle = 'rgba(240,210,150,.85)'; c.lineWidth = Math.max(1.5, R * .02);
      [[-.9, .25], [0, -.1], [.9, .25]].forEach((s) => { c.beginPath(); c.moveTo(cx + s[0] * R, cy - R * 1.1); c.bezierCurveTo(cx + s[0] * R * .4, cy - R * .4 + s[1] * R, cx + s[0] * R * .1, cy + s[1] * R * .2, cx, cy); c.stroke(); c.beginPath(); c.moveTo(cx, cy); c.bezierCurveTo(cx - s[0] * R * .1, cy + R * .4, cx - s[0] * R * .5, cy + R * .7, cx - s[0] * R * .8, cy + R * 1.1); c.stroke(); });
      c.fillStyle = 'rgba(240,210,150,.95)'; c.beginPath(); c.arc(cx, cy, R * .08, 0, 6.29); c.fill(); glow(c, cx, cy, R * .5, 'rgba(240,210,150,A)', .5);
    }
    c.restore();
  };
  return { silhouette, shadow, symbol };
})();
