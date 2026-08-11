(function () {
  function setLabel(button, label) {
    const slot = button.querySelector("[data-slot='label']");
    if (slot) slot.textContent = label;
    else button.textContent = label;
  }

  window.CommonTicketButton = { setLabel };
})();
