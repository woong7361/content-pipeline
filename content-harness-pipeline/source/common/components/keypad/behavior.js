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
