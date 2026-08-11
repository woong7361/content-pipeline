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
