/*
  preview 전용 harness. 컴포넌트 자체와는 무관하다.
  최종 output에는 절대 inline하지 않는다.

  Preview.mount({ title, path, note })  HUD를 만든다
  Preview.control(label, handler)       버튼을 추가한다
  Preview.log(message)                  HUD 하단에 한 줄 남긴다

  stage 스케일링은 여기서 직접 한다. scene-controller에 의존하지 않는다.
  (scene-controller / debug-jumper preview만 그 컴포넌트를 따로 로드한다)
*/
(function () {
  let controls = null;
  let logEl = null;
  let hudEl = null;

  function scale() {
    const stage = document.getElementById("stage");
    if (!stage) return;
    /* HUD는 내용에 따라 줄바꿈되어 높이가 변한다. 고정값으로 비우면
       topbar처럼 stage 맨 위에 붙는 컴포넌트가 HUD에 가린다. */
    const hudHeight = hudEl ? hudEl.offsetHeight : 0;
    const w = innerWidth;
    const h = innerHeight - hudHeight;
    const s = Math.min(w / 1920, h / 1080);
    stage.style.transform = "translate(-50%, -50%) scale(" + s + ")";
    stage.style.top = hudHeight + h / 2 + "px";
  }

  function mount(options) {
    const opts = options || {};
    const hud = document.createElement("div");
    hud.className = "p-hud";
    hud.innerHTML =
      '<div class="p-title"><strong></strong><span></span></div>' +
      '<div class="p-note"></div>' +
      '<div class="p-controls"></div>' +
      '<div class="p-log"></div>';
    hud.querySelector(".p-title strong").textContent = opts.title || "component";
    hud.querySelector(".p-title span").textContent = opts.path || "";
    hud.querySelector(".p-note").textContent = opts.note || "";
    document.body.appendChild(hud);

    hudEl = hud;
    controls = hud.querySelector(".p-controls");
    logEl = hud.querySelector(".p-log");

    scale();
    addEventListener("resize", scale);
    addEventListener("orientationchange", scale);
  }

  function control(label, handler) {
    if (!controls) return;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", handler);
    controls.appendChild(button);
    scale(); /* 버튼이 줄바꿈되면 HUD 높이가 바뀐다 */
  }

  function log(message) {
    if (!logEl) return;
    logEl.textContent = message;
    scale();
  }

  window.Preview = { mount, control, log, scale };
})();
