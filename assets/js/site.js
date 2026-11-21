{
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
const $ = (s) => document.querySelector(s);
const DPR = () => Math.min(devicePixelRatio || 1, 1.5);

/* 화질: 기억해 둔 값, 없으면 화면에 맞춰 */
let Q = 'mid';
try { Q = localStorage.getItem('tal-q') || ''; } catch (e) { Q = ''; }
if (!Q || Q === 'high') {
  const g = TalEngine.gpuName().toLowerCase();
  const weak = /intel|iris|uhd|hd graphics|mali|adreno|powervr|apple gpu|swiftshader|llvmpipe|microsoft basic/.test(g);
  if (!Q) Q = weak ? 'low' : 'mid';
}

/* 장면 */
const S = (o) => o;
const HERO = { ty: 8, el: 3.0, az: 20, top: '#060a1e', hor: '#c8603c', sun: '#ffc490', si: 2.9, g1: '#4a4650', g2: '#0d0b12', fog: .0009, cld: 0, str: 1, exp: 1.05, camy: 24, pit: .3, seed: 8.8, ssz: .026 };
const LANDS0 = [
  { n: '아르하', en: 'Arha', h: '아침', m: '다시 오는 것', d: '부드러운 아침빛이 오래 머무는 땅. 초원과 언덕 사이로 작은 도시와 농장, 풍차가 이어진다. 공동체의 신뢰를 중요하게 여기며, 방랑자가 탈미라를 처음 알아가는 곳이다.',
    p: S({ ty: 0, el: 9, az: -32, top: '#244a82', hor: '#f2c894', sun: '#ffd9a4', si: 3.4, g1: '#8fb04c', g2: '#3d5a2c', fog: .0018, cld: .45, exp: 1.0, camy: 5, pit: .2, seed: 1.3, ssz: .03 }) },
  { n: '카라드', en: 'Karad', h: '정오', m: '그림자 없는 곳', d: '해가 높이 떠 그림자가 짧은 땅. 흰 돌로 지은 도시와 수로, 거대한 기록 보관소가 있다. 법과 증언, 기록을 중시하며 진실을 밝히는 일을 미덕으로 여긴다.',
    p: S({ ty: 1, el: 62, az: 25, top: '#2b62ad', hor: '#c5d7e6', sun: '#fff0d6', si: 3, g1: '#e8cf9c', g2: '#a8794a', fog: .0018, cld: .18, exp: .8, camy: 7, pit: .18, seed: 2.1 }) },
  { n: '세이라', en: 'Seira', h: '노을', m: '남는 빛', d: '노을이 지지 않는 바닷가. 운하와 항구를 따라 무역과 예술이 발달했다. 지난 사건과 인물을 기념하는 문화가 깊다.',
    p: S({ ty: 2, el: 1.2, az: 6, top: '#1d1736', hor: '#f07a46', sun: '#ffa860', si: 4, g1: '#4a2836', g2: '#22121f', fog: .0032, cld: .6, exp: 1.0, camy: 9, pit: .22, seed: 3.7, ssz: .035 }) },
  { n: '무레', en: 'Mure', h: '황혼', m: '사이', d: '푸른 황혼이 숲과 첨탑에 내려앉는 땅. 학자와 기록관, 장례를 맡는 이들이 중요한 지위를 가진다. 삶과 죽음의 경계를 존중하는 문화가 있다.',
    p: S({ ty: 3, el: -4, az: -25, top: '#060d22', hor: '#3d5e8c', sun: '#8fb0e8', si: 1.3, g1: '#20374a', g2: '#0b1620', fog: .014, cld: .3, str: .4, exp: 1.1, camy: 7, pit: .2, seed: 4.4 }) },
  { n: '도른', en: 'Dorn', h: '새벽', m: '등지고 선 땅', d: '해가 뜨지 않는 추운 땅. 철골과 증기, 등불의 불빛으로 이루어진 산업 도시가 긴 밤을 견딘다. 온기상회가 처음 생긴 곳으로, 따뜻한 공간 하나의 값이 다른 땅과 전혀 다르다.', lamps: true,
    p: S({ ty: 4, el: -20, az: 0, top: '#02040a', hor: '#0c172b', sun: '#4a68a0', si: .6, g1: '#b4c3dc', g2: '#4a5874', fog: .0035, cld: .1, str: .8, exp: 2.0, camy: 4, pit: .2, seed: 5.9 }) },
  { n: '메르한', en: 'Merhan', h: '한낮', m: '해 아래', d: '해가 바로 머리 위에 있는 땅. 빛을 다루는 기술이 가장 발달했고, 완성된 질서를 지키는 일을 무엇보다 중요하게 여긴다.',
    p: S({ ty: 5, el: 74, az: 35, top: '#5f95d2', hor: '#eaf0f4', sun: '#fffaf0', si: 3.2, g1: '#f3ead6', g2: '#a88f66', fog: .0014, cld: .12, exp: .7, camy: 6, pit: .14, seed: 6.2 }) },
  { n: '네이', en: 'Nei', h: '자정', m: '끝이자 처음', d: '가장 깊은 밤에 속한 땅. 다른 여섯 땅과 근본적으로 다른 곳이라고 전해진다.', night: true,
    p: S({ ty: 6, el: -45, az: 0, top: '#000002', hor: '#0c1226', sun: '#0d1630', si: .3, g1: '#0a0b12', g2: '#030308', fog: .0016, cld: 0, str: 1, exp: 2.2, camy: 3, pit: .2, seed: 7.5 }) }
];
/* 해에서 가까운 순서: 한낮, 정오, 아침, 노을, 황혼, 새벽, 자정 */
const LANDS = [5, 1, 0, 2, 3, 4, 6].map((i) => LANDS0[i]);
const tall = (p, o) => Object.assign({}, p, { pit: .3 }, o || {});
const HOURS = [['한낮', '#fbf6e6'], ['정오', '#f1d89a'], ['아침', '#f2c79a'], ['노을', '#e8875a'], ['황혼', '#4f6f9e'], ['새벽', '#24314d'], ['자정', '#7fb0ff']];
const NEWS = [
  ['note', '알림', '공식 홈페이지 오픈', '26.11.22'],
  ['world', '세계', '일곱 땅 소개', '26.11.22'],
  ['world', '세계', '정보 추가: 떨어지는 별, 멈춤, 밀린 시간', '26.11.22'],
  ['world', '조직', '조직 소개: 방랑자, 일곱 수호자, 이음회, 미라세', '26.11.22'],
  ['dev', '개발', '오프닝 영상 제작 중', '26.11.21'],
  ['dev', '개발', '사용 엔진: 언리얼 엔진 5.8', '26.11.20']
];
const FTABS = [['all', '전체'], ['note', '알림'], ['world', '세계'], ['dev', '개발']];
const FACTIONS_ALL = [
  { short: '방랑자', en: 'Wanderer', name: '방랑자', sub: '방랑자와 동행', dot: '#7fb0ff',
    desc: '제 시각의 띠를 벗어나 일곱 땅을 여행하는 방랑자와 그 동행. 탈미라의 사람들은 대부분 자기 시각의 띠 안에서 평생을 보내기 때문에, 띠를 넘어 다니는 이는 드물다.',
    cards: [
      { n: '방랑자', t: '일곱 땅을 가로지르며 멈춘 시간을 다시 흐르게 하는 여행자. 여러 시각의 빛을 다룰 수 있는 드문 존재지만, 여행을 시작할 때는 힘을 대부분 잃은 상태다.', w: '무기: 한손검 「자정 속 별」', p: tall(LANDS0[6].p, { seed: 9.1 }), fx: 'ring' },
      { n: '하루', t: '방랑자의 곁에서 쫑알대며 함께 여행하는 작은 존재. 공중을 헤엄치듯 떠다니며 길 안내와 설명을 맡는다.', w: '어디서 왔는지는 알려지지 않았다.', p: tall(LANDS0[3].p, { seed: 4.9 }), fx: 'wisp' }] },
  { short: '수호자', en: 'Guardians', name: '수호자', sub: '일곱 시각의 해를 붙잡은 이들', dot: '#f0dcae',
    desc: '일곱 시각의 해를 붙잡고 있는 존재들. 시각마다 한 명씩, 모두 일곱이다. 각자의 땅에서 신앙과 권위의 중심으로 받들어지며, 땅의 사람들에게는 오래된 질서 그 자체다. 해를 붙잡고 있는 까닭은 수호자마다 다르다.',
    cards: [
      { n: '한낮의 수호자', t: '메르한의 해를 붙잡고 있는 수호자. 일곱 시각 가운데 가장 높은 해를 맡고 있다. 빛과 질서가 정점에 이른 메르한에서 받들어진다.', w: '한낮 · 메르한', p: tall(LANDS0[5].p, { seed: 6.8 }) },
      { n: '정오의 수호자', t: '카라드의 해를 붙잡고 있는 수호자. 흰 석조 도시와 법정, 기록 보관소가 늘어선 카라드에서 질서와 진실의 상징으로 받들어진다.', w: '정오 · 카라드', p: tall(LANDS0[1].p, { seed: 2.7 }) },
      { n: '아침의 수호자', t: '아르하의 해를 붙잡고 있는 수호자. 초원과 풍차가 이어지는 아르하의 마을들에게 신앙과 권위의 중심이다.', w: '아침 · 아르하', p: tall(LANDS0[0].p, { seed: 1.9 }) },
      { n: '노을의 수호자', t: '세이라의 해를 붙잡고 있는 수호자. 끝나지 않는 노을이 바다를 물들이는 항구 도시들에서 섬겨진다. 세이라 사람들은 예술과 기억을 소중히 여긴다.', w: '노을 · 세이라', p: tall(LANDS0[2].p, { seed: 3.6 }) },
      { n: '황혼의 수호자', t: '무레의 해를 붙잡고 있는 수호자. 푸른 황혼이 숲과 첨탑에 내려앉는 땅에서, 삶과 죽음의 경계를 존중하는 무레의 문화 한가운데에 있다.', w: '황혼 · 무레', p: tall(LANDS0[3].p, { seed: 5.1 }) },
      { n: '새벽의 수호자', t: '도른의 해를 붙잡고 있는 수호자. 해 없는 추위가 이어지는 도른에서, 등불의 온기로 버티는 도시들 위에 있다.', w: '새벽 · 도른', p: tall(LANDS0[4].p, { seed: 4.4 }) },
      { n: '자정의 수호자', t: '가장 깊은 밤의 시각, 네이의 해를 맡는 수호자. 그에 대해 알려진 것은 거의 없다.', w: '자정 · 네이', p: tall(LANDS0[6].p, { seed: 7.3 }) }] },
  { short: '이음회', en: 'The Bond', name: '이음회', sub: '사람들의 공동체', dot: '#e6c27a',
    desc: '특정한 신을 따르기보다, 탈미라에서 살아가는 사람들의 내일을 지키는 일을 먼저 생각하는 공동체. 땅과 시각을 가리지 않고 어려운 사람을 돕는다.',
    cards: [
      { n: '수천 년의 손길', t: '멈춘 해 아래에서 수천 년 동안, 사람들이 서로 도우며 조금씩 만들어 온 모임이다. 누군가를 이기려고 모인 것이 아니라, 사람을 돕겠다는 마음으로 이어져 왔다.', w: '', p: tall(LANDS0[2].p, { seed: 8.8, exp: 1.2 }), fx: 'lamps' }] },
  { short: '미라세', en: 'Mirase', name: '미라세', sub: '온기상회', dot: '#ffb466',
    desc: '밤쪽에서 시작해 탈미라 전역으로 진출한 거대 상업 조직. 사람들은 흔히 온기상회라고 부른다. 어두운 지역의 사람들은 미라세가 공급하는 등불과 물자에 생활을 의존한다.',
    cards: [
      { n: '상회장', t: '미라세를 이끄는 최고 지도자. 조직의 규모와 목표를 통제하며, 일곱 시각에 대응하는 일곱 간부를 거느린다.', w: '', p: tall(LANDS0[4].p, { seed: 5.2 }), fx: 'lamps' },
      { n: '일곱 간부', t: '미라세의 핵심 권력자 일곱 명. 일곱 시각에 대응하는 자리를 하나씩 맡아, 각 지역과 미라세의 사업에 저마다 다른 이해관계를 갖는다.', w: '', p: tall(LANDS0[1].p, { seed: 6.1, exp: .9 }), fx: 'lamps' },
      { n: '온기 등불', t: '긴 밤을 견딜 열을 만들어 내는 특수한 등불. 미라세가 생산과 공급을 장악하고 있으며, 등불 하나에 공동체의 존속이 달린 마을도 있다.', w: '작동 원리는 공개되지 않았다.', p: tall(LANDS0[4].p, { seed: 3.3, exp: 1.6 }), fx: 'lamp' }] }
];
const PEOPLE = FACTIONS_ALL.filter((f) => ['방랑자', '수호자'].includes(f.short));
const ORGS = FACTIONS_ALL.filter((f) => ['이음회', '미라세'].includes(f.short));
const LORE = [
  { t: '멈춘 해', en: 'The Still Sun', c: '세계', d: '탈미라는 하늘의 해가 움직이지 않는 둥근 세계다. 먼 옛날 해가 멈춘 뒤로 빛과 시각은 제자리에 고정되었고, 그 뒤의 역사는 멈춘 해 아래에서 이어졌다. 해의 높이가 땅마다 달라서 어떤 땅은 늘 아침이고 어떤 땅은 늘 밤이다. 사람들은 움직이지 않는 해를 세상의 당연한 질서로 받아들이며 살아간다.', w: '사람들은 해가 멈춘 날을 「멈추던 날」이라 부른다.', p: tall(HERO, { pit: .34, seed: 2.6 }) },
  { t: '일곱 시각', en: 'Seven Hours', c: '세계', d: '탈미라의 빛은 한낮, 정오, 아침, 노을, 황혼, 새벽, 자정의 일곱 갈래로 나뉜다. 해의 높이가 같은 지점들은 세계를 한 바퀴 두르는 띠를 이루고, 띠마다 하나의 시각과 하나의 땅이 있다. 밝은 쪽의 땅은 빛을 당연히 여기지만, 어두운 쪽의 땅에서는 작은 온기조차 귀중한 자원이다. 시각마다 빛의 색과 성질이 달라 문명과 싸우는 방식에도 영향을 준다.', w: '', p: tall(LANDS0[2].p) },
  { t: '떨어지는 별', en: 'Falling Stars', c: '세계', d: '탈미라의 하늘에서는 별이 하나씩 떨어지고 있다. 많은 사람은 이를 길조로 받아들여, 별이 떨어지는 날이면 땅마다 축제를 연다.', w: '별이 왜 떨어지는지 정확히 아는 사람은 드물다.', p: tall(LANDS0[6].p, { seed: 8.2 }), fx: 'falls' },
  { t: '수호자', en: 'Guardians', c: '사람', d: '수호자는 일곱 시각의 해를 붙잡고 있는 존재들이다. 각 수호자는 자신의 시각에 속한 땅에서 신앙과 권위의 중심으로 받들어진다. 땅의 사람들에게 수호자는 해를 지키는 이이자 오래된 질서 그 자체다.', w: '해를 붙잡고 있는 이유는 수호자마다 다르다.', p: tall(LANDS0[5].p, { seed: 7.7 }) },
  { t: '멈춤', en: 'Stillness', c: '법칙', d: '멈춤은 시간과 함께 존재하는 또 하나의 근본 원리다. 흐르는 것을 실제로 정지시킬 수 있지만, 그 정지를 영원히 유지하지는 못한다. 이 원리는 해가 멈춘 날보다 훨씬 오래전부터 세계에 있었다.', w: '', p: tall(LANDS0[4].p, { seed: 2.2 }) },
  { t: '미끄러짐', en: 'The Slip', c: '법칙', d: '오래 지속된 멈춤이 조금씩 약해지면서, 정지해 있던 사물과 현상에 변화가 되돌아오는 징후가 나타나고 있다. 굳은 땅에서 풀이 돋았다는 보고가 각지에서 이어진다.', w: '', p: tall(LANDS0[0].p, { seed: 5.5 }) },
  { t: '밀린 시간', en: 'Delayed Time', c: '법칙', d: '멈춰 있던 대상이 다시 흐르기 시작하면, 그동안 쌓여 있던 변화가 한꺼번에 나타난다. 오래 멈춘 꽃이 순식간에 피었다 지거나, 굳어 있던 바위가 한 번에 풍화되어 무너지는 식이다. 회복과 붕괴는 같은 원리에서 나온 서로 다른 결과다.', w: '방랑자의 힘도 이 원리와 맞닿아 있다.', p: tall(LANDS0[3].p, { seed: 6.6 }) },
  { t: '발현자', en: 'Manifesters', c: '사람', d: '발현자는 시각판을 통해 빛의 힘을 다루는 사람이다. 발현의 단계는 3성, 4성, 5성으로 나뉜다. 시각판을 지니고도 힘이 켜지지 않은 사람이 있고, 시각판 자체가 없는 사람도 있다. 시각판이 없다고 약한 것은 아니며, 기술과 경험, 훈련으로 뛰어난 역량을 갖춘 사람도 많다.', w: '', p: tall(LANDS0[1].p, { seed: 9.4 }) },
  { t: '멈춘 지형', en: 'Frozen Terrain', c: '땅', d: '굳어 버린 폭포, 허공에 머문 바위, 더 이상 밀려오지 않는 파도 같은 지형이 곳곳에 남아 있다. 일부는 다시 움직이기도 해서 평범해 보이는 길이 갑자기 위험해질 수 있다. 멈춤이 아주 짙은 곳은 풀도 자라지 않고 돌도 삭지 않아, 오랫동안 아무 변화가 없었던 것처럼 보인다.', w: '', p: tall(HERO, { el: 14, az: -40, top: '#1a2a44', hor: '#9fb4cc', sun: '#eef3ff', si: 2.4, g1: '#5c6a7a', g2: '#262c36', cld: .5, str: 0, exp: .9, seed: 4.1 }) },
  { t: '옛 이름', en: 'The Old Name', c: '세계', d: '해가 멈추기 전, 이 세계는 지금과 다른 이름으로 불렸다고 전해진다. 그 이름은 옛 문자로만 남아 있는데, 지금 사람들은 그 문자를 읽지 못한다. 옛 문자는 유적의 비문과 오래된 문, 그리고 미라세의 간판에서도 볼 수 있다.', w: '', p: tall(LANDS0[6].p, { top: '#030208', hor: '#1a1230', seed: 3.9 }) }
];

/* 그림 캐시: 같은 장면 같은 크기는 한 번만. 브라우저에 저장해 두고 다음 방문엔 다시 안 그린다 */
const cache = new Map();
const hsh = (o) => { const t = JSON.stringify(o); let a = 2166136261; for (let i = 0; i < t.length; i++) { a ^= t.charCodeAt(i); a = Math.imul(a, 16777619); } return (a >>> 0).toString(36); };
const DB = (() => {
  let db = null;
  const open = new Promise((ok) => { try { const r = indexedDB.open('tal-pics', 1); r.onupgradeneeded = () => r.result.createObjectStore('p'); r.onsuccess = () => { db = r.result; ok(); }; r.onerror = () => ok(); } catch (e) { ok(); } });
  const get = (k) => open.then(() => new Promise((ok) => { if (!db) return ok(null); try { const q = db.transaction('p').objectStore('p').get(k); q.onsuccess = () => ok(q.result || null); q.onerror = () => ok(null); } catch (e) { ok(null); } }));
  const put = (k, cv) => { if (!db || !cv.toBlob) return; cv.toBlob((b) => { if (!b) return; try { db.transaction('p', 'readwrite').objectStore('p').put(b, k); } catch (e) {} }, 'image/webp', .92); };
  return { get, put };
})();
const fromDB = (k, w, h) => DB.get(k).then((b) => b ? createImageBitmap(b).then((bm) => { const c = document.createElement('canvas'); c.width = w; c.height = h; c.getContext('2d').drawImage(bm, 0, 0, w, h); cache.set(k, c); return c; }).catch(() => null) : null);
const size = (cv) => { const r = DPR(); const w = Math.max(2, Math.round(cv.clientWidth * r)), h = Math.max(2, Math.round(cv.clientHeight * r)); return [w, h]; };
const paint = (cv, key, params, prio, after) => {
  const [w, h] = size(cv); const k = hsh(params) + '|' + w + 'x' + h + '|' + Q;
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
  const show = () => { cv.classList.remove('wait'); if (after) after(cv); };
  const put = (img) => { const c = cv.getContext('2d'); c.drawImage(img, 0, 0, w, h); show(); };
  if (cache.has(k)) { put(cache.get(k)); return Promise.resolve(); }
  return fromDB(k, w, h).then((img) => {
    if (img) { put(img); return; }
    const off = document.createElement('canvas'); off.width = w; off.height = h;
    return TalEngine.render(cv, params, Q, { preview: true, into: off, prio, onPreview: show }).then((ok) => {
      if (!ok) return;
      cache.set(k, off); DB.put(k, off); put(off);
    });
  });
};
const getImg = (key, params, w, h, prio) => {
  const k = hsh(params) + '|' + w + 'x' + h + '|' + Q;
  if (cache.has(k)) return Promise.resolve(cache.get(k));
  return fromDB(k, w, h).then((img) => {
    if (img) return img;
    const off = document.createElement('canvas'); off.width = w; off.height = h;
    return TalEngine.render(off, params, Q, { prio }).then((ok) => { if (!ok) return null; cache.set(k, off); DB.put(k, off); return off; });
  });
};


/* 소리: 잡음 없는 사인파만. 선율 없이 바닥 화음과 종소리. 누르기 전엔 안 난다 */
const SND = (() => {
  let ac = null, out = null, master = null, on = false;
  const boot = () => {
    if (ac) return;
    ac = new (window.AudioContext || window.webkitAudioContext)();
    const comp = ac.createDynamicsCompressor(); comp.threshold.value = -18; comp.ratio.value = 3; comp.connect(ac.destination);
    out = ac.createGain(); out.gain.value = 1; out.connect(comp);
    master = ac.createGain(); master.gain.value = 0; master.connect(out);
  };
  const tap = (f, v, d) => {
    if (!on || !ac) return;
    const t = ac.currentTime + .005;
    const o = ac.createOscillator(), g = ac.createGain(), lp = ac.createBiquadFilter();
    o.type = 'sine'; o.frequency.setValueAtTime(f, t); o.frequency.exponentialRampToValueAtTime(f * .82, t + d);
    lp.type = 'lowpass'; lp.frequency.value = 1800;
    g.gain.setValueAtTime(.0001, t); g.gain.linearRampToValueAtTime(v, t + .004); g.gain.exponentialRampToValueAtTime(.0001, t + d);
    o.connect(lp); lp.connect(g); g.connect(out); o.start(t); o.stop(t + d + .05);
  };
  const toggle = () => {
    boot(); ac.resume();
    on = !on;
    if (on) tap(523.25, .1, .18);
    return on;
  };
  return { toggle, tick: () => tap(440, .07, .06), move: () => tap(349.23, .09, .1), soft: () => tap(392, .04, .05) };
})();
const sndBtn = $('#snd');
sndBtn.onclick = () => { const v = SND.toggle(); sndBtn.setAttribute('aria-pressed', String(v)); sndBtn.setAttribute('aria-label', v ? '소리 끄기' : '소리 켜기'); };
document.addEventListener('click', (e) => {
  if (e.target.closest('#snd')) return;
  if (e.target.closest('.arrow,.dot,.lc,.peek,.rail button')) SND.move();
  else if (e.target.closest('.tabs a,.ftabs button,.qual button,.btn')) SND.tick();
});
document.querySelectorAll('.card,.nlist li').forEach(() => {});
document.addEventListener('mouseover', (e) => { const c = e.target.closest('.card,.lc'); if (c && !c.dataset.h) { c.dataset.h = '1'; SND.soft(); c.addEventListener('mouseleave', () => { delete c.dataset.h; }, { once: true }); } });

/* 로딩: 해 점이 일곱 시각을 돌고, 준비되면 자정에서 멈춘다 */
const LD = (() => {
  const box = $('#intro'), dot = $('#sunDot'), name = $('#hourName'), en = $('#hourEn');
  const HN = ['한낮', '정오', '아침', '노을', '황혼', '새벽', '자정'], HE = ['MIDDAY', 'NOON', 'MORNING', 'SUNSET', 'DUSK', 'DAWN', 'MIDNIGHT'];
  const R = 150, C = 200, T0 = performance.now(), PER = 7000;
  $('#ticks').innerHTML = HN.map((_, i) => { const a = -Math.PI / 2 + i * Math.PI * 2 / 7; return '<line data-i="' + i + '" x1="' + (C + Math.cos(a) * 160) + '" y1="' + (C + Math.sin(a) * 160) + '" x2="' + (C + Math.cos(a) * 184) + '" y2="' + (C + Math.sin(a) * 184) + '" stroke="#d6be8c" stroke-width="2" opacity=".3"/>'; }).join('');
  const ticks = [...document.querySelectorAll('#ticks line')];
  let ready = false, last = -1, done = false, rT = 0, rP = 0, rEnd = 0, fin = false;
  const frame = (t) => {
    if (done) return;
    let p;
    if (!ready || !rT) {
      p = ((t - T0) % PER) / PER;
      if (ready) { rT = t; rP = p; rEnd = p <= 6 / 7 ? 6 / 7 : 1 + 6 / 7; }
    }
    if (rT) {
      const k = Math.min(1, (t - rT) / Math.max(500, (rEnd - rP) * 1600));
      const e = 1 - Math.pow(1 - k, 3);
      p = (rP + (rEnd - rP) * e) % 1; fin = k >= 1;
    }
    const a = -Math.PI / 2 + p * Math.PI * 2;
    dot.setAttribute('cx', C + Math.cos(a) * R); dot.setAttribute('cy', C + Math.sin(a) * R);
    const hi = Math.round(p * 7) % 7;
    if (hi !== last) { last = hi; name.textContent = HN[hi]; en.textContent = HE[hi]; }
    ticks.forEach((l, i) => { const d = Math.abs(((p * 7 - i + 10.5) % 7) - 3.5); l.setAttribute('opacity', (.3 + .7 * Math.max(0, 1 - d)).toFixed(2)); });
    if (fin) {
      done = true; box.classList.add('stop'); dot.setAttribute('fill', '#7fb0ff'); ticks[6].setAttribute('stroke', '#7fb0ff'); ticks[6].setAttribute('opacity', '1');
      setTimeout(() => box.classList.add('done'), 900); return;
    }
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
  return { finish: () => { ready = true; if (RM) box.classList.add('done'); } };
})();
setTimeout(() => LD.finish(), 25000);

/* 메인 */
$('#hours').innerHTML = HOURS.map((h) => '<li><i style="background:' + h[1] + '"></i>' + h[0] + '</li>').join('');
const heroPic = $('#heroPic'), heroFx = $('#heroFx'), ring = $('#ring');
let horizonY = .7;
const placeRing = () => {
  const w = heroPic.clientWidth, h = heroPic.clientHeight, s = TalEngine.sunScreen(HERO, w, h);
  horizonY = (1 + HERO.pit) / 2 * .98;
  if (s) { ring.style.left = (s.x * 100) + '%'; ring.style.top = (s.y * 100) + '%'; }
};
/* 메인 그림 마무리: 해에서 퍼지는 빛줄기와 번짐. 그림 위에 한 번만 얹는다 */
const heroPost = (cv) => {
  const w = cv.width, h = cv.height, c = cv.getContext('2d');
  if (!('filter' in c)) return;
  const s = TalEngine.sunScreen(HERO, w, h); if (!s) return;
  const sw = Math.max(2, w >> 2), sh = Math.max(2, h >> 2);
  const a = document.createElement('canvas'); a.width = sw; a.height = sh; const ac = a.getContext('2d');
  ac.filter = 'brightness(.75) contrast(3.2) saturate(1.3)'; ac.drawImage(cv, 0, 0, sw, sh); ac.filter = 'none';
  const r = document.createElement('canvas'); r.width = sw; r.height = sh; const rc = r.getContext('2d');
  rc.globalCompositeOperation = 'lighter';
  const cx = s.x * sw, cy = s.y * sh, N = 28;
  for (let i = 0; i < N; i++) { const k = 1 + i * .045; rc.globalAlpha = (1 - i / N) * .07; rc.setTransform(k, 0, 0, k, cx * (1 - k), cy * (1 - k)); rc.drawImage(a, 0, 0); }
  rc.setTransform(1, 0, 0, 1, 0, 0);
  c.save(); c.imageSmoothingQuality = 'high';
  c.globalCompositeOperation = 'screen'; c.globalAlpha = .42; c.drawImage(r, 0, 0, w, h);
  c.filter = 'blur(' + Math.round(w / 90) + 'px)'; c.globalAlpha = .26; c.drawImage(a, 0, 0, w, h);
  c.restore();
};
const paintHero = () => { placeRing(); return paint(heroPic, 'hero', HERO, 10, (cv) => { ring.style.opacity = .4; heroPost(cv); }); };

/* 탭 따라가기, 나타나기 */
const tabs = [...document.querySelectorAll('.tabs a')], arc = $('#arc');
const setTab = (id) => {
  tabs.forEach((a) => a.classList.toggle('on', a.dataset.s === id));
  const a = tabs.find((t) => t.dataset.s === id);
  if (a) arc.style.transform = 'translateX(' + (a.offsetLeft + a.offsetWidth / 2 - 32) + 'px)';
};
const secObs = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting && !document.documentElement.classList.contains('fp')) setTab(e.target.id); }), { rootMargin: '-45% 0px -50% 0px' });
document.querySelectorAll('main > section').forEach((s) => secObs.observe(s));
setTab('main');
const revObs = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); revObs.unobserve(e.target); } }), { threshold: .12 });
document.querySelectorAll('.reveal').forEach((r) => revObs.observe(r));

/* 움직이는 것: 반짝임, 떨어지는 별, 등불 */
const glints = (n, top, bot) => Array.from({ length: n }, () => ({ x: Math.random(), y: top + Math.random() * (bot - top), p: Math.random() * 6.28, s: .6 + Math.random() * 1.4 }));
const fxCtx = (cv) => { const [w, h] = size(cv); if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; } const c = cv.getContext('2d'); c.setTransform(1, 0, 0, 1, 0, 0); return [c, w, h]; };
const meteorField = () => ({ list: [], next: 0 });
const runMeteors = (c, w, h, f, t, maxY) => {
  if (!RM && t > f.next && f.list.length < 2) {
    f.next = t + 2200 + Math.random() * 3800;
    const sp = (4 + Math.random() * 3) * DPR();
    f.list.push({ x: w * (.3 + Math.random() * .7), y: Math.random() * h * maxY * .5, vx: -sp * .45, vy: sp * .9, life: 0, max: 60 + Math.random() * 50, len: (80 + Math.random() * 90) * DPR() });
  }
  f.list = f.list.filter((m) => m.life < m.max && m.y < h * maxY);
  for (const m of f.list) {
    m.x += m.vx; m.y += m.vy; m.life++;
    const k = m.life / m.max, a = k < .15 ? k / .15 : 1 - (k - .15) / .85;
    const n = Math.hypot(m.vx, m.vy), tx = m.x - m.vx / n * m.len, ty = m.y - m.vy / n * m.len;
    const g = c.createLinearGradient(tx, ty, m.x, m.y);
    g.addColorStop(0, 'rgba(255,250,240,0)'); g.addColorStop(1, 'rgba(255,250,240,' + (.9 * a).toFixed(3) + ')');
    c.strokeStyle = g; c.lineWidth = 1.5 * DPR(); c.beginPath(); c.moveTo(tx, ty); c.lineTo(m.x, m.y); c.stroke();
    const hg = c.createRadialGradient(m.x, m.y, 0, m.x, m.y, 6 * DPR()); hg.addColorStop(0, 'rgba(255,255,255,' + a.toFixed(3) + ')'); hg.addColorStop(1, 'rgba(255,255,255,0)');
    c.fillStyle = hg; c.fillRect(m.x - 6 * DPR(), m.y - 6 * DPR(), 12 * DPR(), 12 * DPR());
  }
};
const drawGlints = (c, w, h, list, t) => {
  for (const s of list) {
    const a = RM ? .5 : Math.max(0, Math.sin(t / 1000 * s.s + s.p)) ** 6;
    if (a < .02) continue;
    const x = s.x * w, y = s.y * h, r = 2.2 * DPR();
    c.fillStyle = 'rgba(240,244,255,' + (a * .9).toFixed(3) + ')';
    c.fillRect(x - r, y - .5, r * 2, 1); c.fillRect(x - .5, y - r, 1, r * 2);
  }
};
const LAMPS = [[.14, .78], [.19, .75], [.24, .81], [.36, .84], [.41, .8], [.5, .86], [.57, .83], [.63, .78], [.66, .86], [.74, .82], [.85, .79], [.9, .84]];
const drawLamps = (c, w, h, t, list, big) => {
  list.forEach((p, i) => {
    const a = RM ? .9 : .72 + .28 * Math.sin(t / 260 + i * 1.7) * Math.sin(t / 410 + i);
    const X = p[0] * w, Y = p[1] * h, R = (big ? 90 : 20) * DPR();
    const g = c.createRadialGradient(X, Y, 0, X, Y, R); g.addColorStop(0, 'rgba(255,176,96,' + (.6 * a).toFixed(3) + ')'); g.addColorStop(1, 'rgba(255,150,80,0)');
    c.fillStyle = g; c.fillRect(X - R, Y - R, R * 2, R * 2);
    c.fillStyle = 'rgba(255,214,150,' + a.toFixed(3) + ')'; c.beginPath(); c.arc(X, Y, (big ? 5 : 2.6) * DPR(), 0, 6.29); c.fill();
  });
};
const heroGl = glints(26, .04, .45), heroMet = meteorField();
let heroOn = true; new IntersectionObserver((es) => { if (!document.documentElement.classList.contains('fp')) heroOn = es[0].isIntersecting; }).observe(heroFx);

/* 소식 */
let ftab = 'all';
const renderNews = () => {
  $('#ftabs').innerHTML = FTABS.map((f) => '<button role="tab" data-f="' + f[0] + '" aria-selected="' + (f[0] === ftab) + '">' + f[1] + '</button>').join('');
  $('#nlist').innerHTML = NEWS.filter((n) => ftab === 'all' || n[0] === ftab).map((n, i) => '<li style="animation-delay:' + i * 60 + 'ms"><span class="tag">' + n[1] + '</span><span class="nt">' + n[2] + '</span><span class="nd">' + n[3] + '</span></li>').join('');
};
$('#ftabs').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { ftab = b.dataset.f; renderNews(); } });
renderNews();
let fi = 0; const featPic = $('#featPic');
$('#fdots').innerHTML = LANDS.map(() => '<i></i>').join('');
let featBusy = false;
const showFeat = () => {
  if (featBusy) return;
  const i = fi, L = LANDS[i], [w, h] = size(featPic);
  featBusy = true;
  getImg('feat' + i, L.p, w, h, 2).then((img) => {
    featBusy = false;
    if (!img) return;
    const swapIn = () => {
      if (featPic.width !== w || featPic.height !== h) { featPic.width = w; featPic.height = h; }
      featPic.getContext('2d').drawImage(img, 0, 0, w, h); featPic.classList.remove('wait');
      $('#featName').textContent = L.n; $('#featSub').textContent = L.h + ' · ' + L.m;
      [...$('#fdots').children].forEach((d, k) => d.classList.toggle('on', k === i));
    };
    if (RM || featPic.classList.contains('wait')) swapIn(); else { featPic.classList.add('wait'); setTimeout(swapIn, 700); }
  });
};

/* 인물 */
const swap = (el, fn) => { if (RM) { fn(); return; } el.classList.add('out'); setTimeout(() => { fn(); el.classList.remove('out'); }, 300); };
const cardFx = (kind) => (cv) => {
  const c = cv.getContext('2d'), w = cv.width, h = cv.height, r = DPR();
  if (kind === 'ring') { const R = Math.min(w, h) * .26, X = w / 2, Y = h * .36; c.strokeStyle = 'rgba(240,220,174,.55)'; c.lineWidth = r; c.beginPath(); c.arc(X, Y, R, 0, 6.29); c.stroke();
    for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + i * Math.PI * 2 / 7; c.strokeStyle = i === 6 ? '#7fb0ff' : 'rgba(240,220,174,.7)'; c.lineWidth = (i === 6 ? 2.4 : 1.4) * r; c.beginPath(); c.moveTo(X + Math.cos(a) * R, Y + Math.sin(a) * R); c.lineTo(X + Math.cos(a) * (R + 18 * r), Y + Math.sin(a) * (R + 18 * r)); c.stroke(); } }
  if (kind === 'wisp') { const X = w * .55, Y = h * .4; for (let k = 3; k >= 0; k--) { const R = (18 + k * 34) * r, g = c.createRadialGradient(X, Y, 0, X, Y, R); g.addColorStop(0, 'rgba(160,200,255,' + (.5 - k * .1) + ')'); g.addColorStop(1, 'rgba(110,160,255,0)'); c.fillStyle = g; c.fillRect(X - R, Y - R, R * 2, R * 2); } c.fillStyle = 'rgba(235,244,255,.95)'; c.beginPath(); c.arc(X, Y, 4 * r, 0, 6.29); c.fill(); }
  if (kind === 'lamps') drawLamps(c, w, h, 0, LAMPS.slice(2, 9), false);
  if (kind === 'lamp') drawLamps(c, w, h, 0, [[.5, .58]], true);
  if (kind === 'falls') [[.75, .1, 160], [.35, .2, 110], [.62, .34, 70]].forEach((m) => { const x = w * m[0], y = h * m[1], l = m[2] * r, g = c.createLinearGradient(x + l * .45, y - l * .9, x, y); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, '#fffaf0'); c.strokeStyle = g; c.lineWidth = 1.4 * r; c.beginPath(); c.moveTo(x + l * .45, y - l * .9); c.lineTo(x, y); c.stroke(); });
};
const makeGroup = (root, DATA, tag) => {
  const R = (n) => root.querySelector('[data-r="' + n + '"]');
  let gi = 0;
  const box = R('cards');
  const nav = () => {
    const n = box.children.length; R('cnav').hidden = n <= 2;
    const one = box.children[0] ? box.children[0].getBoundingClientRect().width + 18 : 1;
    R('cpos').textContent = Math.min(n, Math.round(box.scrollLeft / one) + 1) + ' / ' + n;
  };
  const render = (first) => {
    R('rail').innerHTML = DATA.map((f, i) => '<button role="tab" data-i="' + i + '" aria-selected="' + (i === gi) + '"><span class="mk" aria-hidden="true"><i style="background:' + f.dot + ';box-shadow:0 0 12px ' + f.dot + '"></i></span><span>' + f.short + '</span></button>').join('');
    const f = DATA[gi];
    R('crestDot').setAttribute('fill', f.dot);
    const fill = () => { R('pen').textContent = f.en; R('pname').textContent = f.name; R('psub').textContent = f.sub; R('pdesc').textContent = f.desc; };
    first ? fill() : swap(R('pbox'), fill);
    box.innerHTML = f.cards.map((c, i) => '<article class="card" style="animation-delay:' + (150 + i * 120) + 'ms"><canvas class="pic wait" aria-hidden="true"></canvas><div class="tx"><h3>' + c.n + '</h3><p>' + c.t + '</p>' + (c.w ? '<p class="w">' + c.w + '</p>' : '') + '</div></article>').join('');
    box.scrollLeft = 0; nav();
    requestAnimationFrame(() => [...box.querySelectorAll('canvas')].forEach((cv, i) => { const c = f.cards[i]; paint(cv, tag + gi + '-' + i, c.p, 3, c.fx ? cardFx(c.fx) : null); }));
  };
  box.addEventListener('scroll', nav, { passive: true });
  const step = (d) => { const one = box.children[0].getBoundingClientRect().width + 18; box.scrollBy({ left: d * one, behavior: 'smooth' }); };
  R('cprev').onclick = () => step(-1);
  R('cnext').onclick = () => step(1);
  R('rail').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b && +b.dataset.i !== gi) { gi = +b.dataset.i; render(false); } });
  return render;
};
const renderPeopleG = makeGroup($('#people'), PEOPLE, 'pp');
const renderOrgsG = makeGroup($('#orgs'), ORGS, 'og');
const renderPeople = (first) => { renderPeopleG(first); renderOrgsG(first); };

/* 정보 */
let li = 0; const track = $('#track');
const renderLoreCards = () => {
  const vis = [0, 1, 2].map((k) => (li + k) % LORE.length);
  track.innerHTML = vis.map((idx, k) => '<button class="lc' + (k === 0 ? ' on' : '') + '" data-i="' + idx + '" aria-label="' + LORE[idx].t + '"' + (k === 0 ? ' aria-current="true"' : '') + '><canvas class="pic wait" aria-hidden="true"></canvas><span>' + LORE[idx].t + '</span></button>').join('');
  requestAnimationFrame(() => setTimeout(() => track.querySelectorAll('.lc').forEach((b, k) => { const d = LORE[+b.dataset.i]; paint(b.querySelector('canvas'), 'lore' + b.dataset.i + (k === 0 ? 'a' : 'b'), d.p, 4 - k, d.fx ? cardFx(d.fx) : null); }), 60));
};
const renderLore = (first) => {
  const d = LORE[li];
  const fill = () => { $('#len').textContent = d.en; $('#lmeta').textContent = d.c + ' · ' + (li + 1) + ' / ' + LORE.length; $('#ltitle').textContent = d.t; $('#ldesc').textContent = d.d; $('#lfrag').textContent = d.w; };
  first ? fill() : swap($('#lbox'), fill);
  renderLoreCards();
};
const goLore = (n) => { li = (n + LORE.length) % LORE.length; renderLore(false); };
$('#lprev').onclick = () => goLore(li - 1);
$('#lnext').onclick = () => goLore(li + 1);
let px0 = null, swiped = false;
track.addEventListener('pointerdown', (e) => { px0 = e.clientX; swiped = false; });
track.addEventListener('pointerup', (e) => { if (px0 !== null && Math.abs(e.clientX - px0) > 50) { swiped = true; goLore(li + (e.clientX < px0 ? 1 : -1)); } px0 = null; });
track.addEventListener('click', (e) => { if (swiped) { swiped = false; return; } const b = e.target.closest('.lc'); if (b && +b.dataset.i !== li) goLore(+b.dataset.i); });
track.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') goLore(li + 1); if (e.key === 'ArrowLeft') goLore(li - 1); });

/* 세계 */
let wi2 = 0, from = null, fadeStart = 0, curImg = null;
const wPic = $('#wPic'), wFx = $('#wFx');
const wGl = glints(40, .03, .5), wMet = meteorField();
const loadLand = (i, prio) => { const [w, h] = size(wPic); return getImg('land' + i, LANDS[i].p, w, h, prio); };
const showLand = (i, first) => {
  const L = LANDS[i], N = LANDS[(i + 1) % LANDS.length];
  $('#scene').setAttribute('aria-label', L.n + '의 풍경');
  const fill = () => { $('#wen').textContent = L.en; $('#wname').textContent = L.n; $('#wsub').textContent = L.h + ' · ' + L.m; $('#wdesc').textContent = L.d; };
  if (first) fill(); else { swap($('#wn'), fill); swap($('#wdesc'), () => {}); }
  $('#peekname').textContent = N.n; $('#peek').setAttribute('aria-label', '다음 땅 ' + N.n);
  $('#dots').innerHTML = LANDS.map((l, k) => '<button class="dot" data-i="' + k + '" aria-label="' + l.n + '"' + (k === i ? ' aria-current="true"' : '') + '><i></i></button>').join('');
  loadLand(i, 6).then((img) => { if (!img || wi2 !== i) return; from = curImg; curImg = img; fadeStart = performance.now(); });
  paint($('#peekPic'), 'peek' + ((i + 1) % LANDS.length), Object.assign({}, N.p, { pit: .3 }), 1);
};
const goW = (n) => { wi2 = (n + LANDS.length) % LANDS.length; showLand(wi2, false); };
$('#wprev').onclick = () => goW(wi2 - 1);
$('#wnext').onclick = () => goW(wi2 + 1);
$('#peek').onclick = () => goW(wi2 + 1);
$('#dots').addEventListener('click', (e) => { const b = e.target.closest('.dot'); if (b) goW(+b.dataset.i); });
let wx0 = null;
$('#scene').addEventListener('pointerdown', (e) => { wx0 = e.clientX; });
$('#scene').addEventListener('pointerup', (e) => { if (wx0 !== null && Math.abs(e.clientX - wx0) > 50) goW(wi2 + (e.clientX < wx0 ? 1 : -1)); wx0 = null; });
let worldOn = false; new IntersectionObserver((es) => { if (!document.documentElement.classList.contains('fp')) worldOn = es[0].isIntersecting; }).observe(wPic);


/* 한 화면에 한 칸 (넓은 화면) */
const secs = [...document.querySelectorAll('main > section')];
let cur = 0, lock = 0;
const pager = document.createElement('nav'); pager.className = 'pager'; pager.setAttribute('aria-label', '칸 이동');
pager.innerHTML = secs.map((s, i) => '<button data-i="' + i + '" aria-label="' + s.getAttribute('aria-label') + '"><i></i></button>').join('');
document.body.appendChild(pager);
const fpOK = () => innerWidth >= 900 && innerHeight >= 700;
const go = (i, force) => {
  i = Math.max(0, Math.min(secs.length - 1, i));
  if (i === cur && !force) return;
  const down = i > cur;
  secs.forEach((s, k) => { s.classList.toggle('on', k === i); s.classList.toggle('up', k !== i && (k < i)); });
  cur = i; lock = performance.now();
  setTab(secs[i].id);
  heroOn = secs[i].id === 'main'; worldOn = secs[i].id === 'world';
  [...pager.children].forEach((b, k) => b.setAttribute('aria-current', String(k === i)));
  try { history.replaceState(null, '', '#' + secs[i].id); } catch (e) {}
  secs[i].querySelectorAll('.reveal').forEach((r) => r.classList.add('in'));
};
const fpOn = () => {
  const want = fpOK();
  document.documentElement.classList.toggle('fp', want);
  if (want) { const h = location.hash.slice(1), k = secs.findIndex((s) => s.id === h); go(k >= 0 ? k : cur, true); }
  else secs.forEach((s) => s.classList.remove('on', 'up'));
};
const isFp = () => document.documentElement.classList.contains('fp');
addEventListener('wheel', (e) => {
  if (!isFp()) return;
  e.preventDefault();
  if (performance.now() - lock < 1100 || Math.abs(e.deltaY) < 24) return;
  go(cur + (e.deltaY > 0 ? 1 : -1));
}, { passive: false });
addEventListener('keydown', (e) => {
  if (!isFp() || e.target.closest('input,textarea,.track')) return;
  if (['ArrowDown', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); go(cur + 1); }
  if (['ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); go(cur - 1); }
  if (e.key === 'Home') go(0); if (e.key === 'End') go(secs.length - 1);
});
let ty0 = null;
addEventListener('touchstart', (e) => { ty0 = e.touches[0].clientY; }, { passive: true });
addEventListener('touchend', (e) => { if (!isFp() || ty0 === null) return; const d = ty0 - e.changedTouches[0].clientY; if (Math.abs(d) > 60) go(cur + (d > 0 ? 1 : -1)); ty0 = null; });
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]'); const p = e.target.closest('.pager button');
  if (p) { go(+p.dataset.i); return; }
  if (a && isFp()) { const k = secs.findIndex((s) => '#' + s.id === a.getAttribute('href')); if (k >= 0) { e.preventDefault(); go(k); } }
});
fpOn();

/* 한 고리: 움직이는 것만 매 프레임 */
const loop = (t) => {
  if (heroOn) { const [c, w, h] = fxCtx(heroFx); c.clearRect(0, 0, w, h); drawGlints(c, w, h, heroGl, t); runMeteors(c, w, h, heroMet, t, horizonY - .05); }
  if (worldOn && curImg) {
    const [pw, ph] = size(wPic); if (wPic.width !== pw || wPic.height !== ph) { wPic.width = pw; wPic.height = ph; }
    const c = wPic.getContext('2d'), k = RM ? 1 : Math.min(1, (t - fadeStart) / 900);
    if (from && k < 1) { c.globalAlpha = 1; c.drawImage(from, 0, 0, pw, ph); c.globalAlpha = k; c.drawImage(curImg, 0, 0, pw, ph); c.globalAlpha = 1; }
    else if (k <= 1 && (from || !wPic.dataset.done)) { c.drawImage(curImg, 0, 0, pw, ph); if (k >= 1) { from = null; wPic.dataset.done = '1'; } }
    const [fc, fw, fh] = fxCtx(wFx); fc.clearRect(0, 0, fw, fh);
    const L = LANDS[wi2];
    if (L.lamps) drawLamps(fc, fw, fh, t, LAMPS, false);
    if (L.night || L.p.str) drawGlints(fc, fw, fh, wGl, t);
    if (L.night) runMeteors(fc, fw, fh, wMet, t, .55);
  }
  requestAnimationFrame(loop);
};
const startW = () => { wPic.dataset.done = ''; showLand(wi2, true); };

/* 화질 */
const qBtns = [...document.querySelectorAll('.qual button')];
const QN = { low: '낮음', mid: '중간', high: '높음' };
const markQ = () => { qBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.q === Q))); $('#qnow').textContent = QN[Q]; };
const qBtn = $('#qbtn'), qPop = $('#qpop');
const qOpen = (v) => { qPop.hidden = !v; qBtn.setAttribute('aria-expanded', String(v)); };
qBtn.onclick = (e) => { e.stopPropagation(); qOpen(qPop.hidden); };
document.addEventListener('click', (e) => { if (!e.target.closest('.qwrap')) qOpen(false); });
addEventListener('keydown', (e) => { if (e.key === 'Escape') qOpen(false); });
markQ();
const repaintAll = () => {
  TalEngine.clear(); cache.clear();
  paintHero(); renderPeople(true); renderLoreCards(); showFeat(); curImg = null; startW();
};
qBtns.forEach((b) => b.onclick = () => { qOpen(false); if (Q === b.dataset.q) return; Q = b.dataset.q; try { localStorage.setItem('tal-q', Q); } catch (e) {} markQ(); repaintAll(); });
let rT = 0; addEventListener('resize', () => { fpOn(); const on = tabs.find((t) => t.classList.contains('on')); if (on) setTab(on.dataset.s); clearTimeout(rT); rT = setTimeout(() => { placeRing(); paintHero(); curImg = null; startW(); }, 400); });

/* 차례: 메인 먼저, 나머지는 뒤에 */
const idle = (f) => (window.requestIdleCallback ? requestIdleCallback(f, { timeout: 1500 }) : setTimeout(f, 200));
renderNews(); renderPeople(true); renderLore(true);
paintHero().then(() => { LD.finish(); idle(() => { showFeat(); startW(); }); });
setInterval(() => { if (featBusy) return; fi = (fi + 1) % LANDS.length; showFeat(); }, 7000);
setTimeout(() => idle(() => LANDS.forEach((L, i) => { if (i !== wi2) loadLand(i, 0); })), 6000);
requestAnimationFrame(loop);
}
