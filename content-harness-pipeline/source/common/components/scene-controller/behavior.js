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
