(function () {
  function setText(el, text) {
    const slot = el.querySelector("[data-slot='text']");
    if (slot) slot.textContent = text;
    else el.textContent = text;
  }

  function show(el, text) {
    if (typeof text === "string") setText(el, text);
    el.dataset.state = "visible";
  }

  function hide(el) {
    el.dataset.state = "hidden";
  }

  window.CommonSpeechBubble = { setText, show, hide };
})();
