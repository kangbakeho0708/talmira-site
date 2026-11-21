# 탈미라 홈페이지

빌드 도구 없이 그대로 올리는 정적 사이트다. 아무 웹 호스팅에나 이 폴더를 통째로 올리면 된다.

## 파일
- `index.html` 페이지
- `404.html` 없는 주소로 들어왔을 때
- `assets/css/site.css` 모양
- `assets/js/engine.js` 하늘 · 땅 그림 엔진 (WebGL2 셰이더). 장면을 한 번 그리고 멈춘다
- `assets/js/site.js` 내용 (소식, 인물, 정보, 일곱 땅) 과 움직임
- `assets/img/` 아이콘, 공유 이미지

## 글 고치기
문구는 전부 `assets/js/site.js` 위쪽 자료 칸 (`NEWS`, `FACTIONS`, `LORE`, `LANDS`) 과 `index.html` 에 있다.

## 올리기 (GitHub Pages)
1. GitHub 에서 공개 저장소를 하나 만든다. 이 폴더 내용을 그대로 올린다.
2. 저장소 Settings → Pages → Source 를 「GitHub Actions」 로 바꾼다.
3. 몇 분 뒤 `https://<아이디>.github.io/<저장소 이름>/` 에서 열린다. `main` 에 올릴 때마다 저절로 다시 올라간다.

## 그래픽
바닥글의 화질 (낮음 · 중간 · 높음) 로 고른다. 처음엔 그래픽 칩을 보고 내장 그래픽이면 낮음, 아니면 중간으로 시작한다. WebGL2 가 없으면 단순한 그림으로 대신한다.
