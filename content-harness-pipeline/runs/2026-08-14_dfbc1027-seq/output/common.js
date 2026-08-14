/* 이 파일은 source/common/components에서 코드가 생성한다.
   여기를 고쳐도 다음 stage가 끝나면 원본으로 되돌아간다.
   이 차시에서만 값을 바꾸려면 index.html의 <style>에서 오버라이드한다.
   <link>보다 뒤에 오므로 소스 순서로 이긴다. */

/* --- debug-jumper --- */
(function () {
  function init(panel, controller, options) {
    const list = panel.querySelector("[data-slot='scene-list']") || panel.querySelector(".c-debugList");
    const current = panel.querySelector("[data-slot='current']") || panel.querySelector(".c-debugCurrent");
    const close = panel.querySelector("[data-action='close']") || panel.querySelector(".c-debugHead button");
    const toggle = options && options.toggle;
    if (!list || !current) return null;

    function build() {
      list.innerHTML = "";
      controller.scenes.forEach((scene, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "c-debugScene";
        button.dataset.go = scene.id;
        button.innerHTML =
          '<span class="c-debugOrder">' + (scene.dataset.qaOrder || String(index + 1)) + '</span>' +
          '<span><span class="c-debugLabel">' + (scene.dataset.qaLabel || scene.id) + '</span>' +
          '<span class="c-debugId">' + scene.id + '</span></span>';
        button.addEventListener("click", () => controller.showScene(scene.id));
        list.appendChild(button);
      });
    }

    function sync() {
      const scene = controller.currentScene();
      if (!scene) return;
      current.textContent = scene.id + " · " + (scene.dataset.qaLabel || "");
      panel.querySelectorAll(".c-debugScene").forEach(button => {
        button.classList.toggle("current", button.dataset.go === scene.id);
      });
    }

    function open(force) {
      const next = typeof force === "boolean" ? force : panel.hidden;
      panel.hidden = !next;
      if (next) sync();
    }

    build();
    sync();
    if (close) close.addEventListener("click", () => open(false));
    if (toggle) toggle.addEventListener("click", () => open());
    addEventListener("common:scenechange", sync);
    addEventListener("keydown", event => {
      const tag = event.target && event.target.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (!event.altKey && !event.metaKey && (event.key === "`" || event.code === "Backquote")) {
        event.preventDefault();
        open();
      }
    });

    return { open, sync };
  }

  window.CommonDebugJumper = { init };
})();

/* --- feedback-layer --- */
(function () {
  let stampTimer = 0;

  function showStamp(el, type, options) {
    if (!el) return;
    const hold = !!(options && options.hold);
    clearTimeout(stampTimer);
    const correct = type === "correct";
    el.src = correct ? el.dataset.correctSrc : el.dataset.wrongSrc;
    el.alt = correct ? "정답 O 도장" : "오답 X 도장";
    el.classList.remove("show");
    void el.offsetWidth;
    el.classList.add("show");
    if (!hold) {
      stampTimer = setTimeout(() => el.classList.remove("show"), 900);
    }
  }

  function hideStamp(el) {
    clearTimeout(stampTimer);
    if (el) el.classList.remove("show");
  }

  window.CommonFeedbackLayer = { showStamp, hideStamp };
})();

/* --- keypad --- */
(function () {
  const KEYPAD_KEYS = [1,2,3,4,5,6,7,8,9,"del",0,"enter"];

  function keypadPress(button) {
    button.classList.add("keypad-pressing");
    const off = () => button.classList.remove("keypad-pressing");
    button.addEventListener("pointerup", off, { once: true });
    button.addEventListener("pointerleave", off, { once: true });
    button.addEventListener("pointercancel", off, { once: true });
  }

  function displayTick(display) {
    if (!display) return;
    display.classList.remove("keypad-tick");
    void display.offsetWidth;
    display.classList.add("keypad-tick");
  }

  function build(root, handler) {
    const keysRoot = root.matches(".c-keypad") ? root : root.querySelector(".c-keypad");
    if (!keysRoot) return;
    keysRoot.innerHTML = "";
    KEYPAD_KEYS.forEach(value => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "c-key" + (value === "enter" ? " enter" : value === "del" ? " del" : "");
      button.textContent = value === "enter" ? "확인" : value === "del" ? "←" : value;
      if (value === "enter") button.setAttribute("aria-label", "확인");
      if (value === "del") button.setAttribute("aria-label", "지우기");
      button.addEventListener("pointerdown", () => keypadPress(button));
      button.addEventListener("click", () => handler(typeof value === "number" ? String(value) : value));
      keysRoot.appendChild(button);
    });
  }

  function setEnabled(root, enabled) {
    root.querySelectorAll(".c-key").forEach(key => {
      key.disabled = !enabled;
    });
  }

  function setConfirmOnly(root) {
    root.querySelectorAll(".c-key").forEach(key => {
      key.disabled = !key.classList.contains("enter");
    });
  }

  window.CommonKeypad = { build, displayTick, setEnabled, setConfirmOnly };
})();

/* --- scene-controller --- */
(function () {
  function scaleStage(stage) {
    if (!stage) return;
    const portrait = innerHeight > innerWidth;
    const scale = portrait
      ? Math.min(innerWidth / 1080, innerHeight / 1920)
      : Math.min(innerWidth / 1920, innerHeight / 1080);
    const rotate = portrait ? " rotate(90deg)" : "";
    stage.style.transform = "translate(-50%, -50%)" + rotate + " scale(" + scale + ")";
  }

  function createSceneController(stage) {
    const scenes = Array.from(stage.querySelectorAll(".scene"));
    let current = scenes.find(scene => scene.classList.contains("active")) || scenes[0];
    if (current) current.classList.add("active");

    function showScene(id) {
      const next = scenes.find(scene => scene.id === id || scene.dataset.qaScene === id);
      if (!next || next === current) return;
      const previous = current;
      current = next;
      if (previous) {
        previous.classList.remove("active");
        previous.classList.add("leaving");
        setTimeout(() => previous.classList.remove("leaving"), 460);
      }
      next.classList.add("active");
      window.dispatchEvent(new CustomEvent("common:scenechange", {
        detail: { sceneId: next.id, scene: next }
      }));
    }

    function currentScene() {
      return current;
    }

    window.__contentHarnessShowScene = showScene;
    return { scenes, showScene, currentScene };
  }

  window.CommonSceneController = { scaleStage, createSceneController };
})();

/* --- speech-bubble --- */
(function () {
  function setText(el, text) {
    const slot = el.querySelector("[data-slot='text']");
    if (slot) slot.textContent = text;
    else el.textContent = text;
  }

  /* label: 문자열이면 그 문구로 버튼을 켜고, 빈 값(null/""/false)이면 끈다.
     true를 주면 마크업에 적힌 문구를 그대로 두고 켜기만 한다. */
  function setNext(el, label) {
    const nav = el.querySelector("[data-slot='nav']");
    if (!nav) return;
    if (typeof label === "string" && label) {
      const button = nav.querySelector("[data-action='next']");
      if (button) button.textContent = label;
    }
    nav.hidden = !(label === true || (typeof label === "string" && label));
  }

  function show(el, text, options) {
    if (typeof text === "string") setText(el, text);
    if (options && "next" in options) setNext(el, options.next);
    el.dataset.state = "visible";
  }

  function hide(el) {
    el.dataset.state = "hidden";
  }

  /* 버튼마다 핸들러를 달지 않는다. 나중에 삽입된 말풍선도 같은 경로로 동작해야 한다.
     클릭은 말풍선까지 그대로 버블링된다 — 말풍선 전체를 진행 표면으로 쓰는 콘텐츠가
     버튼만 죽은 자리로 만들지 않기 위해서다. 둘 다 듣지 않는다. */
  document.addEventListener("click", event => {
    const target = event.target;
    if (!target || !target.closest) return;
    const button = target.closest("[data-action='next']");
    if (!button) return;
    /* class도 함께 본다 — data-component 없이 마크업한 말풍선에서 버튼만 죽는 것을 막는다 */
    const bubble = button.closest("[data-component='speech-bubble'], .c-speechBubble");
    if (!bubble) return;
    bubble.dispatchEvent(new CustomEvent("common:speechnext", {
      bubbles: true,
      detail: { bubble }
    }));
  });

  window.CommonSpeechBubble = { setText, setNext, show, hide };
})();

/* --- ticket-button --- */
(function () {
  function setLabel(button, label) {
    const slot = button.querySelector("[data-slot='label']");
    if (slot) slot.textContent = label;
    else button.textContent = label;
  }

  window.CommonTicketButton = { setLabel };
})();

/* --- topbar --- */
(function () {
  function slot(root, name) {
    return root.querySelector("[data-slot='" + name + "']");
  }

  function action(root, name) {
    return root.querySelector("[data-action='" + name + "']");
  }

  function setTitle(root, text) {
    const el = slot(root, "title");
    if (!el) return;
    el.textContent = text || "";
    if (text) el.setAttribute("aria-label", "차시 제목: " + text);
    else el.removeAttribute("aria-label");
  }

  /* 지금 어느 단계인지. 빈 값이면 구분선까지 함께 감춘다 */
  function setStep(root, text) {
    const el = slot(root, "step");
    if (!el) return;
    el.textContent = text || "";
    el.hidden = !text;
    if (text) el.setAttribute("aria-label", "현재 단계: " + text);
    else el.removeAttribute("aria-label");
  }

  function setProgress(root, value) {
    const pct = Math.max(0, Math.min(100, Math.round(Number(value) || 0)));
    const fill = slot(root, "fill");
    const pctText = slot(root, "pct");
    const bar = slot(root, "bar");
    if (fill) fill.style.width = pct + "%";
    if (pctText) pctText.textContent = pct + "%";
    if (bar) bar.setAttribute("aria-label", "학습 진행률 " + pct + "퍼센트");
    return pct;
  }

  function setSoundOn(root, on) {
    const button = action(root, "sound");
    if (!button) return;
    button.setAttribute("aria-pressed", String(!!on));
    button.dataset.soundOn = String(!!on);
    button.setAttribute("aria-label", on ? "소리 끄기" : "소리 켜기");
    button.title = on ? "소리 끄기" : "소리 켜기";
  }

  function isSoundOn(root) {
    const button = action(root, "sound");
    return !button || button.getAttribute("aria-pressed") !== "false";
  }

  /* 타이틀 화면처럼 HUD를 감출 때 쓴다 */
  function setHidden(root, hidden) {
    root.dataset.state = hidden ? "hidden" : "visible";
  }

  function setMenuExpanded(root, open) {
    const button = action(root, "menu");
    if (button) button.setAttribute("aria-expanded", String(!!open));
  }

  function openMenu(menu, root) {
    menu.classList.add("is-open");
    if (root) setMenuExpanded(root, true);
  }

  function closeMenu(menu, root) {
    menu.classList.remove("is-open");
    if (root) setMenuExpanded(root, false);
  }

  /* course = { gradeLabel, current, lessons: [{ no, id, path, title }] }
     path가 있으면 그 경로로, 없고 id만 있으면 형제 디렉토리(`../{id}/`)로 간다.
     둘 다 없으면 아직 준비되지 않은 차시로 보고 잠근다. */
  function buildMenu(menu, course, onNavigate) {
    const list = slot(menu, "list");
    const grade = slot(menu, "grade");
    if (grade) grade.textContent = (course && course.gradeLabel) || "";
    if (!list) return;

    list.innerHTML = "";
    const lessons = (course && course.lessons) || [];
    lessons.forEach(item => {
      const href = item.path || (item.id ? "../" + item.id + "/" : "");
      const available = !!href;
      const current = available && !!item.id && item.id === (course && course.current);

      const button = document.createElement("button");
      button.type = "button";
      button.className = "c-courseMenuItem";
      if (current) button.classList.add("is-current");
      if (!available) {
        button.classList.add("is-locked");
        button.disabled = true;
        button.setAttribute("aria-disabled", "true");
      }

      const no = document.createElement("span");
      no.className = "c-courseMenuNo";
      no.textContent = item.no == null ? "" : String(item.no);
      button.appendChild(no);

      const title = document.createElement("span");
      title.className = "c-courseMenuTitle";
      title.textContent = item.title || "준비 중";
      button.appendChild(title);

      if (current) {
        const now = document.createElement("span");
        now.className = "c-courseMenuNow";
        now.textContent = "지금";
        button.appendChild(now);
      }

      if (!available) {
        const soon = document.createElement("span");
        soon.className = "c-courseMenuSoon";
        soon.textContent = "준비 중";
        button.appendChild(soon);
      }

      if (available && !current) {
        button.dataset.goto = href;
        button.addEventListener("click", () => onNavigate(href, item));
      }

      list.appendChild(button);
    });
  }

  /* options = {
       menu,            드로어 element. 생략하면 [data-component='course-menu']를 찾는다
       course,          차시 목록 데이터
       title, step, progress, soundOn,
       onSoundChange(on),
       onHome(),        "처음으로". scene 이동은 콘텐츠가 정한다 (컴포넌트끼리 직접 호출하지 않는다)
       onNavigate(href, item),   기본값은 location.assign(href)
       followScenes     기본 true. common:scenechange를 듣고 scene의
                        data-qa-label → step, data-progress → progress를 반영한다
     } */
  function init(root, options) {
    const opts = options || {};
    const menu = opts.menu || document.querySelector("[data-component='course-menu']");
    const navigate = opts.onNavigate || (href => location.assign(href));

    if (opts.title != null) setTitle(root, opts.title);
    if (opts.step != null) setStep(root, opts.step);
    setProgress(root, opts.progress || 0);
    setSoundOn(root, opts.soundOn !== false);

    const soundButton = action(root, "sound");
    if (soundButton) {
      soundButton.addEventListener("click", () => {
        const next = !isSoundOn(root);
        setSoundOn(root, next);
        if (opts.onSoundChange) opts.onSoundChange(next);
      });
    }

    if (menu) {
      buildMenu(menu, opts.course, navigate);
      const menuButton = action(root, "menu");
      if (menuButton) {
        menuButton.addEventListener("click", () => {
          if (menu.classList.contains("is-open")) closeMenu(menu, root);
          else openMenu(menu, root);
        });
      }
      const close = action(menu, "close");
      if (close) close.addEventListener("click", () => closeMenu(menu, root));
      const home = action(menu, "home");
      if (home) {
        home.addEventListener("click", () => {
          closeMenu(menu, root);
          if (opts.onHome) opts.onHome();
        });
      }
      /* 패널 바깥(오버레이 자신)을 눌렀을 때만 닫는다 */
      menu.addEventListener("click", event => {
        if (event.target === menu) closeMenu(menu, root);
      });
      /* aria-modal 드로어라 Escape로도 닫는다. 08에는 없던 동작이다 */
      addEventListener("keydown", event => {
        if (event.key === "Escape" && menu.classList.contains("is-open")) closeMenu(menu, root);
      });
    }

    if (opts.followScenes !== false) {
      addEventListener("common:scenechange", event => {
        const scene = event.detail && event.detail.scene;
        if (!scene) return;
        setStep(root, scene.dataset.qaLabel || "");
        if (scene.dataset.progress != null) setProgress(root, scene.dataset.progress);
      });
    }

    return {
      root,
      menu,
      setTitle: text => setTitle(root, text),
      setStep: text => setStep(root, text),
      setProgress: value => setProgress(root, value),
      setSoundOn: on => setSoundOn(root, on),
      isSoundOn: () => isSoundOn(root),
      setHidden: hidden => setHidden(root, hidden),
      open: () => menu && openMenu(menu, root),
      close: () => menu && closeMenu(menu, root)
    };
  }

  window.CommonTopbar = {
    init,
    setTitle,
    setStep,
    setProgress,
    setSoundOn,
    isSoundOn,
    setHidden,
    openMenu,
    closeMenu
  };
})();
