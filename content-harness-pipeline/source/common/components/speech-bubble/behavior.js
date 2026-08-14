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
