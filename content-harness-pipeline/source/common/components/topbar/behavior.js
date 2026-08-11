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
