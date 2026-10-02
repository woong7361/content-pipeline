/**
 * 빌드된 차시를 학습자처럼 **끝까지 풀며** 문항마다 정답·오답·힌트가 도는지 본다. LLM 0회.
 *
 *   node tools/run_functional_tests.mjs <dist/index.html 경로 또는 URL> <출력 디렉토리> <gyo6_content 경로>
 *
 * 왜 필요한가 — `check_outputs` 가 `tests/functional-test-plan.json` 을 만들지만 **아무도 실행하지
 * 않았다.** `capture_lesson.mjs` 는 문제 앞에서 멈추고(키패드·드래그를 못 푼다), `--scene-jump` 는
 * 문제를 풀지 않고 건너뛴다. 그래서 "정답을 넣으면 넘어가는가", "두 번 틀리면 힌트가 뜨는가" 를
 * 본 적이 없다. 실측(2026-09-29, 4-1/03) — 힌트가 도형판 뒤에 가려지는 결함은 **두 번 틀린
 * 뒤에만** 보이는 화면이라 어느 캡처에도 없었고, 문항을 직접 푼 검수에서야 나왔다.
 *
 * 어떻게 답을 아는가 — base 의 모든 문제는 `PROBLEM_ATOMS[k].mount(host, spec, ctx)` 를 지난다.
 * ext 가 등록한 원자(`sortToBin` 등)도 같은 표에 들어간다. 그 mount 를 감싸 **그 문제의 사양과
 * 채점 통로(ctx.submit)** 를 잡는다. 정답은 사양에 있다 — `randomizeProblem` 이 바꾼 값까지.
 *
 * 두 가지 방식으로 푼다. 어느 쪽이었는지를 결과에 반드시 적는다.
 *   ui         실제 버튼을 누른다(choicePick · multiPick · keypad · judgeRows).
 *              채점 로직과 화면 반응을 **둘 다** 본다.
 *   flow-only  UI 를 자동으로 못 푸는 원자(드래그·ext 원자)는 잡아 둔 `ctx.submit(false/true)` 를
 *              직접 부른다. **채점 로직은 안 보고** 정오 이후의 흐름(재시도·힌트·다음 문제)만 본다.
 *
 * 결과: <출력 디렉토리>/functional-results.json, 상태별 캡처 f001-<문항>-<상태>.png
 * 종료 코드 0 = 실패 없음, 1 = 실패가 있다, 2 = 실행 자체를 못 했다.
 */
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';

const [target, outDir, gyo6Root] = process.argv.slice(2);
if (!target || !outDir || !gyo6Root) {
  console.error('사용법: node tools/run_functional_tests.mjs <URL 또는 dist/index.html> <출력 디렉토리> <gyo6_content 경로>');
  process.exit(2);
}

// playwright 는 gyo6_content 의 것을 쓴다 — `check_rendered.mjs` 와 같은 이유.
const localPlaywright = join(resolve(gyo6Root), 'node_modules', 'playwright', 'index.js');
const playwright = existsSync(localPlaywright)
  ? await import(pathToFileURL(localPlaywright).href)
  : await import('playwright');
const chromium = playwright.chromium ?? playwright.default?.chromium;
if (!chromium) {
  console.error(`playwright 를 못 찾았다: ${localPlaywright}`);
  process.exit(2);
}

const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(resolve(target)).href;
mkdirSync(outDir, { recursive: true });

const results = {
  url,
  // 학습자가 본 순서 그대로의 **모든** 화면(대사·이야기·문제 상태·완료·인증서). ④ 판정이 이것을 본다.
  // 문제 화면만 찍으면 스토리보드 대조가 "짝 없는 쪽"을 장면 누락으로 잘못 낸다(실측 2026-09-29 — 5건).
  timeline: [],
  problems: [],
  seen_ids: [],
  stuck: false,
  stuck_detail: '',
  ended: '',
  page_errors: [],
  click_notes: [],
};
const seenIds = new Set();
let shotNo = 0;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', (error) => results.page_errors.push(String(error).slice(0, 200)));

/* ── 페이지 안에서 도는 훅 ──────────────────────────────────────────────────
   `PROBLEM_ATOMS` · `stepIdx` · `probIdx` · `correct` · `_paProblems` · `L` 은 player.js 의
   최상위 선언이라 같은 전역 스코프에서 이름으로 닿는다(window 속성은 아니다). */
const HOOK = () => {
  if (window.__qa) return true;
  if (typeof PROBLEM_ATOMS === 'undefined') return false;
  window.__qa = { mounts: [], lastRandom: null };
  const ext = window.lessonExt;
  if (ext && typeof ext.randomizeProblem === 'function' && !ext.randomizeProblem.__qa) {
    const original = ext.randomizeProblem;
    ext.randomizeProblem = function (...args) {
      const value = original.apply(this, args);
      window.__qa.lastRandom = value ?? null;
      return value;
    };
    ext.randomizeProblem.__qa = true;
  }
  return true;
};

// ext 가 원자를 늦게 등록할 수 있으므로 매 바퀴 다시 감싼다. 이미 감싼 것은 건너뛴다.
const WRAP = () => {
  if (typeof PROBLEM_ATOMS === 'undefined' || !window.__qa) return 0;
  let wrapped = 0;
  for (const [key, atom] of Object.entries(PROBLEM_ATOMS)) {
    if (!atom || atom.__qa || typeof atom.mount !== 'function') continue;
    const original = atom.mount;
    atom.mount = function (host, spec, ctx) {
      const entry = (typeof _paProblems !== 'undefined') ? _paProblems[probIdx] : null;
      const problem = window.__qa.lastRandom ?? entry?.spec ?? {};
      window.__qa.lastRandom = null;
      const index = window.__qa.mounts.length;
      const record = {
        index,
        key,
        probKey: `${stepIdx}:${probIdx}`,
        problemId: String(problem.id ?? problem.specId ?? ''),
        hintAfterWrong: problem.hintAfterWrong ?? null,
        spec,
        submits: [],
      };
      host.dataset.qaMount = String(index);
      const wrappedCtx = Object.assign({}, ctx, {
        submit: (ok, el) => {
          record.submits.push(!!ok);
          return ctx.submit(ok, el);
        },
      });
      record.ctx = wrappedCtx;
      const handle = original.call(this, host, spec, wrappedCtx);
      record.terminal = !!(handle && handle.terminal);
      window.__qa.mounts.push(record);
      return handle;
    };
    atom.__qa = true;
    wrapped += 1;
  }
  return wrapped;
};

const STATE = () => {
  const norm = (s) => String(s || '').replace(/\s+/g, '');
  const step = (typeof L !== 'undefined' && L.steps) ? L.steps[stepIdx] : null;
  const speech = norm(document.querySelector('#speech .bubble-text')?.innerText
    ?? document.querySelector('#speech')?.innerText);
  // 말풍선 글과 같은 컷을 찾아 그 id 를 본 것으로 센다(장면 도달 판정용).
  let cutId = '';
  if (speech && typeof L !== 'undefined') {
    const cuts = (L.steps || []).flatMap((s) => [
      ...(s.stageDirections || []),
      ...(s.rounds || []).flatMap((r) => r.stageDirections || []),
    ]);
    const hit = cuts.find((c) => c && norm(c.speechText) === speech);
    cutId = hit ? String(hit.id ?? hit.specId ?? '') : '';
  }
  const app = document.getElementById('app');
  return {
    stepIdx: typeof stepIdx !== 'undefined' ? stepIdx : -1,
    probIdx: typeof probIdx !== 'undefined' ? probIdx : -1,
    correct: typeof correct !== 'undefined' ? correct : -1,
    stepId: step ? String(step.id ?? '') : '',
    stepSpecId: step ? String(step.specId ?? '') : '',
    lastStep: typeof L !== 'undefined' && L.steps ? stepIdx >= L.steps.length - 1 : false,
    cutId,
    // 이야기 카드는 `#content` 밖 팝업이라 본문 글로는 카드끼리 구별이 안 된다.
    slide: typeof realLifeSlideIdx !== 'undefined' ? realLifeSlideIdx : -1,
    story: !!document.querySelector('.real-life-popup'),
    speech: speech.slice(0, 40),
    panel: !!document.querySelector('.pa-panel'),
    hint: !!document.querySelector('.pa-panel .pa-hint') || !!app?.classList.contains('hint-cast'),
    mode: (app?.className || '').trim(),
    text: (document.getElementById('content')?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80),
    mounts: window.__qa ? window.__qa.mounts.length : 0,
  };
};

// 지금 보이는 "넘어가는" 버튼 하나. 학습자가 누를 순서대로 본다.
const NEXT_SELECTORS = ['#stageBeatCta', '.bubble-next', '#realLifeNextBtn', '#content .cta', '#introStartBtn'];
const FIND_NEXT = (selectors) => {
  for (const sel of selectors) {
    for (const el of document.querySelectorAll(sel)) {
      const rect = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      if (rect.width < 2 || rect.height < 2) continue;
      if (style.visibility === 'hidden' || style.display === 'none' || Number(style.opacity) < 0.5) continue;
      if (el.disabled) continue;
      return sel;
    }
  }
  return '';
};

const state = () => page.evaluate(STATE);
const shot = async (label) => {
  shotNo += 1;
  const file = `f${String(shotNo).padStart(3, '0')}-${label.replace(/[^\w.-]+/g, '_')}.png`;
  await page.mouse.move(1270, 710);
  /* 화면 전환(페이드) 도중에 찍으면 화면 전체가 어둡게 찍혀 판정이 "짙은 오버레이" 로 오판한다
     (실측 2026-09-29, 4-1/04 — 막는 것 2건이 그것이었다). #app 의 애니메이션이 끝날 때까지 기다린다. */
  for (let i = 0; i < 10; i += 1) {
    const busy = await page.evaluate(() => document.getAnimations().some((a) => a.playState === 'running'
      && a.effect && a.effect.target === document.getElementById('app'))).catch(() => false);
    if (!busy) break;
    await page.waitForTimeout(150);
  }
  await page.screenshot({ path: join(outDir, file) });
  results.timeline.push({ file, label });
  return file;
};
const shotScreens = new Set();
const note = (st) => {
  for (const id of [st.stepId, st.stepSpecId, st.cutId]) if (id) seenIds.add(id);
};

/* 누른다. 일반 클릭이 안 되면 force 로 한 번 더 — 이 런타임은 버튼이 계속 움직여서
   playwright 가 "안정" 을 영영 못 기다린다(CLAUDE.md). force 가 필요했다는 사실은 남긴다. */
async function press(locator, label) {
  try {
    await locator.click({ timeout: 1500 });
  } catch {
    await locator.click({ force: true, timeout: 3000 });
    if (!results.click_notes.includes(label)) results.click_notes.push(label);
  }
}

async function mountsFor(probKey) {
  return page.evaluate((key) => window.__qa.mounts
    .filter((m) => m.probKey === key)
    .map((m) => ({ index: m.index, key: m.key, problemId: m.problemId, terminal: m.terminal,
                   hintAfterWrong: m.hintAfterWrong, spec: JSON.parse(JSON.stringify(m.spec ?? {})) })), probKey);
}

/* ── 원자별 풀이 ──────────────────────────────────────────────────────────── */
const asList = (v) => (Array.isArray(v) ? v : [v]).map((x) => String(x ?? ''));
const optValue = (o) => String(o && typeof o === 'object' ? (o.value ?? o.label ?? '') : (o ?? ''));
const within = (m, sel) => page.locator(`[data-qa-mount="${m.index}"] ${sel}`);
const cssValue = (v) => v.replace(/["\\]/g, '\\$&');

const UI = {
  async choicePick(m, right) {
    const answer = String(m.spec.answer ?? '');
    const values = (m.spec.options ?? []).map(optValue);
    const pick = right ? answer : values.find((v) => v !== answer);
    if (pick === undefined) return 'no-wrong-option';
    await press(within(m, `.pa-choice[data-v="${cssValue(pick)}"]`).first(), 'choicePick');
    return '';
  },
  async multiPick(m, right) {
    const answer = new Set(asList(m.spec.answer));
    const values = (m.spec.items ?? m.spec.options ?? []).map(optValue);
    const want = right ? values.filter((v) => answer.has(v))
      : (answer.size === 1 && answer.has(values[0]) ? values : [values[0]]);
    for (const v of want) await press(within(m, `.pa-item[data-v="${cssValue(v)}"]`).first(), 'multiPick');
    await press(within(m, '.pa-confirm').first(), 'multiPick 확인');
    return '';
  },
  async keypad(m, right) {
    const answers = asList(m.spec.answer);
    const typed = right ? answers : [answers[0] === '0' ? '1' : '0'];
    for (const value of typed) {
      for (const ch of value) await press(within(m, `.hk-key[data-k="${ch}"]`).first(), 'keypad');
      await press(within(m, '.hk-ok').first(), 'keypad 확인');
      await page.waitForTimeout(150);
    }
    return '';
  },
  async judgeRows(m, right) {
    const rows = (m.spec.rows ?? []).map((r) => String(r && typeof r === 'object' ? (r.answer ?? 'O') : 'O').toUpperCase() || 'O');
    for (let i = 0; i < rows.length; i += 1) {
      const row = within(m, `.pa-judge-row[data-row="${i}"]`);
      if (await row.evaluate((el) => el.classList.contains('is-done')).catch(() => true)) continue;
      const want = right ? rows[i] : (rows[i] === 'O' ? 'X' : 'O');
      await press(row.locator(`.pa-judge-btn[data-v="${want}"]`).first(), 'judgeRows');
      if (!right) return '';
      await page.waitForTimeout(120);
    }
    return '';
  },
};

async function submitFlow(m, ok) {
  await page.evaluate(({ index, ok }) => {
    const record = window.__qa.mounts[index];
    record.ctx.submit(ok, null);
  }, { index: m.index, ok });
}

async function answer(mounts, right) {
  // 오답은 첫 채점 원자 하나로 충분하다. 정답은 채점 원자 **전부**가 내야 채점된다.
  const terminals = mounts.filter((m) => m.terminal);
  const targets = right ? terminals : terminals.slice(0, 1);
  const modes = [];
  for (const m of targets) {
    if (UI[m.key]) {
      const reason = await UI[m.key](m, right);
      if (reason) return { mode: 'ui', skipped: reason };
      modes.push('ui');
    } else {
      await submitFlow(m, right);
      modes.push('flow-only');
    }
  }
  return { mode: modes.includes('flow-only') ? 'flow-only' : 'ui', skipped: '' };
}

async function testProblem(st) {
  const probKey = `${st.stepIdx}:${st.probIdx}`;
  const mounts = await mountsFor(probKey);
  const first = mounts[0] ?? {};
  const id = first.problemId || `step${st.stepIdx}-prob${st.probIdx}`;
  if (first.problemId) seenIds.add(first.problemId);
  const record = {
    probKey,
    id,
    atoms: mounts.map((m) => m.key),
    mode: mounts.every((m) => !m.terminal || UI[m.key]) ? 'ui' : 'flow-only',
    tests: {},
    shots: [],
  };
  results.problems.push(record);

  /* 문제에 **도입 연출**이 있으면(대사 → `다음` → 그제서야 입력 영역이 보인다) 그것부터 넘긴다.
     실측(2026-09-30, 4-1/03) — 사람이 Q-01 에 도입 대사를 넣자, 도구가 안 보이는 키패드를 누르다 "정답을 냈는데
     안 넘어간다" 로 오판했고 뒤 문항이 전부 미도달로 잡혔다. 입력 영역이 실제로 보일 때까지 `다음` 을 누른다. */
  const firstTerminal = mounts.find((m) => m.terminal);
  if (firstTerminal) {
    for (let i = 0; i < 12; i += 1) {
      const visible = await page.evaluate((index) => {
        const host = document.querySelector(`[data-qa-mount="${index}"]`);
        if (!host) return false;
        const r = host.getBoundingClientRect();
        let opacity = 1;
        for (let n = host; n; n = n.parentElement) opacity *= Number(getComputedStyle(n).opacity || 1);
        return r.width > 2 && r.height > 2 && opacity > 0.5 && getComputedStyle(host).visibility !== 'hidden';
      }, firstTerminal.index);
      if (visible) break;
      if (i === 0) record.shots.push(await shot(`${id}-intro`));
      const next = await page.evaluate(FIND_NEXT, NEXT_SELECTORS);
      if (next) await press(page.locator(next).first(), `${id} 도입 ${next}`);
      await page.waitForTimeout(900);
    }
  }
  record.shots.push(await shot(`${id}-before`));

  if (!mounts.some((m) => m.terminal)) {
    record.tests.correct = { status: 'fail', detail: '채점하는 원자가 없다 — 이 문제는 끝낼 수 없다' };
    return;
  }

  /* 오답 → 그 자리에 남는가(재시도). 힌트가 있으면 그 횟수만큼 더 틀려 본다. */
  const hint = first.hintAfterWrong;
  const wrongTimes = hint ? Math.max(1, Number(hint.count) || 2) : 1;
  let retry = { status: 'pass', detail: '' };
  for (let i = 0; i < wrongTimes; i += 1) {
    const before = await state();
    const res = await answer(mounts, false);
    if (res.skipped) { retry = { status: 'skip', detail: `오답을 만들 수 없다: ${res.skipped}` }; break; }
    await page.waitForTimeout(250);
    if (i === 0) record.shots.push(await shot(`${id}-wrong`));
    await page.waitForTimeout(1200);
    const after = await state();
    if (after.probIdx !== before.probIdx || after.stepIdx !== before.stepIdx || !after.panel) {
      retry = { status: 'fail', detail: `오답을 냈는데 문제를 벗어났다 (${before.stepIdx}:${before.probIdx} → ${after.stepIdx}:${after.probIdx})` };
      break;
    }
    if (after.correct !== before.correct) {
      retry = { status: 'fail', detail: '오답을 냈는데 점수가 올랐다' };
      break;
    }
  }
  record.tests.retry = retry;
  if (retry.status === 'fail') return;

  if (hint) {
    const st2 = await state();
    record.tests.hint = st2.hint
      ? { status: 'pass', detail: `${wrongTimes}번 틀린 뒤 힌트가 떴다` }
      : { status: 'fail', detail: `hintAfterWrong 이 있는데 ${wrongTimes}번 틀려도 힌트가 안 떴다` };
    record.shots.push(await shot(`${id}-hint`));
  }

  /* 정답 → 점수가 오르거나 다음 문제로 넘어가는가. */
  const before = await state();
  const res = await answer(mounts, true);
  if (res.skipped) {
    record.tests.correct = { status: 'skip', detail: res.skipped };
    return;
  }
  record.mode = res.mode;
  await page.waitForTimeout(300);
  record.shots.push(await shot(`${id}-correct`));
  let after = before;
  for (let t = 0; t < 12; t += 1) {
    await page.waitForTimeout(500);
    after = await state();
    if (after.correct > before.correct || after.probIdx !== before.probIdx || after.stepIdx !== before.stepIdx) break;
  }
  const accepted = after.correct > before.correct;
  const moved = after.probIdx !== before.probIdx || after.stepIdx !== before.stepIdx;
  record.tests.correct = accepted || moved
    ? { status: 'pass', detail: accepted ? '정답 인정(점수 +1)' : '다음으로 넘어갔다(점수 미집계 문제)' }
    : { status: 'fail', detail: '정답을 냈는데 점수도 안 오르고 다음으로도 안 넘어간다' };
}

/* 끝 화면과 인증서. 인증서는 완료 화면의 버튼을 눌러야 열린다 — 안 누르면 어느 캡처에도 없다. */
async function shotEnd(st) {
  await shot(`end-${st.stepId || 'last'}`);
  const cert = page.locator('button, .cta, [role="button"], a').filter({ hasText: /인증서/ });
  const count = await cert.count();
  if (!count) {
    results.click_notes.push('완료 화면에서 인증서 버튼을 못 찾았다 — 인증서 화면은 안 찍혔다');
    return;
  }
  await press(cert.first(), '인증서 받기');
  await page.waitForTimeout(1800);
  await shot('certificate');
}

/* ── 걷기 ─────────────────────────────────────────────────────────────── */
try {
  await page.goto(url, { waitUntil: 'networkidle' }).catch(() => {});
  await page.waitForTimeout(1200);
  if (!(await page.$('#app'))) {
    console.error(`화면이 뜨지 않았다: ${url}`);
    await browser.close();
    process.exit(2);
  }
  if (!(await page.evaluate(HOOK))) {
    console.error('PROBLEM_ATOMS 에 닿지 못했다 — 런타임 구조가 바뀌었을 수 있다');
    await browser.close();
    process.exit(2);
  }

  const tested = new Set();
  let lastKey = '';
  let sameRuns = 0;
  let idleRetries = 0;   // 화면 전환을 기다려 준 횟수(전체)
  for (let loop = 0; loop < 400; loop += 1) {
    await page.evaluate(WRAP);
    const st = await state();
    note(st);

    if (st.panel && st.mounts > 0) {
      const probKey = `${st.stepIdx}:${st.probIdx}`;
      const has = (await mountsFor(probKey)).length > 0;
      if (has && !tested.has(probKey)) {
        tested.add(probKey);
        await testProblem(st);
        lastKey = '';
        sameRuns = 0;
        continue;
      }
    }

    // 넘어가는 버튼이 나타날 때까지 기다린다 — 이야기 카드는 10초 뒤에 버튼이 뜬다.
    let next = '';
    for (let wait = 0; wait < 26 && !next; wait += 1) {
      next = await page.evaluate(FIND_NEXT, NEXT_SELECTORS);
      if (!next) {
        const peek = await state();
        if (peek.panel && !tested.has(`${peek.stepIdx}:${peek.probIdx}`)) break;
        await page.waitForTimeout(500);
      }
    }
    /* 버튼은 있는데 **조상이 투명**해서 못 찾는 경우가 있다 — 화면 전환 애니메이션(`stage-fade-in`)이
       끝나지 않고 `#app` 이 opacity 0 에 머문 것이다. 실측(2026-09-29, 4-1/04) — 같은 자리에서 3번 중
       2번 그랬다. 조금 더 기다려 보고, 그래도 그대로면 "끝" 이 아니라 **진행 막힘**으로 적는다.
       조용히 끝으로 처리하면 뒤 문항이 전부 "미도달" 로 잘못 보고된다. */
    if (!next) {
      const hiddenByFade = () => page.evaluate((selectors) => selectors.some((sel) =>
        [...document.querySelectorAll(sel)].some((el) => {
          const r = el.getBoundingClientRect();
          if (r.width < 2 || getComputedStyle(el).display === 'none' || el.disabled) return false;
          let o = 1;
          for (let n = el; n; n = n.parentElement) o *= Number(getComputedStyle(n).opacity || 1);
          return o < 0.5;
        })), NEXT_SELECTORS);
      for (let retry = 0; retry < 3 && !next && await hiddenByFade(); retry += 1) {
        await page.waitForTimeout(2000);
        next = await page.evaluate(FIND_NEXT, NEXT_SELECTORS);
      }
      if (!next && await hiddenByFade()) {
        results.stuck = true;
        results.stuck_detail = '넘어가는 버튼이 투명한 채로 남았다 — 화면 전환(stage-fade)이 끝나지 않아 '
          + `화면이 보이지 않는다: ${st.mode}`;
        await shot('stuck-transparent');
        break;
      }
    }
    /* 포기하기 전에 **화면 전환이 막 시작됐는지** 본다. 스스로 넘어가는 컷이 있는 차시에서는 버튼을 13초
       찾다 포기하는 바로 그 순간에 다음 장면의 페이드인이 시작된다 — 실측(2026-09-29, 4-1/04) 멈춘 자리에서
       `stageFadeIn` 이 t=0 이었고 0.5초 뒤 opacity 1 이었다. 전환이 돌고 있으면 끝날 때까지 기다리고 다시 찾는다. */
    if (!next && idleRetries < 6) {
      const animating = await page.evaluate(() => document.getAnimations()
        .some((a) => a.playState === 'running' && a.effect && a.effect.target === document.getElementById('app')));
      if (animating) {
        idleRetries += 1;
        await page.waitForTimeout(1500);
        continue;
      }
    }
    if (!next) {
      const peek = await state();
      if (peek.panel && !tested.has(`${peek.stepIdx}:${peek.probIdx}`)) continue;
      results.ended = `더 누를 버튼이 없다: ${peek.mode} · ${peek.text}`;
      // 화면 전환 애니메이션이 **멈춘 것인지, 계속 다시 시작되는 것인지** 가른다. 1.5초 동안 #app 의
      // opacity 와 돌고 있는 애니메이션을 잰다. 다시 시작되면 currentTime 이 계속 0 근처로 돌아간다.
      results.stop_animations = [];
      for (let sample = 0; sample < 4; sample += 1) {
        results.stop_animations.push(await page.evaluate(() => ({
          appOpacity: getComputedStyle(document.getElementById('app')).opacity,
          appClass: document.getElementById('app').className,
          animations: document.getAnimations().slice(0, 6).map((a) => ({
            name: a.animationName || a.transitionProperty || a.constructor.name,
            state: a.playState,
            t: Math.round(a.currentTime ?? -1),
            target: (() => { const el = a.effect && a.effect.target; return el ? `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}` : '?'; })(),
          })),
        })));
        await page.waitForTimeout(500);
      }
      // 왜 못 눌렀는지 남긴다 — 버튼이 없는 것인지, 있는데 가려졌거나 투명한 것인지.
      results.stop_diagnosis = await page.evaluate((selectors) => selectors.flatMap((sel) =>
        [...document.querySelectorAll(sel)].map((el) => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const top = r.width ? document.elementFromPoint(cx, cy) : null;
          let chainOpacity = 1;
          const faded = [];
          for (let n = el; n; n = n.parentElement) {
            const o = Number(getComputedStyle(n).opacity || 1);
            chainOpacity *= o;
            if (o < 1) faded.push(`${n.tagName.toLowerCase()}${n.id ? '#' + n.id : ''}.${[...n.classList].join('.')} opacity=${o}`);
          }
          return {
            sel, text: (el.innerText || '').trim().slice(0, 20), w: Math.round(r.width), h: Math.round(r.height),
            display: s.display, visibility: s.visibility, opacity: s.opacity, chainOpacity: Number(chainOpacity.toFixed(2)),
            pointerEvents: s.pointerEvents, disabled: !!el.disabled, hidden: !!el.hidden,
            coveredBy: top && top !== el && !el.contains(top) ? `${top.tagName.toLowerCase()}.${[...top.classList].join('.')}` : '',
            fadedAncestors: faded,
          };
        })), NEXT_SELECTORS);
      await shotEnd(peek);
      break;
    }

    const key = `${st.stepIdx}:${st.probIdx}|${st.mode}|${st.text}`;
    // 누르기 전에 이 화면을 찍는다. 버튼이 뜬 뒤라 이야기 카드도 다 읽힌 상태다.
    // 문제를 푼 뒤에도 패널이 DOM 에 남은 채 대사 컷이 뜬다. 이미 푼 문제의 패널은 "문제 화면" 이 아니다.
    const screenKey = `${st.stepIdx}|${st.cutId}|${st.slide}|${st.speech}|${st.text}`;
    const onOpenProblem = st.panel && !tested.has(`${st.stepIdx}:${st.probIdx}`);
    if (!onOpenProblem && !shotScreens.has(screenKey)) {
      shotScreens.add(screenKey);
      // 이야기 카드 뒤에는 앞 대사가 깔려 있어 cutId 가 그 대사를 가리킨다. 카드면 카드 번호로 부른다.
      await shot(st.story ? `story-${st.slide + 1}` : (st.cutId || st.stepId || `step${st.stepIdx}`));
    }
    sameRuns = key === lastKey ? sameRuns + 1 : 0;
    lastKey = key;
    if (sameRuns >= 5) {
      /* 마지막 스텝의 완료 화면에는 `나가기`·`다음 차시`·`인증서 받기` 처럼 **이 차시 밖으로**
         나가는 버튼만 남는다. 눌러도 화면이 그대로인 것이 정상이다 — 멈춤이 아니라 끝이다. */
      if (st.lastStep && !st.panel) {
        results.ended = `마지막 스텝에 닿았다: ${st.text}`;
        await shotEnd(st);
        break;
      }
      results.stuck = true;
      results.stuck_detail = `"${next}" 를 ${sameRuns}번 눌러도 화면이 그대로다: ${st.text}`;
      await shot('stuck');
      break;
    }
    await press(page.locator(next).first(), next);
    await page.waitForTimeout(700);
  }
} catch (error) {
  results.page_errors.push(`automation: ${String(error?.stack || error).slice(0, 400)}`);
  await shot('automation-stopped').catch(() => {});
} finally {
  results.seen_ids = [...seenIds].sort();
  writeFileSync(join(outDir, 'functional-results.json'), JSON.stringify(results, null, 2));
  await browser.close();
}

const failed = results.problems.flatMap((p) => Object.entries(p.tests)
  .filter(([, t]) => t.status === 'fail').map(([name, t]) => `${p.id} ${name}: ${t.detail}`));
console.log(`문항 ${results.problems.length}개 · 실패 ${failed.length}건${results.stuck ? ' · 진행 멈춤' : ''}`);
for (const line of failed) console.log(`  ✗ ${line}`);
if (results.stuck) console.log(`  ✗ ${results.stuck_detail}`);
process.exit(failed.length || results.stuck ? 1 : 0);
