/* 랜드마크 · 크기 단서 · 삶의 흔적. 전부 선과 면 (가제. 강백호 선그림이 오면 갈아 끼운다)
   좌표: 세계 x (좌우, 카메라 기준), z (앞으로 거리). 화면 자리는 깊이 지도에서 땅을 찾아 정한다 */
var TalMarks = (function () {
  const lin = (h) => { const n = parseInt(h.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => Math.pow(v / 255, 2.2)); };
  const aces = (c) => c.map((v) => { v = Math.max(0, v); v = (v * (2.51 * v + .03)) / (v * (2.43 * v + .59) + .14); return Math.pow(Math.min(1, v), 1 / 2.2); });
  const rgb = (c, a) => 'rgba(' + c.map((v) => Math.round(v * 255)).join(',') + ',' + (a == null ? 1 : a) + ')';
  const mix = (a, b, k) => a.map((v, i) => v + (b[i] - v) * k);

  /* 장면 도우미: 투영, 깊이, 안개 */
  const Scene = function (P, w, h, depth) {
    this.P = P; this.w = w; this.h = h; this.depth = depth; /* depth: Float32Array w*h, 세계 거리 */
    this.sun = TalEngine.sunScreen(P, w, h);
    this.FAR = 700;
    const CH = lin(P.hor), CS = lin(P.sun), CT = lin(P.top), si = Math.min(P.si == null ? 3 : P.si, 1.5);
    this.CH = CH; this.CS = CS; this.CT = CT; this.si = si;
    this.exp = P.exp == null ? 1 : P.exp;
    this.fog = P.fog == null ? .005 : P.fog;
    this.sd = (function (el, az) { const e = el * Math.PI / 180, a = az * Math.PI / 180; return [Math.sin(a) * Math.cos(e), Math.sin(e), Math.cos(a) * Math.cos(e)]; })(P.el == null ? 5 : P.el, P.az || 0);
  };
  /* 세계 x, 거리 z → 화면 x */
  Scene.prototype.px = function (x, z) { return (1.7 * x / z * this.h + this.w) / 2; };
  /* 화면 x, 거리 z → 그 거리의 땅이 있는 화면 y (아래에서 위로 깊이가 z 를 넘는 첫 줄) */
  Scene.prototype.ground = function (px, z) {
    const w = this.w, h = this.h, X = Math.max(0, Math.min(w - 1, Math.round(px)));
    for (let y = h - 1; y >= 0; y--) { if (this.depth[y * w + X] >= z) return y; }
    return -1;
  };
  /* 세계 높이 → 거리 z 에서의 화면 픽셀 높이 */
  Scene.prototype.ph = function (hw, z) { return hw * (1.7 / z) * this.h / 2; };
  /* 거리 z 와 화면 x 에서의 안개 비율과 안개 색 (셰이더 fogc 와 같은 꼴) */
  Scene.prototype.fogAt = function (z, px) {
    let f = 1 - Math.exp(-z * this.fog);
    const a = Math.min(1, Math.max(0, (z - this.FAR * .55) / (this.FAR * .65))); f = Math.max(f, a * a * (3 - 2 * a));
    const ux = (px * 2 - this.w) / this.h, sux = this.sun ? (this.sun.x * this.w * 2 - this.w) / this.h : 9;
    const mu = Math.max(0, 1 - Math.abs(ux - sux) * .9) * Math.max(0, Math.min(1, (this.sd[1] + .1) * 4));
    const fc = mix(this.CH.map((v) => v * .9), this.CS.map((v) => v * this.si * .7), Math.pow(mu, 6) * .6);
    return { f, col: fc };
  };
  /* 물체의 선형 색 → 안개 섞고 노출 · 톤맵 거친 화면 색 */
  Scene.prototype.shade = function (linCol, z, px, a) {
    const fg = this.fogAt(z, px); const c = mix(linCol, fg.col, fg.f).map((v) => v * this.exp);
    return rgb(aces(c), a);
  };
  /* 빛을 받는 면의 선형 색: 알베도 × (해 + 하늘) */
  Scene.prototype.lit = function (albedo, facing) {
    const dif = Math.max(0, facing == null ? .6 : facing) * Math.max(0, this.sd[1] * 2 + .3);
    const amb = .55; const skyA = mix(this.CH, this.CT, .5);
    const sunT = this.CS.map((v) => v * (this.P.si == null ? 3 : this.P.si) * .9);
    return albedo.map((v, i) => v * (sunT[i] * dif + skyA[i] * amb * .75));
  };
  Scene.prototype.glow = function (c, x, y, r, col, a) { const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, rgb(col, a)); g.addColorStop(.35, rgb(col, a * .35)); g.addColorStop(1, rgb(col, 0)); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2); };

  /* 왼쪽에서 오는 해면 왼면이 밝다. facing 값 두 개 (왼면, 오른면) */
  const faces = (S) => { const l = S.sd[0] < 0 ? .9 : .25, r = S.sd[0] < 0 ? .25 : .9; return [l, r]; };

  /* 풍차: 몸통 원뿔대 + 지붕 + 날개 넷 */
  const windmill = (c, S, o) => {
    const z = o.z, x = o.x, px = S.px(x, z), gy = S.ground(px, z); if (gy < 0) return;
    const H = S.ph(o.h || 14, z), W = H * .34, al = lin(o.color || '#8a7556'), [fl, fr] = faces(S);
    const cl = S.shade(S.lit(al, fl), z, px), cr = S.shade(S.lit(al, fr), z, px), roof = S.shade(S.lit(lin('#4a3a30'), .5), z, px), wing = S.shade(S.lit(lin('#d8ccb0'), .7), z, px, .95);
    /* 몸통 두 면 */
    c.fillStyle = cl; c.beginPath(); c.moveTo(px - W * .5, gy); c.lineTo(px - W * .34, gy - H * .68); c.lineTo(px, gy - H * .68); c.lineTo(px, gy); c.closePath(); c.fill();
    c.fillStyle = cr; c.beginPath(); c.moveTo(px, gy); c.lineTo(px, gy - H * .68); c.lineTo(px + W * .34, gy - H * .68); c.lineTo(px + W * .5, gy); c.closePath(); c.fill();
    /* 지붕 */
    c.fillStyle = roof; c.beginPath(); c.moveTo(px - W * .42, gy - H * .66); c.quadraticCurveTo(px, gy - H * 1.02, px + W * .42, gy - H * .66); c.closePath(); c.fill();
    /* 날개 */
    const hx = px + W * .05, hy = gy - H * .74, L = H * .62; c.strokeStyle = wing; c.lineCap = 'round'; c.lineWidth = Math.max(1, H * .012);
    for (let i = 0; i < 4; i++) { const a = (o.rot || .4) + i * Math.PI / 2; c.beginPath(); c.moveTo(hx, hy); c.lineTo(hx + Math.cos(a) * L, hy + Math.sin(a) * L); c.stroke();
      const bx = hx + Math.cos(a) * L * .25, by = hy + Math.sin(a) * L * .25, ex = hx + Math.cos(a) * L, ey = hy + Math.sin(a) * L, nx = -Math.sin(a) * L * .09, ny = Math.cos(a) * L * .09;
      c.fillStyle = wing; c.globalAlpha = .75; c.beginPath(); c.moveTo(bx, by); c.lineTo(bx + nx, by + ny); c.lineTo(ex + nx * .6, ey + ny * .6); c.lineTo(ex, ey); c.closePath(); c.fill(); c.globalAlpha = 1; }
    c.fillStyle = roof; c.beginPath(); c.arc(hx, hy, Math.max(1, H * .02), 0, 6.29); c.fill();
  };

  /* 집 (작은 지붕 몇 채) */
  const houses = (c, S, o) => {
    const z = o.z, n = o.n || 5, al = lin(o.color || '#b8a98a'), rf = lin(o.roof || '#7a3d34'), [fl, fr] = faces(S);
    for (let i = 0; i < n; i++) {
      const x = o.x + (i - (n - 1) / 2) * (o.gap || 7) + Math.sin(i * 7.3) * 2, zz = z + Math.cos(i * 3.1) * (o.gap || 7) * .6;
      const px = S.px(x, zz), gy = S.ground(px, zz); if (gy < 0) continue;
      const H = S.ph(o.h || 4.5, zz), W = H * (1.1 + (i % 3) * .3);
      c.fillStyle = S.shade(S.lit(al, fl), zz, px); c.fillRect(px - W / 2, gy - H * .6, W / 2, H * .6);
      c.fillStyle = S.shade(S.lit(al, fr), zz, px); c.fillRect(px, gy - H * .6, W / 2, H * .6);
      c.fillStyle = S.shade(S.lit(rf, .6), zz, px); c.beginPath(); c.moveTo(px - W * .56, gy - H * .58); c.lineTo(px, gy - H); c.lineTo(px + W * .56, gy - H * .58); c.closePath(); c.fill();
      if (o.lit && (i % 2 === 0)) { const wy = gy - H * .3; S.glow(c, px + W * .15, wy, H * .35, [1, .75, .4], .5); c.fillStyle = 'rgba(255,210,140,.95)'; c.fillRect(px + W * .08, wy - H * .07, W * .14, H * .14); }
    }
  };

  /* 굴뚝 연기 한 줄기 */
  const smoke = (c, S, o) => {
    const px = S.px(o.x, o.z), gy = (o.y != null ? o.y : S.ground(px, o.z)); if (gy < 0) return;
    const H = S.ph(o.h || 6, o.z), top = gy - S.ph(o.rise || 30, o.z); const fg = S.fogAt(o.z, px);
    const col = aces(mix(mix(S.CH, [1, 1, 1], .4), fg.col, fg.f).map((v) => v * S.exp));
    for (let i = 0; i < 18; i++) { const k = i / 17, y = gy - H - (gy - H - top) * k, x = px + Math.sin(k * 5 + (o.seed || 0)) * H * .5 * k + (o.drift || .6) * (gy - y) * .25, r = H * (.08 + k * .5); S.glow(c, x, y, r, col, .09 * (1 - k * .8)); }
  };

  /* 길: 세계 좌표 점들을 땅 위로 투영해서 밝은 띠로 */
  const road = (c, S, o) => {
    const pts = [];
    for (const [x, z] of o.pts) { const px = S.px(x, z), gy = S.ground(px, z); if (gy >= 0) pts.push([px, gy, z]); }
    if (pts.length < 2) return;
    const al = lin(o.color || '#8a7a58');
    for (let i = 0; i < pts.length - 1; i++) {
      const [x0, y0, z0] = pts[i], [x1, y1, z1] = pts[i + 1], w0 = S.ph(o.w || 2.2, z0), w1 = S.ph(o.w || 2.2, z1);
      c.fillStyle = S.shade(S.lit(al, .8), (z0 + z1) / 2, (x0 + x1) / 2, .7);
      c.beginPath(); c.moveTo(x0 - w0 / 2, y0); c.lineTo(x1 - w1 / 2, y1); c.lineTo(x1 + w1 / 2, y1); c.lineTo(x0 + w0 / 2, y0); c.closePath(); c.fill();
    }
  };

  /* 점만 한 사람 (뒷모습). 크기 단서 */
  const figure = (c, S, o) => {
    const px = S.px(o.x, o.z), gy = S.ground(px, o.z); if (gy < 0) return;
    const H = S.ph(o.h || 1.7, o.z), col = S.shade(lin(o.color || '#17141c').map((v) => v * .6), o.z, px);
    c.fillStyle = col; c.beginPath(); c.moveTo(px - H * .14, gy); c.lineTo(px - H * .1, gy - H * .72); c.quadraticCurveTo(px, gy - H * .86, px + H * .1, gy - H * .72); c.lineTo(px + H * .14, gy); c.closePath(); c.fill();
    c.beginPath(); c.arc(px, gy - H * .9, H * .1, 0, 6.29); c.fill();
    c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(px, gy, H * .22, H * .05, 0, 0, 6.29); c.fill();
  };

  /* 회랑: 기둥 줄이 멀어진다 (카라드) */
  const colonnade = (c, S, o) => {
    const n = o.n || 14, al = lin(o.color || '#cfc6b4'), [fl, fr] = faces(S);
    for (let i = n - 1; i >= 0; i--) {
      const z = o.z0 + i * (o.step || 9), x = o.x + (o.dx || 0) * i, px = S.px(x, z), gy = S.ground(px, z); if (gy < 0) continue;
      const H = S.ph(o.h || 9, z), W = S.ph(o.w || 1.3, z);
      c.fillStyle = S.shade(S.lit(al, fl), z, px); c.fillRect(px - W / 2, gy - H, W / 2, H);
      c.fillStyle = S.shade(S.lit(al, fr), z, px); c.fillRect(px, gy - H, W / 2, H);
      c.fillStyle = S.shade(S.lit(al, .95), z, px); c.fillRect(px - W * .8, gy - H - W * .5, W * 1.6, W * .5);
      c.fillStyle = S.shade(S.lit(al, .3), z, px); c.fillRect(px - W * .55, gy - W * .25, W * 1.1, W * .25);
      /* 짧은 그림자 (해가 머리 위) */
      c.fillStyle = 'rgba(0,0,0,.28)'; c.beginPath(); c.ellipse(px + W * .2, gy + W * .1, W * .9, W * .18, 0, 0, 6.29); c.fill();
    }
    /* 기둥 위 보: 기둥 사이마다 */
    for (let i = 0; i < n - 1; i++) {
      const za = o.z0 + i * (o.step || 9), zb = za + (o.step || 9), pa = S.px(o.x + (o.dx || 0) * i, za), pb = S.px(o.x + (o.dx || 0) * (i + 1), zb), ga = S.ground(pa, za), gb = S.ground(pb, zb); if (ga < 0 || gb < 0) continue;
      const Ha = S.ph(o.h || 9, za), Hb = S.ph(o.h || 9, zb), Wa = S.ph(o.w || 1.3, za), Wb = S.ph(o.w || 1.3, zb);
      c.fillStyle = S.shade(S.lit(al, .85), (za + zb) / 2, (pa + pb) / 2); c.beginPath(); c.moveTo(pa - Wa * .9, ga - Ha - Wa * .5); c.lineTo(pb - Wb * .9, gb - Hb - Wb * .5); c.lineTo(pb + Wb * .9, gb - Hb - Wb * .95); c.lineTo(pa + Wa * .9, ga - Ha - Wa * .95); c.closePath(); c.fill();
    }
  };

  /* 수로: 땅 위 가는 물줄기 (하늘색 반사) */
  const channel = (c, S, o) => { road(c, S, Object.assign({}, o, { color: o.color || '#9fc4e0', w: o.w || 1.2 })); };

  /* 항구: 돔 하나, 돛대 몇, 배 한 척, 불빛 */
  const harbor = (c, S, o) => {
    const z = o.z, px = S.px(o.x, z); let gy = S.ground(px, z); if (gy < 0) gy = o.y || S.h * .6;
    const H = S.ph(o.h || 16, z), al = lin(o.color || '#6b4a44');
    const dark = S.shade(S.lit(al, .2), z, px);
    /* 도시 덩어리 (낮은 건물 띠) */
    const W = S.ph(o.w || 60, z); c.fillStyle = dark; c.fillRect(px - W / 2, gy - H * .32, W, H * .32);
    for (let i = 0; i < 9; i++) { const bx = px - W / 2 + W * (i + .5) / 9, bh = H * (.35 + (i * 7 % 5) * .08), bw = W / 9 * .8; c.fillRect(bx - bw / 2, gy - bh, bw, bh); }
    /* 돔 */
    c.beginPath(); c.moveTo(px - H * .3, gy - H * .5); c.lineTo(px - H * .3, gy - H * .62); c.arc(px, gy - H * .62, H * .3, Math.PI, 0); c.lineTo(px + H * .3, gy - H * .5); c.closePath(); c.fill();
    c.fillRect(px - H * .02, gy - H * 1.02, H * .04, H * .12);
    /* 돛대 */
    c.strokeStyle = dark; c.lineWidth = Math.max(1, H * .012); for (let i = 0; i < 5; i++) { const mx = px + W * (-.42 + i * .19 + Math.sin(i) * .03); c.beginPath(); c.moveTo(mx, gy); c.lineTo(mx, gy - H * (.45 + (i % 2) * .15)); c.stroke(); }
    /* 불빛 */
    for (let i = 0; i < 6; i++) { const lx = px - W / 2 + W * (i + .5) / 6 + Math.sin(i * 2.1) * W * .04, ly = gy - H * .12 - (i % 3) * H * .08; S.glow(c, lx, ly, H * .09, [1, .72, .35], .7); c.fillStyle = 'rgba(255,220,160,.95)'; c.fillRect(lx - 1, ly - 1, 2, 2); }
  };
  const boat = (c, S, o) => {
    const z = o.z, px = S.px(o.x, z); let gy = S.ground(px, z); if (gy < 0) return;
    const H = S.ph(o.h || 5, z), col = S.shade([.004, .003, .004], z, px);
    c.fillStyle = col; c.beginPath(); c.moveTo(px - H * .6, gy - H * .12); c.quadraticCurveTo(px, gy + H * .1, px + H * .6, gy - H * .12); c.lineTo(px + H * .5, gy); c.lineTo(px - H * .5, gy); c.closePath(); c.fill();
    c.fillRect(px - H * .02, gy - H, H * .04, H * .9);
    c.beginPath(); c.moveTo(px + H * .02, gy - H * .95); c.lineTo(px + H * .45, gy - H * .3); c.lineTo(px + H * .02, gy - H * .3); c.closePath(); c.fill();
    /* 물에 비친 어두운 자국 */
    c.fillStyle = 'rgba(20,8,6,.35)'; c.fillRect(px - H * .5, gy, H, H * .3);
  };

  /* 숲: 거리별 나무 실루엣 띠 (무레) */
  const forest = (c, S, o) => {
    const bands = o.bands || [[320, .9], [200, 1.1], [120, 1.3]], al = lin(o.color || '#132a2e');
    const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5; return x - Math.floor(x); };
    bands.forEach(([z, hk], bi) => {
      const nb = bands.length, dk = .9 - .7 * (bi / Math.max(1, nb - 1)); const col = S.shade(S.lit(al.map((v) => v * dk), .25), z, S.w / 2); c.fillStyle = col;
      const base0 = S.ph(2.6, z), th = S.ph((o.h || 9) * hk, z);
      let px = -base0 * 2, k = bi * 1000;
      c.beginPath(); c.moveTo(-10, S.h); let last = -1;
      while (px < S.w + base0 * 2) {
        const r1 = rnd(k++), r2 = rnd(k++), r3 = rnd(k++);
        const gy0 = S.ground(Math.max(0, Math.min(S.w - 1, px)), z); const base = gy0 >= 0 ? gy0 : last; if (base < 0) { px += base0; continue; } last = base;
        const slow = .55 + .45 * Math.sin(px * .006 + bi * 2.1 + z * .01);
        const h = th * (.5 + r1 * .7) * slow, w = base0 * (.6 + r2 * .8);
        c.lineTo(px - w, base + 2); c.lineTo(px - w * .55, base - h * .45); c.lineTo(px - w * .25, base - h * .78); c.lineTo(px, base - h); c.lineTo(px + w * .25, base - h * .78); c.lineTo(px + w * .55, base - h * .45); c.lineTo(px + w, base + 2);
        px += w * (.9 + r3 * .9);
      }
      c.lineTo(S.w + 10, S.h); c.closePath(); c.fill();
    });
  };
  /* 첨탑 하나 + 창 하나 (무레) */
  const spire = (c, S, o) => {
    const z = o.z, px = S.px(o.x, z), gy = S.ground(px, z); if (gy < 0) return;
    const H = S.ph(o.h || 42, z), W = H * .16, col = S.shade(S.lit(lin(o.color || '#1b2630'), .3), z, px);
    c.fillStyle = col;
    c.fillRect(px - W / 2, gy - H * .62, W, H * .62);
    c.beginPath(); c.moveTo(px - W * .55, gy - H * .6); c.lineTo(px, gy - H); c.lineTo(px + W * .55, gy - H * .6); c.closePath(); c.fill();
    c.fillRect(px - W * 1.6, gy - H * .32, W * 3.2, H * .32);
    c.beginPath(); c.moveTo(px - W * 1.7, gy - H * .3); c.lineTo(px - W * .5, gy - H * .42); c.lineTo(px + W * 1.7, gy - H * .3); c.closePath(); c.fill();
    /* 창 하나 */
    const wy = gy - H * .5; S.glow(c, px, wy, H * .1, [1, .7, .38], .85); c.fillStyle = 'rgba(255,214,150,1)'; c.fillRect(px - W * .1, wy - W * .18, W * .2, W * .36);
  };

  /* 굴뚝 도시 + 등불 줄 (도른) */
  const chimneys = (c, S, o) => {
    const z = o.z, n = o.n || 7, al = lin(o.color || '#0f1420');
    for (let i = 0; i < n; i++) {
      const x = o.x + (i - (n - 1) / 2) * (o.gap || 12) + Math.sin(i * 4.1) * 3, zz = z + Math.cos(i * 2.3) * 14, px = S.px(x, zz), gy = S.ground(px, zz); if (gy < 0) continue;
      const H = S.ph((o.h || 26) * (i === Math.floor(n / 2) ? 1.5 : .7 + (i % 3) * .2), zz), W = S.ph(3, zz), col = S.shade(S.lit(al, .25), zz, px);
      c.fillStyle = col; c.fillRect(px - W / 2, gy - H, W, H); c.fillRect(px - W * 2.2, gy - H * .3, W * 4.4, H * .3);
      smoke(c, S, { x, z: zz, y: gy - H, h: 3, rise: 40 + i * 5, seed: i, drift: .9 });
    }
  };
  const lamps = (c, S, o) => {
    const pts = o.pts; /* [[x,z],...] 길 따라 */
    pts.forEach(([x, z], i) => { const px = S.px(x, z), gy = S.ground(px, z); if (gy < 0) return; const H = S.ph(o.h || 4, z); c.fillStyle = S.shade([.02, .02, .03], z, px); c.fillRect(px - H * .03, gy - H, H * .06, H); S.glow(c, px, gy - H, H * (o.r || 1.6), [1, .62, .25], .8); c.fillStyle = 'rgba(255,225,180,1)'; c.beginPath(); c.arc(px, gy - H, Math.max(1, H * .09), 0, 6.29); c.fill(); });
  };

  /* 거대한 탑 (메르한): 해 바로 아래, 좌우 대칭 */
  const tower = (c, S, o) => {
    const z = o.z, px = S.px(o.x, z), gy = S.ground(px, z); if (gy < 0) return;
    const H = S.ph(o.h || 120, z), al = lin(o.color || '#b9b2a2');
    const top = S.shade(S.lit(al, .9), z, px), side = S.shade(S.lit(al, .32), z, px), gold = S.shade(S.lit(lin('#c8a860'), .9), z, px);
    const tiers = 5;
    for (let i = 0; i < tiers; i++) { const k = i / tiers, w = H * (.42 - k * .3), y0 = gy - H * k, y1 = gy - H * (k + 1 / tiers) ; c.fillStyle = side; c.fillRect(px - w / 2, y1, w, y0 - y1); c.fillStyle = top; c.fillRect(px - w / 2 - H * .02, y1 - H * .012, w + H * .04, H * .012); }
    c.fillStyle = gold; c.beginPath(); c.moveTo(px - H * .06, gy - H); c.lineTo(px, gy - H * 1.14); c.lineTo(px + H * .06, gy - H); c.closePath(); c.fill();
    /* 밑의 계단 (크기 단서) */
    for (let i = 0; i < 6; i++) { const w = H * (.5 + i * .06); c.fillStyle = i % 2 ? side : top; c.fillRect(px - w / 2, gy + i * H * .006, w, H * .006); }
    /* 탑 양쪽의 낮은 대칭 건물 */
    c.fillStyle = side; [-1, 1].forEach((s) => { for (let i = 1; i <= 3; i++) { const w = H * .09, hh = H * (.22 - i * .04), x = px + s * (H * .24 + i * H * .11); c.fillRect(x - w / 2, gy - hh, w, hh); c.fillStyle = top; c.fillRect(x - w / 2, gy - hh - H * .008, w, H * .008); c.fillStyle = side; } });
  };

  /* 화면 위 가운데에서 내려오는 빛 (해가 머리 위에 있을 때) */
  const topglow = (c, S, o) => { const x = S.w * (o.x == null ? .5 : o.x); const g = c.createRadialGradient(x, -S.h * .1, 0, x, -S.h * .1, S.h * (o.r || .75)); g.addColorStop(0, 'rgba(255,250,235,' + (o.a == null ? .55 : o.a) + ')'); g.addColorStop(.5, 'rgba(255,245,220,' + (o.a == null ? .18 : o.a * .33) + ')'); g.addColorStop(1, 'rgba(255,245,220,0)'); c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = g; c.fillRect(0, 0, S.w, S.h); c.restore(); };
  /* 지평선의 아주 작은 빛 하나 (네이) */
  const lonelight = (c, S, o) => { const px = S.px(o.x, o.z), gy = S.ground(px, o.z); if (gy < 0) return; S.glow(c, px, gy - 2, S.h * (o.r || .03), o.col || [.6, .75, 1], .5); c.fillStyle = 'rgba(220,235,255,1)'; c.fillRect(px - 1, gy - 3, 2, 2); };

  return { Scene, topglow, windmill, houses, smoke, road, figure, colonnade, channel, harbor, boat, forest, spire, chimneys, lamps, tower, lonelight };
})();
