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
