/**
 * 빌드된 차시를 클릭하며 화면을 찍는다. LLM 0회.
 *
 *   node tools/capture_lesson.mjs <dist/index.html 경로 또는 URL> <출력 디렉토리> [최대 화면 수]
 *
 * 왜 node 인가: playwright 를 이 레포에 새로 설치하지 않는다. gyo6_content 가 이미 갖고 있고
 * 브라우저 바이너리도 거기 받혀 있다. **이 스크립트는 그 node_modules 안에서 실행한다** —
 * `cwd` 를 gyo6_content 로 두고 부른다(`stages/lesson_review.py` 가 그렇게 한다).
 *
 * 왜 클릭으로 도는가: gyo6_content 런타임에는 `data-qa-scene` 같은 장면 점프 hook 이 없다.
 * 학습자가 실제로 누르는 경로를 그대로 밟는 것이 화면을 보는 유일한 길이고,
 * **눌러도 안 넘어가는 결함**이 그 과정에서 함께 드러난다(실측으로 그렇게 찾았다).
 */
import { mkdirSync, writeFileSync, existsSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [target, outDir, maxShots = '10', gyo6Root, mode] = process.argv.slice(2);
if (!target || !outDir) {
  console.error('사용법: node capture_lesson.mjs <URL 또는 파일경로> <출력 디렉토리> [최대 화면 수] [gyo6_content 경로] [--scene-jump]');
  process.exit(1);
}

/* `--scene-jump` 는 **문제 화면까지 본다.**
 *
 * 기본 모드는 학습자가 누르는 길을 그대로 밟는다. 그 길은 문제 앞에서 멈춘다 — 드래그·선 긋기·
 * 키패드를 자동으로 풀 수 없기 때문이다. 실측(2026-09-11) — 3-1/05 는 15장을 찍고 전부 컷씬이었고,
 * 미션 다섯 개의 배치는 **한 장도 찍히지 않았다.** 안 찍힌 화면은 대조도 못 한다.
 *
 * base 는 `?dev` 로 장면 이동 패널(`.dev-scene-jump`)을 연다. 장면·대화 묶음·문제마다 버튼이
 * 하나씩 있어, 풀지 않고 모든 화면에 닿을 수 있다. 배치를 보는 것이 목적일 때는 이쪽이 맞다.
 *
 * 진행 가능 여부는 이 모드로 못 본다(전부 점프하므로). 그건 기본 모드와 `check_rendered.mjs` 의 몫이다.
 */
const sceneJump = mode === '--scene-jump';

// playwright 는 이 레포에 설치하지 않는다. gyo6_content 것을 절대 경로로 부른다 —
// node 는 import 를 **스크립트 위치** 기준으로 푸므로 cwd 를 옮기는 것만으로는 안 된다.
const root = gyo6Root || process.env.GYO6_ROOT || process.cwd();
const entry = path.join(root, 'node_modules', 'playwright', 'index.mjs');
if (!existsSync(entry)) {
  console.error(`playwright 를 찾지 못했다: ${entry}\n  gyo6_content 경로를 4번째 인자나 GYO6_ROOT 로 준다.`);
  process.exit(1);
}
const { chromium } = await import(pathToFileURL(entry).href);
const url = /^https?:\/\//.test(target) ? target : 'file://' + path.resolve(target).replace(/\\/g, '/');
mkdirSync(outDir, { recursive: true });

/* 지난 회차의 화면을 지운다.
 *
 * 파일 이름은 `s{번호}-{누른 글자}.png` 라 **회차마다 달라진다.** 그래서 덮어쓰이지 않고
 * 쌓인다 — 실측(2026-09-11) 같은 디렉토리에 `s02-step-1장면.png`(지난 회차)와
 * `s02-편지를클릭하세요.png`(이번 회차)가 함께 있었다. 지금은 `capture.json` 목록으로만
 * 넘겨 판정에 안 섞이지만, **고친 뒤의 화면과 고치기 전의 화면이 한 폴더에 있는 것** 자체가
 * 언제든 잘못 읽힐 자리다. 캡처는 그 시점의 화면 전부여야 한다. */
readdirSync(outDir)
  .filter((name) => /^s\d+-.*\.png$/.test(name) || name === 'capture.json')
  .forEach((name) => rmSync(path.join(outDir, name), { force: true }));

// 헤더의 목록·소리·처음으로 버튼은 콘텐츠 진행이 아니다.
const SKIP = /목록|소리|처음으로|닫기|나가기|다음\s*차시/;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e).slice(0, 200)));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });

const openUrl = sceneJump ? `${url}${url.includes('?') ? '&' : '?'}dev` : url;
await page.goto(openUrl, { waitUntil: 'networkidle' }).catch(() => {});
await page.waitForTimeout(1500);

const shots = [];
let stuck = 0;
const capture = async (label) => {
  const name = `s${String(shots.length + 1).padStart(2, '0')}-${label}.png`;
  const file = path.join(outDir, name);
  await page.screenshot({ path: file });
  // 무대 텍스트만으로는 컷 전환을 못 가른다 — 헤더가 늘 같은 글자를 갖고 있어서
  // 대사가 바뀌어도 같은 화면으로 보인다(실측). 픽셀도 함께 본다.
  const text = (await page.locator('#app').first().innerText().catch(() => '') || '')
    .replace(/\s+/g, ' ').trim();
  const png = readFileSync(file);
  const fingerprint = createHash('sha1').update(png).digest('hex').slice(0, 12);
  shots.push({ file: name, clicked: label, stage_text: text.slice(0, 300), fingerprint });
  return `${fingerprint}|${text}`;
};

/* 누르기. **일반 클릭이 실패하면 force 로 한 번 더 누른다.**
 *
 * 왜 — 이 런타임은 버튼이 계속 움직인다(타이틀 숨쉬기, 말풍선 팝, 커서 따라다니기).
 * playwright 의 기본 클릭은 "요소가 **안정될 때까지**" 기다리므로 그 버튼을 영영 못 누른다.
 * 실측(2026-09-11): 타이틀의 `편지를 클릭하세요` 가 `waiting for element to be visible,
 * enabled and stable` 로 타임아웃했고, 예전 코드는 그 실패를 `.catch(() => {})` 로 삼킨 뒤
 * **같은 버튼을 15번 다시 눌러** 같은 화면 15장을 남겼다. 타이틀이 애니메이션 중이라
 * 픽셀이 매번 달라서 `stuck` 검사에도 안 걸렸다.
 *
 * force 로 가려진 버튼까지 눌러 버리는 것은 감수한다 — "버튼이 가려져 못 누른다"는
 * `tools/check_rendered.mjs` 가 겹침으로 따로 본다. 여기서는 끝까지 도는 것이 일이고,
 * force 가 필요했다는 사실 자체는 `forced` 에 남겨 신호를 잃지 않는다.
 */
const clickNotes = [];
const pressButton = async (b, label) => {
  const failed = await b.click({ timeout: 2000 }).then(() => null, (e) => e);
  if (!failed) return 'clicked';
  const stillFailed = await b.click({ timeout: 2000, force: true }).then(() => null, (e) => e);
  if (stillFailed) {
    clickNotes.push(`${label}: 눌리지 않음 — ${String(stillFailed).split('\n')[0].slice(0, 120)}`);
    return 'failed';
  }
  clickNotes.push(`${label}: 일반 클릭 실패 → force 로 눌렀다 (요소가 계속 움직인다)`);
  return 'forced';
};

/* 장면 이동 패널은 개발용이라 화면의 일부가 아니다. 켜자마자 숨긴다 —
   안 감추면 대조하는 쪽이 그것을 "스토리보드에 없는 요소"로 잡고,
   학습자 경로 훑기가 그 버튼을 눌러 엉뚱한 데로 튄다(`:visible` 이 숨긴 것을 거른다). */
if (sceneJump) {
  await page.addStyleTag({ content: '.dev-scene-jump{display:none!important}' }).catch(() => {});
}

let previous = await capture('start');
for (let i = 0; i < Number(maxShots); i += 1) {
  const buttons = page.locator('#app button:visible');
  const total = await buttons.count();
  let label = null;
  for (let k = 0; k < total; k += 1) {
    const b = buttons.nth(k);
    const t = ((await b.textContent().catch(() => '')) || '').replace(/\s+/g, '');
    if (!t || SKIP.test(t)) continue;
    label = t.slice(0, 12);
    await pressButton(b, label);
    break;
  }
  if (!label) break;
  await page.waitForTimeout(1600);
  const text = await capture(label);
  // 같은 화면이 반복되면 전환이 안 되는 것이다. 결함이므로 기록하고 멈춘다.
  if (text === previous) {
    stuck += 1;
    if (stuck >= 2) {
      shots[shots.length - 1].stuck = true;
      break;
    }
  } else {
    stuck = 0;
  }
  previous = text;
}

/* ── 이어서 장면 이동 ──────────────────────────────────────────────────────
   위 훑기는 **컷 단위 깊이**를 준다(대사가 한 줄씩 넘어가는 화면). 다만 문제 앞에서 멈춘다.
   여기서는 **넓이**를 채운다 — 장면·대화 묶음·문제마다 버튼 하나씩 눌러 전부 찍는다.
   둘 중 하나만 하면 반쪽이다. 실측(2026-09-11): 이동만 하면 대사 컷이 안 찍혀
   스토리보드 7쪽이 "짝이 없다"로 남았고, 훑기만 하면 문제 화면이 한 장도 안 찍혔다.
   누르는 것은 페이지 안에서 `el.click()` 으로 한다 — 숨긴 요소는 좌표 클릭이 안 먹는다. */
if (sceneJump) {
  const targets = await page.evaluate(() =>
    [...document.querySelectorAll('.dev-scene-jump button')].map((b) => ({
      kind: b.dataset.kind || 'step',
      label: (b.textContent || '').trim().slice(0, 12),
    }))
  );
  if (!targets.length) {
    clickNotes.push('장면 이동 패널이 없다 — base 가 `?dev` 를 지원하는지 확인한다. 문제 화면은 안 찍혔다.');
  }
  /* 이동 버튼은 **묶음의 처음**으로 간다. 대화 묶음 안에 컷이 여럿이면 첫 컷만 찍힌다 —
     실측(2026-09-11): outro 5컷 중 1컷만 찍혀 "뒤 컷이 없다"는 거짓 신호가 났고,
     Scene 7-2 시각화 4컷은 통째로 안 찍혔다. 그래서 이동한 뒤 그 묶음 안을 몇 컷 더 넘긴다. */
  /* 5 로는 모자랐다 — R5 대화 묶음이 9컷이라 Scene 7-2 시각화 넉 장이 안 찍혔고,
     스토리보드 23~25쪽이 "짝이 없다" 로 남았다(실측 2026-09-11). 묶음이 끝나면
     같은 화면이 반복돼 저절로 멈추므로, 넉넉히 두는 쪽이 안전하다. */
  const groupDepth = Number(process.env.CAPTURE_GROUP_DEPTH || 12);
  for (let i = 0; i < targets.length; i += 1) {
    await page.evaluate((index) => {
      const list = document.querySelectorAll('.dev-scene-jump button');
      if (list[index]) list[index].click();
    }, i);
    await page.waitForTimeout(1400);
    let previousShot = await capture(`${targets[i].kind}-${targets[i].label}`);
    if (targets[i].kind === 'prob') continue;
    for (let k = 0; k < groupDepth; k += 1) {
      const next = await page.$('.bubble-next:visible, #stageBeatCta:visible, button.cta:visible');
      if (!next) break;
      const label = ((await next.textContent().catch(() => '')) || '').replace(/\s+/g, '').slice(0, 10);
      if (SKIP.test(label)) break;
      await pressButton(next, label);
      await page.waitForTimeout(1100);
      const shot = await capture(`${targets[i].label}-${k + 1}`);
      if (shot === previousShot) break;
      previousShot = shot;
    }
  }
}

const report = {
  url: openUrl,
  mode: sceneJump ? 'walk+scene-jump' : 'walk',
  shots,
  stuck: shots.some(s => s.stuck),
  page_errors: [...new Set(errors)].slice(0, 10),
  click_notes: [...new Set(clickNotes)].slice(0, 10),
};
writeFileSync(path.join(outDir, 'capture.json'), JSON.stringify(report, null, 2) + '\n', 'utf-8');
console.log(JSON.stringify({ count: shots.length, stuck: report.stuck, errors: report.page_errors.length }));
await browser.close();
