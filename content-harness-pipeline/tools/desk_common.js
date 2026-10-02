// 차시 작업대(/)와 초안 파이프라인(/pipeline)이 함께 쓰는 것 — 글자 처리 · 토큰 단위 · AI 모델 고르기.
// 두 화면에 같은 코드가 복사돼 있던 것을 모았다(2026-10-01 정리). 페이지 스크립트보다 먼저, #models 가 생긴 뒤에 싣는다.

function esc(s) { return String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
function time(s) { return s ? s.slice(5, 16).replace("T", " ") : ""; }
// 토큰은 단위로 줄여 소수 첫째 자리까지(사용자 요청 2026-09-30) — 1a = 1토큰, 1b = 1,000a, 1c = 1,000b, 1d = 1,000c
function tok(n) {
  if (n == null) return "-";
  const units = ["a", "b", "c", "d", "e"];
  let v = Number(n), i = 0;
  while (Math.abs(v) >= 1000 && i < units.length - 1) { v /= 1000; i++; }
  if (Number(v.toFixed(1)) >= 1000 && i < units.length - 1) { v /= 1000; i++; }  // 999.96b → 1000.0b 가 아니라 1.0c
  return v.toFixed(1) + units[i];
}
async function postJson(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json", "X-Desk": "1" }, body: JSON.stringify(body) });
  return { res, data: await res.json().catch(() => ({})) };
}

// ── 음성 파일 넣기(2026-10-01 사용자 요청) — 차시 작업대 카드와 초안 파이프라인 화면이 같이 쓴다 ──
// 대사 한 줄마다 따로 받은 파일을 올리면 서버가 자동으로 짝짓고(이름 속 대사 글자 → 번호·순서), 여기서 줄마다 들어 보고
// 바꾼 뒤 [넣기]. target = { lesson } 또는 { run_id }. 사람이 바꾼 짝은 box._edits 에 두어 다시 그려도 남긴다
const voicePlayer = new Audio();
function voiceAudioUrl(target, params) {
  const t = target.lesson ? `lesson=${encodeURIComponent(target.lesson)}` : `run=${encodeURIComponent(target.run_id)}`;
  return `/api/voice/audio?${t}&` + Object.entries(params).map(([k, v]) => `${k}=${encodeURIComponent(v)}`).join("&");
}
function renderVoice(box, target, voice, refresh) {
  if (!box.dataset.wired) wireVoice(box, refresh);
  box._target = target;
  box._voice = voice;
  const sig = JSON.stringify([target, voice]);
  if (box.dataset.sig === sig) return;
  if (box.contains(document.activeElement) && document.activeElement.matches("select.v-file")) return;   // 고르는 중
  box.dataset.sig = sig;
  const open = box.querySelector("details.voice")?.open ?? !!(voice && voice.status === "ready");
  const edits = (voice && box._edits?.[voice.id]) || {};
  let body = "";
  if (voice && voice.status === "ready") {
    const pairs = voice.pairs || {};
    const pick = r => r.key in edits ? edits[r.key] : (pairs[r.key]?.file || "");
    const used = new Set(voice.rows.map(pick).filter(Boolean));
    const n = voice.rows.filter(r => pick(r)).length;
    const leftover = voice.files.filter(f => !used.has(f));
    body = `<p class="meta">${voice.mode === "all" ? "교체 포함(모든 대사)" : "빈 대사만"} · 올린 파일 ${voice.files.length}개 · 짝지은 대사 ${n}줄
        ${leftover.length ? ` · <b>짝 없는 파일 ${leftover.length}</b>: ${esc(leftover.join(", "))}` : ""}</p>
      <div class="table-wrap"><table class="v-table"><tr><th>#</th><th class="l">누가</th><th class="l">대사</th><th class="l">지금 소리</th><th class="l">새 파일</th></tr>
      ${voice.rows.map((r, i) => {
        const f = pick(r), how = r.key in edits ? "직접" : (pairs[r.key]?.method || "");
        return `<tr data-key="${esc(r.key)}"><td>${i + 1}</td><td class="l">${esc(r.speaker_name)}</td><td class="l v-text">${esc(r.text)}</td>
          <td class="l">${r.current ? `${r.current_path ? `<button class="v-play" data-current="${esc(r.current_path)}" title="지금 걸린 소리 듣기">▶</button> ` : ""}<span class="meta">${esc(r.current)}</span>` : `<span class="meta">없음</span>`}</td>
          <td class="l"><select class="v-file"><option value="">— 넣지 않음 —</option>${voice.files.map(x => `<option${x === f ? " selected" : ""}>${esc(x)}</option>`).join("")}</select>
            ${f ? `<button class="v-play" data-file="${esc(f)}" title="새 파일 듣기">▶</button>` : ""}
            ${how ? `<span class="v-how v-how-${how === "순서" ? "order" : "ok"}">${esc(how)}</span>` : ""}</td></tr>`;
      }).join("")}</table></div>
      <div class="v-acts"><button class="primary v-apply">넣기 (${n})</button><button class="v-discard">버리기</button>
        <span class="meta">'순서'로 짝지은 줄은 꼭 들어 보세요 · 교체된 예전 파일은 보관 폴더로 옮깁니다${target.lesson ? " · 넣으면 바로 빌드합니다" : " · gyo6 에는 [gyo6에 넣기]로 반영"}</span></div>`;
  } else if (voice && voice.status === "applied") {
    const moved = (voice.moved || []).length;
    body = `<p class="meta">마지막으로 넣음: ${Object.keys(voice.applied || {}).length}줄${moved ? ` · 예전 파일 ${moved}개 보관` : ""} — 새 파일을 올리면 다시 짝짓습니다</p>`;
  }
  box.innerHTML = `<details class="voice"${open ? " open" : ""}><summary><b>음성 파일 넣기</b>${voice && voice.status === "ready" ? " — 확인하고 넣을 차례" : ""}</summary>
    <div class="v-up"><select class="v-mode"><option value="empty">빈 대사만 채우기</option><option value="all">교체 포함(모든 대사)</option></select>
      <input type="file" class="v-files" multiple accept="audio/*,.mp3,.wav,.ogg,.m4a">
      <button class="v-send">올려서 짝짓기</button>
      <span class="meta">대사 한 줄마다 따로 받은 파일 여러 개를 한꺼번에</span></div>${body}</details>`;
}
function wireVoice(box, refresh) {
  box.dataset.wired = "1";
  box._edits = {};
  const msg = text => { let m = box.querySelector(".v-msg"); if (!m) { m = document.createElement("p"); m.className = "v-msg err"; box.querySelector("details")?.appendChild(m); } m.textContent = text; };
  const send = async (path, extra) => {
    const { res, data } = await postJson(path, { ...box._target, ...extra });
    if (!res.ok) { msg(data.error || "요청 실패"); return null; }
    box.dataset.sig = ""; refresh(); return data;
  };
  box.addEventListener("change", e => {
    const s = e.target.closest("select.v-file");
    if (!s || !box._voice) return;
    (box._edits[box._voice.id] ||= {})[s.closest("tr").dataset.key] = s.value;
    s.blur(); box.dataset.sig = ""; renderVoice(box, box._target, box._voice, refresh);
  });
  box.addEventListener("click", async e => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.matches(".v-play")) {
      voicePlayer.src = b.dataset.file ? voiceAudioUrl(box._target, { session: box._voice.id, file: b.dataset.file })
                                       : voiceAudioUrl(box._target, { current: b.dataset.current });
      voicePlayer.play().catch(() => msg("재생하지 못했습니다"));
    } else if (b.matches(".v-send")) {
      const files = [...box.querySelector(".v-files").files];
      if (!files.length) return msg("음성 파일을 먼저 고르세요");
      b.disabled = true; b.textContent = "올리는 중…";
      const read = f => new Promise((ok, no) => { const rd = new FileReader(); rd.onload = () => ok({ name: f.name, data: rd.result }); rd.onerror = no; rd.readAsDataURL(f); });
      await send("/api/voice/upload", { mode: box.querySelector(".v-mode").value, files: await Promise.all(files.map(read)) });
      b.disabled = false; b.textContent = "올려서 짝짓기";
    } else if (b.matches(".v-apply")) {
      const v = box._voice, edits = box._edits[v.id] || {};
      const pairs = Object.fromEntries(v.rows.map(r => [r.key, r.key in edits ? edits[r.key] : (v.pairs[r.key]?.file || "")]));
      const n = Object.values(pairs).filter(Boolean).length;
      if (!n) return msg("넣을 짝이 없습니다");
      if (!confirm(`${n}줄에 음성을 넣을까요?`)) return;
      const r = await send("/api/voice/apply", { session: v.id, pairs });
      if (r) { delete box._edits[v.id]; msg(`넣었습니다 — ${r.placed}줄${r.replaced ? ` (교체 ${r.replaced})` : ""}${r.moved?.length ? ` · 예전 파일 ${r.moved.length}개 보관` : ""}`); }
    } else if (b.matches(".v-discard")) {
      if (confirm("이 음성 세션을 버릴까요? (올린 파일은 보관 폴더에 남습니다)")) send("/api/voice/discard", { session: box._voice.id });
    }
  });
}

// 서버 코드가 켠 뒤에 바뀌었으면 맨 위에 띠를 띄운다 — 화면만 새것이고 서버는 예전 것이면 화면이 깨진다
// (problem.md [desk-page-server-version-skew]). 페이지는 상태를 받을 때마다 restartNeeded 값을 넘긴다
function showRestartBanner(on) {
  let bar = document.getElementById("restart-banner");
  if (!on) { bar?.remove(); return; }
  if (bar) return;
  bar = document.createElement("div");
  bar.id = "restart-banner";
  bar.className = "restart-banner";
  bar.textContent = "작업대 코드가 바뀌었습니다 — 바탕화면 「차시 작업대」를 다시 누르면 새 코드로 켭니다(도는 작업이 있으면 먼저 묻습니다).";
  document.body.prepend(bar);
}

// ── AI 모델 · 추론 강도 고르기(사이드바 아래) — 두 화면 공용 설정, 다음 작업부터 적용 ──
// 목록은 각 CLI 가 받아 둔 것(클로드: ~/.claude/cache/model-catalog · 코덱스: ~/.codex/models_cache.json)을 서버가 읽어 준다.
// 페이지는 상태를 받을 때마다 renderModels(state.models) 만 부른다
// 접었다 폈다(2026-10-02 사용자 요청) — 기본은 접힘, 접힌 줄에 지금 고른 것을 짧게 보이고, 펼친 상태는 브라우저에 기억한다
document.getElementById("models").innerHTML = `
  <details class="mfold" id="m-fold">
    <summary><span class="mtitle">AI 모델</span><span class="mpicked" id="m-picked"></span></summary>
    <div class="mbody">
    <label>클로드 <span class="mnote">코드 메모 · 초안의 기획~개발</span><select id="m-claude"></select></label>
    <input id="m-claude-custom" class="hidden" placeholder="클로드 모델 이름 (Enter 로 저장)" spellcheck="false">
    <label>추론 강도<select id="m-claude-effort"></select></label>
    <label>코덱스 <span class="mnote">그림·검증 메모 · 초안의 그림 굽기</span><select id="m-codex"></select></label>
    <input id="m-codex-custom" class="hidden" placeholder="코덱스 모델 이름 (Enter 로 저장)" spellcheck="false">
    <label>추론 강도<select id="m-codex-effort"></select></label>
    <p class="mnote">두 화면 공용 · 다음 작업부터 적용 · 도는 작업은 그대로</p>
    <span class="mmsg" id="m-msg"></span>
    </div>
  </details>`;
{
  const fold = document.getElementById("m-fold");
  try { fold.open = localStorage.getItem("desk.models.open") === "1"; } catch { /* 저장소를 못 쓰면 접힌 채로 */ }
  fold.addEventListener("toggle", () => { try { localStorage.setItem("desk.models.open", fold.open ? "1" : "0"); } catch { /* 무시 */ } });
}

let modelState = null;
const effortName = e => (modelState && modelState.effort_label[e]) || e;
function modelInfo(which, id) {
  const list = which === "claude" ? modelState.claude_models : modelState.codex_models;
  const key = id || (which === "codex" ? modelState.codex_default : "");
  return list.find(x => x.id === key) || null;
}
function fillModel(which, value, list, defaultLabel) {
  const sel = document.getElementById(`m-${which}`), custom = document.getElementById(`m-${which}-custom`);
  const known = list.some(x => x.id === value);
  const opt = x => `<option value="${esc(x.id)}">${esc(x.name)}</option>`;
  const main = list.filter(x => x.main), rest = list.filter(x => !x.main);
  const html = `<option value="">${esc(defaultLabel)}</option>`
    + (rest.length ? `<optgroup label="주 모델">${main.map(opt).join("")}</optgroup><optgroup label="그 밖의 버전">${rest.map(opt).join("")}</optgroup>`
                   : main.map(opt).join(""))
    + `<option value="__custom__">직접 입력…</option>`;
  if (sel.dataset.sig !== html) { sel.innerHTML = html; sel.dataset.sig = html; }
  sel.value = value && !known ? "__custom__" : value;
  custom.classList.toggle("hidden", !(value && !known));
  if (value && !known) custom.value = value;
}
function fillEffort(which, model, effort, cliDefault) {
  const sel = document.getElementById(`m-${which}-effort`);
  const info = modelInfo(which, model);
  const efforts = info ? info.efforts : ["low", "medium", "high", "xhigh", "max"];
  let first = "기본";
  if (info && info.recommended) first = `기본 (추천: ${effortName(info.recommended)})`;
  else if (cliDefault && !model) first = `기본 (CLI 설정: ${effortName(cliDefault)})`;
  const html = efforts.length ? `<option value="">${esc(first)}</option>` + efforts.map(e => `<option value="${e}">${esc(effortName(e))}</option>`).join("")
                              : `<option value="">이 모델은 추론 강도가 없습니다</option>`;
  if (sel.dataset.sig !== html) { sel.innerHTML = html; sel.dataset.sig = html; }
  sel.disabled = !efforts.length;
  sel.value = efforts.includes(effort) ? effort : "";
}
function renderModels(m) {
  if (!m) return;
  modelState = m;
  // 사람이 고르는 중인 칸은 새로고침이 덮지 않는다
  const picking = which => [`m-${which}`, `m-${which}-custom`, `m-${which}-effort`].some(x => document.activeElement === document.getElementById(x));
  if (!picking("claude")) {
    fillModel("claude", m.claude, m.claude_models, "기본 (CLI 설정)");
    fillEffort("claude", m.claude, m.claude_effort, "");
  }
  if (!picking("codex")) {
    fillModel("codex", m.codex, m.codex_models, m.codex_default ? `기본 (CLI 설정: ${m.codex_default})` : "기본 (CLI 설정)");
    fillEffort("codex", m.codex, m.codex_effort, m.codex_default_effort);
  }
  // 접힌 줄에 보이는 지금 설정 — 펼치지 않아도 무엇으로 도는지 안다
  const picked = which => {
    const info = m[which] ? modelInfo(which, m[which]) : null;
    const effort = m[`${which}_effort`] ? ` · ${effortName(m[`${which}_effort`])}` : "";
    return `${(info ? info.name : m[which]) || "기본"}${effort}`;
  };
  const line = document.getElementById("m-picked");
  line.textContent = `클로드 ${picked("claude")} / 코덱스 ${picked("codex")}`;
  line.title = line.textContent;
}
async function saveModels(patch) {
  const s = modelState || {};
  const body = { claude: s.claude || "", codex: s.codex || "", claude_effort: s.claude_effort || "", codex_effort: s.codex_effort || "", ...patch };
  // 모델을 바꿨는데 고른 강도를 그 모델이 지원하지 않으면 '기본'으로 되돌린다
  for (const which of ["claude", "codex"]) {
    const info = modelState && modelInfo(which, body[which]);
    if (info && body[`${which}_effort`] && !info.efforts.includes(body[`${which}_effort`])) body[`${which}_effort`] = "";
  }
  const { res, data } = await postJson("/api/models", body);
  const msg = document.getElementById("m-msg");
  if (!res.ok) { msg.style.color = "var(--bad)"; msg.textContent = data.error || "저장 실패"; return; }
  const name = which => { const i = modelInfo(which, body[which]); return (i ? i.name : body[which]) || "기본"; };
  const effort = which => body[`${which}_effort`] ? effortName(body[`${which}_effort`]) : "기본";
  msg.style.color = "";
  msg.textContent = `저장함 — 클로드: ${name("claude")} · ${effort("claude")} / 코덱스: ${name("codex")} · ${effort("codex")}`;
  document.activeElement && document.activeElement.blur();
  renderModels(data.models);
}
for (const which of ["claude", "codex"]) {
  const sel = document.getElementById(`m-${which}`), custom = document.getElementById(`m-${which}-custom`);
  sel.addEventListener("change", () => {
    if (sel.value === "__custom__") { custom.classList.remove("hidden"); custom.focus(); return; }
    custom.classList.add("hidden");
    saveModels({ [which]: sel.value });
  });
  custom.addEventListener("keydown", e => { if (e.key === "Enter" && custom.value.trim()) saveModels({ [which]: custom.value.trim() }); });
  document.getElementById(`m-${which}-effort`).addEventListener("change", e => saveModels({ [`${which}_effort`]: e.target.value }));
}
