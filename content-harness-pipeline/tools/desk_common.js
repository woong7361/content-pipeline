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
  if (box.dataset.sig) loadVoiceLinks(box);   // 넣기 · 버리기로 세션이 바뀌면 연결도 바뀌었을 수 있다(펼쳐 있을 때만 다시 읽는다)
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
  box.querySelector(".v-import").innerHTML = `<details class="voice"${open ? " open" : ""}><summary><b>음성 파일 넣기</b>${voice && voice.status === "ready" ? " — 확인하고 넣을 차례" : ""}</summary>
    <div class="v-up"><select class="v-mode"><option value="empty">빈 대사만 채우기</option><option value="all">교체 포함(모든 대사)</option></select>
      <input type="file" class="v-files" multiple accept="audio/*,.mp3,.wav,.ogg,.m4a">
      <button class="v-send">올려서 짝짓기</button>
      <span class="meta">대사 한 줄마다 따로 받은 파일 여러 개를 한꺼번에</span></div>${body}</details>`;
}
// 대사 ↔ 음성 연결 보기(2026-10-06 사용자 요청) — 파일을 넣지 않아도 지금 lesson.json 에 걸린 소리를 본다.
// 넣기 칸과 따로 그려 2초 새로고침에 닫히지 않게 하고, 펼칠 때만 서버에서 읽는다.
// 줄마다 [넣기]/[바꾸기]로 그 줄에 파일 하나를 바로 건다(같은 날 사용자 요청, /api/voice/put). 이야기 카드 조각은 조각마다
const VOICE_KIND = { cut: "컷", problem: "문제", hint: "힌트", slide: "이야기 카드" };
async function loadVoiceLinks(box) {
  const holder = box.querySelector(".v-links");
  if (!holder?.open || !box._target) return;
  const t = box._target.lesson ? `lesson=${encodeURIComponent(box._target.lesson)}` : `run=${encodeURIComponent(box._target.run_id)}`;
  const body = holder.querySelector(".v-links-body");
  const data = await fetch(`/api/voice/lines?${t}`).then(r => r.json()).catch(() => ({ error: "읽지 못했습니다" }));
  if (data.error) { body.innerHTML = `<p class="err">${esc(data.error)}</p>`; return; }
  const rows = data.rows || [];
  box._linkRows = rows;
  const put = (i, k, label) => `<button class="v-put" data-row="${i}"${k == null ? "" : ` data-piece="${k}"`} title="이 자리에 음성 파일 넣기">${label}</button>`;
  const has = rows.filter(r => r.current).length;
  const broken = rows.filter(r => r.sequence ? r.sequence.some(s => !s.exists) : r.current && !r.exists).length;
  body.innerHTML = `<p class="meta">대사 ${rows.length}줄 · 소리 걸림 <b>${has}</b> · 없음 <b>${rows.length - has}</b>${broken ? ` · <b class="err">파일 없음 ${broken}</b>` : ""}</p>
    <div class="table-wrap"><table class="v-table"><tr><th>#</th><th class="l">자리</th><th class="l">누가</th><th class="l">대사</th><th class="l">소리</th></tr>
    ${rows.map((r, i) => `<tr class="${r.current ? "" : "v-none"}"><td>${i + 1}</td><td class="l">${esc(VOICE_KIND[r.kind] || r.kind)}</td>
      <td class="l">${esc(r.speaker_name)}</td><td class="l v-text">${esc(r.text)}</td>
      <td class="l${r.sequence ? "" : " v-drop"}" data-row="${i}">${r.sequence ? `<span class="meta">이어서 ${r.sequence.length}개</span>` + r.sequence.map((s, k) => s.exists
          ? `<div class="v-drop" data-row="${i}" data-piece="${k}">${k + 1}. <button class="v-play" data-current="${esc(s.path)}" title="듣기">▶</button> <span class="meta">${esc(s.id)}</span> ${put(i, k, "바꾸기")}</div>`
          : `<div class="v-drop" data-row="${i}" data-piece="${k}">${k + 1}. <span class="err">${esc(s.id)} — 파일 없음</span> ${put(i, k, "넣기")}</div>`).join("")
        : !r.current ? `<span class="meta">없음</span> ${put(i, null, "넣기")}`
        : r.exists ? `<button class="v-play" data-current="${esc(r.current_path)}" title="듣기">▶</button> <span class="meta">${esc(r.current)}</span> ${put(i, null, "바꾸기")}`
        : `<span class="err">${esc(r.current)} — 파일 없음</span> <span class="meta">${esc(r.current_path || "audioMap 에 없음")}</span> ${put(i, null, "넣기")}`}</td></tr>`).join("")}</table></div>
    ${(data.skipped || []).length ? `<details><summary class="meta">소리를 재생하지 않는 자리 ${data.skipped.length}곳</summary><ul class="meta">${data.skipped.map(s => `<li>${esc(s)}</li>`).join("")}</ul></details>` : ""}`;
}
function wireVoice(box, refresh) {
  box.dataset.wired = "1";
  box._edits = {};
  box.innerHTML = `<div class="v-import"></div><details class="voice v-links"><summary><b>대사 · 음성 연결 보기</b></summary>
    <p class="meta">줄마다 [넣기]·[바꾸기]로, 또는 소리 칸에 파일을 끌어 놓아 바로 겁니다 — 빌드는 하지 않으니 다 넣은 뒤 [빌드]. 바뀐 예전 파일은 보관 폴더로 옮깁니다</p>
    <p class="v-links-msg meta"></p><input type="file" class="v-put-file" accept="audio/*,.mp3,.wav,.ogg,.m4a" style="display:none">
    <div class="v-links-body"><p class="meta">읽는 중…</p></div></details>`;
  box.querySelector(".v-links").addEventListener("toggle", () => loadVoiceLinks(box));
  const putFile = box.querySelector(".v-put-file");
  putFile.addEventListener("change", () => putVoice(box._put, putFile.files[0]));
  // 끌어 놓기 — 소리 칸(조각이면 그 조각 줄)에 놓는다. 칸 밖에 놓아도 브라우저가 파일을 열고 화면을 떠나지 않게 막는다
  const links = box.querySelector(".v-links");
  const zoneOf = e => e.target.closest?.(".v-drop");
  const lit = z => links.querySelectorAll(".v-drop.v-over").forEach(el => el !== z && el.classList.remove("v-over"));
  links.addEventListener("dragover", e => {
    if (![...(e.dataTransfer?.types || [])].includes("Files")) return;
    e.preventDefault();
    const z = zoneOf(e);
    e.dataTransfer.dropEffect = z ? "copy" : "none";
    lit(z); z?.classList.add("v-over");
  });
  links.addEventListener("dragleave", e => { if (!links.contains(e.relatedTarget)) lit(null); });
  links.addEventListener("drop", e => {
    if (![...(e.dataTransfer?.types || [])].includes("Files")) return;
    e.preventDefault();
    lit(null);
    const z = zoneOf(e), files = [...e.dataTransfer.files];
    if (!z) return;
    if (files.length !== 1) { const n = box.querySelector(".v-links-msg"); n.className = "v-links-msg err"; n.textContent = "한 칸에 파일 하나만 놓습니다"; return; }
    putVoice({ row: Number(z.dataset.row), piece: z.dataset.piece == null ? null : Number(z.dataset.piece) }, files[0]);
  });
  async function putVoice(at, f) {
    const note = box.querySelector(".v-links-msg");
    if (!f || !at) return;
    if (!/\.(mp3|wav|ogg|m4a)$/i.test(f.name)) { note.className = "v-links-msg err"; note.textContent = `음성 파일이 아닙니다: ${f.name} (mp3 · wav · ogg · m4a)`; return; }
    const row = box._linkRows[at.row], piece = at.piece == null ? null : row.sequence[at.piece];
    const where = piece ? `${row.text.split("\n")[0]} — 조각 ${at.piece + 1}(${piece.id})` : row.text.split("\n")[0];
    if ((piece || row.current) && !confirm(`「${where}」의 소리를 ${f.name} 로 바꿀까요?`)) return;
    note.textContent = `넣는 중… ${f.name}`;
    const data = await new Promise((ok, no) => { const rd = new FileReader(); rd.onload = () => ok(rd.result); rd.onerror = no; rd.readAsDataURL(f); });
    const { res, data: r } = await postJson("/api/voice/put", { ...box._target, name: f.name, data,
      ...(piece ? { sound: piece.id } : { key: row.key, text: row.text }) });
    note.textContent = res.ok ? `넣었습니다 — 「${where}」 ← ${f.name}${r.moved?.length ? ` · 예전 파일 ${r.moved.length}개 보관` : ""} · 화면에 반영하려면 [빌드]`
                              : (r.error || "넣지 못했습니다");
    note.className = `v-links-msg ${res.ok ? "meta" : "err"}`;
    loadVoiceLinks(box);
    box.dataset.sig = ""; refresh();
  }
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
    if (b.matches(".v-put")) {
      box._put = { row: Number(b.dataset.row), piece: b.dataset.piece == null ? null : Number(b.dataset.piece) };
      putFile.value = ""; putFile.click();
    } else if (b.matches(".v-play")) {
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
