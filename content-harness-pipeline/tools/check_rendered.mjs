/* 빌드된 차시를 실제로 열어 화면을 검사한다.
 *
 * 왜 필요한가 — 이 파이프라인이 2026-09-08~09 이틀에 걸쳐 잡은 결함 12종이
 * **전부** 데이터 게이트·gyo6_content 엄격 검증·빌드를 통과한 뒤 사람 눈으로만 발견됐다.
 * `problem.md` 의 `[gates-pass-but-screen-empty]` 가 그 기록이고 8회까지 쌓였다.
 * 데이터가 유효한 것과 화면이 멀쩡한 것은 다른 문제라 데이터만 봐서는 영영 못 잡는다.
 *
 * 여기서 보는 것은 **렌더 결과에서만 드러나는 것**뿐이다. 데이터로 확정할 수 있는 것은
 * `stages/scripts/lesson_check.py` 가 이미 본다. 같은 것을 두 곳에서 보지 않는다.
 *
 *   node tools/check_rendered.mjs <gyo6_content 경로> <슬롯>/<id> [--port 3050]
 *
 * 종료 코드 1 이면 위반이 있다. `npm run serve` 가 떠 있으면 그쪽으로 열고,
 * 없으면 `dist/<슬롯>/<id>/index.html` 을 직접 연다 — 서버를 띄우는 것은 선택이다.
 */
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';

const [, , gyo6Root, lessonId, ...rest] = process.argv;
if (!gyo6Root || !lessonId) {
  console.error('사용법: node tools/check_rendered.mjs <gyo6_content 경로> <슬롯>/<id> [--port 3050]');
  process.exit(2);
}

/* playwright 는 이 레포가 아니라 gyo6_content 의 node_modules 에 있다.
   경로로 부를 때는 file:// URL 이어야 한다 — 윈도우 경로를 그대로 주면
   ERR_UNSUPPORTED_ESM_URL_SCHEME 로 죽는다. */
const localPlaywright = join(resolve(gyo6Root), 'node_modules', 'playwright', 'index.js');
const playwright = existsSync(localPlaywright)
  ? await import(pathToFileURL(localPlaywright).href)
  : await import('playwright');
// playwright 는 CJS 라 동적 import 하면 실체가 `default` 아래로 들어간다.
const chromium = playwright.chromium ?? playwright.default?.chromium;
if (!chromium) {
  console.error(`playwright 를 못 찾았다: ${localPlaywright}`);
  process.exit(2);
}
const portIndex = rest.indexOf('--port');
const port = portIndex >= 0 ? rest[portIndex + 1] : '3050';
// `verify_lesson.py` 가 위반을 담당자별로 나누려면 글이 아니라 목록이 필요하다.
const jsonIndex = rest.indexOf('--json');
const jsonPath = jsonIndex >= 0 ? rest[jsonIndex + 1] : '';

/* 서버가 떠 있으면 그쪽으로, 없으면 빌드 산출물을 file:// 로 직접 연다.
 * 예전에는 `npm run serve` 가 떠 있어야만 돌았고, 안 떴을 때 ERR_CONNECTION_REFUSED 가
 * **처리되지 않은 예외**로 터져 스택 트레이스만 남았다. 화면 검사는 파이프라인의 마지막
 * 관문이라 "서버를 안 띄웠다"는 이유로 건너뛰어지면 그 관문이 없는 것과 같다.
 * `review_lesson.py` 는 처음부터 dist 의 index.html 을 직접 열어 왔다 — 같은 방식으로 맞춘다. */
const httpUrl = `http://localhost:${port}/${lessonId}/`;
const distIndex = join(resolve(gyo6Root), 'dist', ...lessonId.split('/'), 'index.html');

/* 어디를 열지는 **브라우저를 띄우기 전에** 정한다. 실패한 항해 뒤에 다시 항해하면
   `chrome-error://chromewebdata/` 로 가는 앞 항해와 경합해 또 죽는다(실측). */
const serverUp = await fetch(httpUrl, { method: 'GET' })
  .then((response) => response.ok)
  .catch(() => false);
if (!serverUp && !existsSync(distIndex)) {
  console.error('화면을 열 수 없다. 서버도 빌드 산출물도 없다.');
  console.error(`  서버: ${httpUrl} (응답 없음)`);
  console.error(`  빌드: ${distIndex} (없음)`);
  console.error(`  먼저: cd ${resolve(gyo6Root)} && npm run build:lesson -- ${lessonId}`);
  process.exit(2);
}
const url = serverUp ? httpUrl : pathToFileURL(distIndex).href;
if (!serverUp) console.log(`서버가 없어 빌드 산출물을 직접 연다: ${distIndex}`);

/* 화면에 절대 나오면 안 되는 글자.
 * 객체를 글자 자리에 넣으면 `[object Object]`, 파일을 잘못된 인코딩으로 읽으면 `???`,
 * 스토리보드 표기를 그대로 옮기면 `[시작하기]` 가 그대로 찍힌다. 셋 다 실제로 있었다. */
const FORBIDDEN = [
  { re: /\[object Object\]/, kind: 'object_in_text', why: '문자열 자리에 객체가 들어갔다' },
  { re: /\?{2,}/, kind: 'mojibake', why: '한글이 코드페이지에서 깨졌다' },
  { re: /[�]/, kind: 'mojibake', why: '복원 불가 문자(U+FFFD)가 있다' },
  { re: /원자 미구현|미구현 원자/, kind: 'atom_placeholder', why: '어휘 밖의 원자라 자리표시자가 떴다' },
];

/* 차시가 `#app.<상태>` 로 쓴 CSS 를 모은다. 그 상태가 화면을 도는 동안 한 번도
   안 붙으면 그 규칙은 전부 죽은 것이다 — 실측(2026-09-09) 으로 확인했다.
   `bn-money`·`bn-diff` 규칙을 써 놓고 갱신 훅을 잘못 걸어 `bn-intro` 가 끝까지 남았고,
   문제 화면 CSS 가 통째로 죽은 채 데이터 게이트를 **전부** 통과했다. */
const extCssPath = join(resolve(gyo6Root), 'lessons', ...lessonId.split('/'), 'player-ext.css');
const declaredStates = existsSync(extCssPath)
  ? [...new Set([...readFileSync(extCssPath, 'utf8').matchAll(/#app\.([\w-]+)/g)].map((m) => m[1]))]
  : [];
const observedStates = new Set();

const violations = [];
const add = (kind, where, detail) => violations.push({ kind, where, detail });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', (error) => add('page_error', 'runtime', String(error).slice(0, 160)));
/* 콘솔 에러는 대부분 이 환경의 네트워크 잡음(프록시 SSL)이라 차시 결함이 아니다.
   배포 중인 4-1/01 에도 똑같이 뜬다. 스크립트가 실제로 죽는 것은 pageerror 가 잡는다. */
page.on('console', (message) => {
  const text = message.text();
  /* file:// 로 열면 음성을 fetch 로 못 읽는다(`URL scheme "file" is not supported`). 런타임은 그때
     <audio> 로 되받아 재생하므로 차시 결함이 아니다 — 배포 중인 1-1/01 도 똑같이 뜬다(2026-09-29 실측). */
  if (message.type() === 'error' && !/Failed to load resource|net::|URL scheme "file" is not supported/.test(text)) {
    add('console_error', 'runtime', text.slice(0, 160));
  }
});

/* `capture_lesson.mjs` 와 같은 방식이다 — 항해 실패를 삼키고, 화면이 실제로 떴는지로 판정한다.
   file:// 에서는 networkidle 이 안 오는 경우가 있어 예외로 멈추면 안 된다. */
/* `?dev` 로 연다. base 의 장면 이동 패널이 있어야 학습자 경로가 멈춘 뒤에도 나머지 화면에
   닿을 수 있다. 패널은 곧바로 **display:none** 으로 지운다. `visibility:hidden` 으로는 부족하다 —
   레이아웃 상자가 남아 "버튼이 화면 아래로 밀렸다" 로 잡힌다(실측 2026-09-11, 배포 중인
   4-1/01 에서 거짓 양성 2건). `display:none` 이어도 `el.click()` 은 그대로 먹으므로
   장면 이동에는 지장이 없다. */
const devUrl = `${url}${url.includes('?') ? '&' : '?'}dev`;
await page.goto(devUrl, { waitUntil: 'networkidle' }).catch(() => {});
await page.waitForTimeout(1200);
await page.addStyleTag({ content: '.dev-scene-jump{display:none!important}' }).catch(() => {});
if (!(await page.$('#app'))) {
  console.error(`화면이 뜨지 않았다: ${url}`);
  console.error('  #app 이 없다. 빌드가 깨졌거나 경로가 그 차시가 아니다.');
  await browser.close();
  process.exit(2);
}

const snapshot = () =>
  page.evaluate(() => {
    const app = document.getElementById('app');
    const content = document.getElementById('content');
    const box = content?.getBoundingClientRect();
    /* src 가 비어 있는 img 는 화면 전환 도중에 잠깐 생긴다 — 배포 중인 1-1/04 가
       그렇다. 위반은 **경로가 있는데 못 불러온 것**뿐이다. */
    const images = [...document.querySelectorAll('img')]
      .filter((img) => img.complete && img.naturalWidth === 0)
      .map((img) => img.getAttribute('src'))
      .filter((src) => src && src.trim());
    return {
      mode: (app?.className || '').split(' ').filter(Boolean).join(' '),
      text: (content?.innerText || '').replace(/\s+/g, ' ').trim(),
      /* 세로로 넘치면 확인 버튼이 화면 밖으로 나가 문제를 끝낼 수 없다.
         실측 — 팔레트가 5칸이 되자 확인 버튼이 720px 아래로 밀렸다. */
      /* 컨테이너가 아니라 **눌러야 하는 버튼**으로 잰다. 컨테이너는 넘치지 않는데
         안쪽 팔레트가 길어져 확인 버튼만 화면 밖으로 밀리는 경우가 실제로 있었다. */
      offscreen: [...document.querySelectorAll(
        '.pa-confirm, .kp-confirm, #stageBeatCta, .cta, button')]
        .filter((el) => el.offsetParent !== null)
        .map((el) => ({ label: (el.innerText || '').trim().slice(0, 12),
                        below: Math.round(el.getBoundingClientRect().bottom - window.innerHeight) }))
        .filter((item) => item.below > 4),
      /* 넘쳤을 때 **어디가 자리를 먹었는지**까지 준다. "56px 밀렸다" 만으로는
         무엇을 줄여야 할지 모른다 — 실측(2026-09-09)으로 확인했다. 그 되먹임을
         세 회차 돌렸더니 모델이 player-ext.css 를 바이트까지 같게 다시 만들었다. */
      heights: [...document.querySelectorAll(
        '.pa-prompt, .pa-stimulus, .pa-stim-img, .pa-palette, .pa-canvas-wrap, .pa-choices, .kp-pad')]
        .filter((el) => el.offsetParent !== null)
        .map((el) => {
          const rect = el.getBoundingClientRect();
          return { name: '.' + [...el.classList][0], h: Math.round(rect.height) };
        })
        .filter((item) => item.h > 0),
      overflowX: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
      /* 자리를 줄여 화면에 욱여넣으면 이번엔 서로 겹친다. 넘침만 보면 "위반 없음" 이
         나오는데 화면에서는 글자가 가려진다 — 실측(2026-09-09) 으로 확인했다.
         겹치면 안 되는 형제들만 짝지어 본다. */
      overlaps: (() => {
        /* 후보는 base 가 그리는 것과 **차시 ext 가 그리는 것** 둘 다다.
           실측(2026-09-11) — MISSION 3·4 에서 실제로 겹친 것은 ext 가 얹은 자·약도 라벨·
           편지지였는데, 후보가 base 클래스뿐이라 한 건도 안 잡혔다.
           `querySelectorAll` 인 이유도 같다 — 같은 클래스가 여럿일 때 첫 개만 보면
           나머지 겹침이 통째로 안 보인다. */
        const keys = ['.pa-prompt', '.pa-stimulus', '.pa-palette', '.pa-canvas-wrap',
                      '.pa-choices', '.pa-slots', '.pa-sources', '.kp-pad', '.pa-confirm',
                      '.kp-confirm', '[class^="g5-"]', '[class*=" g5-"]'];
        const boxes = [];
        const marked = new Set();
        keys.forEach((sel) => {
          document.querySelectorAll(sel).forEach((el) => {
            if (marked.has(el) || el.offsetParent === null) return;
            marked.add(el);
            boxes.push({ sel: sel.startsWith('[') ? '.' + (el.className || '').split(' ')[0] : sel, el, r: el.getBoundingClientRect() });
          });
        });
        const found = [];
        for (let i = 0; i < boxes.length; i += 1) {
          for (let j = i + 1; j < boxes.length; j += 1) {
            /* 부모가 자식을 감싸는 것은 겹침이 아니다. 이걸 안 빼면 `.pa-canvas-wrap`
               안에 있는 `.pa-palette` 가 매번 겹침으로 잡힌다(2026-09-09 실측). */
            if (boxes[i].el.contains(boxes[j].el) || boxes[j].el.contains(boxes[i].el)) continue;
            /* **얹은 것은 겹침이 아니다.** 봉투 위의 손글씨 메모와 우표, 점판 안의 점처럼
               한쪽이 다른 쪽 안에 통째로 들어가는 것은 의도된 층이다(실측 2026-09-11 —
               `.g5-*` 를 후보에 넣자마자 이런 것들이 무더기로 잡혔다).
               가려서 문제가 되는 것은 **부분만 걸치는** 경우다. */
            const a = boxes[i].r;
            const b = boxes[j].r;
            const inside = (x, y) => x.left >= y.left - 1 && x.right <= y.right + 1
                                  && x.top >= y.top - 1 && x.bottom <= y.bottom + 1;
            if (inside(a, b) || inside(b, a)) continue;
            /* 같은 클래스끼리는 같은 규칙이 나란히 놓은 것이다(점·눈금·보기 칸).
               서로 걸쳐 보여도 배치 결함이 아니라 그 규칙의 간격 문제이고,
               그건 이 검사가 아니라 눈으로 볼 일이다. */
            if (boxes[i].sel === boxes[j].sel) continue;
            const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
            const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
            if (w > 4 && h > 4) {
              found.push({ a: boxes[i].sel, b: boxes[j].sel,
                           w: Math.round(w), h: Math.round(h) });
            }
          }
        }
        return found;
      })(),
      brokenImages: images,
      /* 글자 자체를 잰다 — 요소 상자가 아니라 **글자 노드의 실제 영역**이다.
         위 겹침 검사는 정해 둔 클래스 목록만 봐서 ext 가 그린 라벨(`.gj-lbl` 등)끼리 뭉친 것과
         말풍선이 화면 옆으로 나간 것을 못 봤다(실측 2026-09-29, 4-1/03 — 정삼각형의 60°·60°·?° 가
         한 점에 겹쳤고 도입 말풍선 앞부분이 화면 왼쪽 밖으로 잘렸는데 "위반 없음" 이었다). */
      texts: (() => {
        const vw = window.innerWidth;
        const nodes = [];
        const walker = document.createTreeWalker(document.getElementById('app') || document.body, NodeFilter.SHOW_TEXT);
        for (let node = walker.nextNode(); node; node = walker.nextNode()) {
          const text = node.nodeValue.trim();
          const el = node.parentElement;
          if (!text || !el || el.closest('.dev-scene-jump, script, style')) continue;
          if (el.checkVisibility && !el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
          const range = document.createRange();
          range.selectNodeContents(node);
          const r = range.getBoundingClientRect();
          if (r.width < 2 || r.height < 2) continue;
          nodes.push({ el, text: text.slice(0, 16), r });
        }
        const offscreen = nodes
          .filter((n) => n.r.left < -4 || n.r.right > vw + 4)
          .map((n) => ({ text: n.text, left: Math.round(n.r.left), right: Math.round(n.r.right) }));
        const overlaps = [];
        for (let i = 0; i < nodes.length; i += 1) {
          for (let j = i + 1; j < nodes.length; j += 1) {
            const a = nodes[i];
            const b = nodes[j];
            if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
            const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
            const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
            if (w > 4 && h > 4) overlaps.push({ a: a.text, b: b.text, w: Math.round(w), h: Math.round(h) });
          }
        }
        return { offscreen, overlaps };
      })(),
    };
  });

/* 글자 검사 결과. **아직 위반이 아니라 참고다.** 게이트는 배포 차시 거짓 양성 0건일 때만 넣는다(CLAUDE.md).
   첫 측정(2026-09-29)에서 각도기 눈금 숫자처럼 원래 촘촘한 글자가 겹침으로 잡혔다 — 기준선을 세기 전까지는
   `advisories` 로만 내고 종료 코드에 넣지 않는다. `verify_lesson.py` 는 이것을 막지 않는 medium 으로 올린다. */
const advisories = [];
const addTextIssues = (state, key) => {
  for (const item of state.texts.offscreen) {
    const tag = `textoff|${item.text}|${key}`;
    if (seen.has(tag)) continue;
    seen.add(tag);
    advisories.push({ kind: 'text_offscreen', where: state.mode,
      detail: `글자 "${item.text}" 가 화면 가로 밖으로 나갔다 (x ${item.left}~${item.right}, 화면 폭 1280)` });
  }
  for (const item of state.texts.overlaps) {
    const tag = `textover|${item.a}|${item.b}|${key}`;
    if (seen.has(tag)) continue;
    seen.add(tag);
    advisories.push({ kind: 'text_overlap', where: state.mode,
      detail: `글자 "${item.a}" 와 "${item.b}" 가 ${item.w}×${item.h}px 겹친다` });
  }
};

await page.click('#introStartBtn', { force: true }).catch(() => {});

const seen = new Set();
let stuckRuns = 0;
let lastKey = '';

for (let step = 0; step < 60; step += 1) {
  await page.waitForTimeout(800);
  const state = await snapshot();
  const key = `${state.mode}|${state.text.slice(0, 60)}`;
  for (const cls of state.mode.split(' ')) observedStates.add(cls);

  for (const rule of FORBIDDEN) {
    if (rule.re.test(state.text) && !seen.has(`${rule.kind}|${key}`)) {
      seen.add(`${rule.kind}|${key}`);
      add(rule.kind, state.mode, `${rule.why}: ${state.text.slice(0, 70)}`);
    }
  }
  for (const item of state.offscreen) {
    const tag = `offscreen|${item.label}|${key}`;
    if (seen.has(tag)) continue;
    seen.add(tag);
    const budget = state.heights.map((h) => `${h.name} ${h.h}px`).join(' + ');
    add('button_offscreen', state.mode,
      `버튼 "${item.label}" 이 화면 아래로 ${item.below}px 밀려 누를 수 없다. `
      + `세로를 먹는 것: ${budget}. 화면 높이는 720px 이다`);
  }
  if (state.overflowX > 8 && !seen.has(`overflowx|${key}`)) {
    seen.add(`overflowx|${key}`);
    add('overflow_x', state.mode, `가로로 ${state.overflowX}px 넘친다`);
  }
  for (const item of state.overlaps) {
    const tag = `overlap|${item.a}|${item.b}|${key}`;
    if (seen.has(tag)) continue;
    seen.add(tag);
    add('overlap', state.mode,
      `${item.a} 와 ${item.b} 가 ${item.w}×${item.h}px 겹친다. 뒤에 있는 것이 가려진다`);
  }

  for (const src of state.brokenImages) {
    if (!seen.has(`img|${src}`)) {
      seen.add(`img|${src}`);
      add('broken_image', state.mode, `그림을 못 불러온다: ${src}`);
    }
  }
  addTextIssues(state, key);

  /* 같은 화면이 계속 나오면 진행이 막힌 것이다. 화면 전환 애니메이션 때문에
     픽셀 비교는 못 믿고(버튼이 계속 맥동한다) 텍스트로 본다. */
  const cta = page.locator('#stageBeatCta');
  const hasCta = (await cta.count()) > 0;

  /* 문제 화면에서 멈춰 있는 것은 정상이다 — 학습자가 답을 놓기를 기다리는 중이다.
     위반은 **넘어가는 버튼이 있는데 눌러도 안 넘어갈 때**뿐이다. 이 구분이 없으면
     배포 중인 4-1/01 도 걸린다. */
  stuckRuns = hasCta && key === lastKey ? stuckRuns + 1 : 0;
  lastKey = key;
  if (stuckRuns >= 4) {
    add('stuck', state.mode,
      `넘어가는 버튼을 ${stuckRuns}번 눌러도 화면이 그대로다: ${state.text.slice(0, 60)}`);
    break;
  }
  if (hasCta) await cta.click({ force: true }).catch(() => {});
}

/* ── 못 간 화면으로 이어서 간다 ────────────────────────────────────────────
   위 훑기는 학습자 경로라 **첫 미션 앞에서 멈춘다.** 그러면 문제 화면의 겹침·넘침을
   한 번도 못 보고 "위반 없음" 이 나온다 — 실측(2026-09-11) 로 MISSION 2~5 의 겹침이
   전부 그렇게 통과했고, 검사기 스스로 "안 붙은 상태 클래스 8개" 라고 적고 있었다.
   **못 본 화면을 위반 없음으로 보고하는 것이 가장 나쁘다.**
   base 가 `?dev` 로 여는 장면 이동으로 나머지를 돌며 같은 검사를 건다. */
const jumped = await page.evaluate(() => document.querySelectorAll('.dev-scene-jump button').length);
if (jumped) {
  for (let i = 0; i < jumped; i += 1) {
    await page.evaluate((index) => {
      const list = document.querySelectorAll('.dev-scene-jump button');
      if (list[index]) list[index].click();
    }, i);
    await page.waitForTimeout(900);
    const state = await snapshot();
    const key = `${state.mode}|${state.text.slice(0, 60)}`;
    for (const cls of state.mode.split(' ')) observedStates.add(cls);
    for (const rule of FORBIDDEN) {
      if (rule.re.test(state.text) && !seen.has(`${rule.kind}|${key}`)) {
        seen.add(`${rule.kind}|${key}`);
        add(rule.kind, state.mode, `${rule.why}: ${state.text.slice(0, 70)}`);
      }
    }
    for (const item of state.overlaps) {
      const tag = `overlap|${item.a}|${item.b}|${key}`;
      if (seen.has(tag)) continue;
      seen.add(tag);
      add('overlap', state.mode, `${item.a} 와 ${item.b} 가 ${item.w}×${item.h}px 겹친다. 뒤에 있는 것이 가려진다`);
    }
    for (const src of state.brokenImages) {
      if (!seen.has(`img|${src}`)) {
        seen.add(`img|${src}`);
        add('broken_image', state.mode, `그림을 못 불러온다: ${src}`);
      }
    }
    addTextIssues(state, key);
  }
}

/* 여기는 **위반이 아니라 참고**다. 이 훑기는 문제를 풀지 못해서(돈을 끌어다 놓거나
   키패드를 눌러야 다음으로 간다) 뒤쪽 화면에 닿지 못한다. 그래서 "한 번도 안 붙었다" 가
   "죽었다" 를 뜻하지 않는다 — 배포 중인 4-1/01 도 19개가 그렇게 잡혔고 전부 정상이었다.
   그래도 어디까지 갔는지와 함께 보여 주면 모델이 고칠 실마리가 된다. */
const deadStates = declaredStates.filter((cls) => !observedStates.has(cls));

await browser.close();

const reachedText = `훑은 화면 상태: ${[...observedStates].join(' ') || '(없음)'}`;

if (violations.length) {
  console.log(`화면 위반 ${violations.length}건 — ${url}`);
  for (const item of violations) console.log(`  [${item.kind}] ${item.where} — ${item.detail}`);
} else {
  console.log(`화면 위반 없음 — ${url}`);
}

if (deadStates.length) {
  console.log(`
참고 — 이번 훑기에서 안 붙은 상태 클래스 (${deadStates.length}개)`);
  console.log(`  #app.${deadStates.join(' · #app.')}`);
  console.log(`  ${reachedText}`);
  console.log('  훑기가 문제를 풀지 못해 뒤쪽 화면에 못 갔을 수도 있다. 위반으로 세지 않는다.');
}

if (advisories.length) {
  console.log(`\n참고 — 글자 겹침·화면 밖 ${advisories.length}건 (기준선 확인 전이라 위반으로 세지 않는다)`);
  for (const item of advisories.slice(0, 12)) console.log(`  [${item.kind}] ${item.where} — ${item.detail}`);
  if (advisories.length > 12) console.log(`  … ${advisories.length - 12}건 더`);
}

if (jsonPath) {
  writeFileSync(jsonPath, JSON.stringify({
    url,
    violations,
    advisories,
    dead_states: deadStates,
    observed_states: [...observedStates],
  }, null, 2));
}

process.exit(violations.length ? 1 : 0);
