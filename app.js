(function () {
  const cfg = window.AO_CONFIG || {};
  const countEl = document.querySelector("[data-observer-count]");
  const joinButton = document.querySelector("[data-join]");
  const result = document.querySelector("[data-observer-result]");
  const assignedNumber = document.querySelector("[data-observer-number]");

  const base = Number(cfg.startingObserverCount || 1);
  const stored = localStorage.getItem("aoObserverNumber");
  const localJoins = Number(localStorage.getItem("aoLocalJoinCount") || 0);

  function renderCount(value) {
    if (!countEl) return;
    countEl.textContent = Number(value).toLocaleString("en-US");
  }

  renderCount(base + localJoins);

  if (stored && result && assignedNumber) {
    assignedNumber.textContent = Number(stored).toLocaleString("en-US");
    result.classList.add("show");
    if (joinButton) joinButton.textContent = "Continue";
  }

  if (joinButton) {
    joinButton.addEventListener("click", function () {
      if (stored) {
        window.location.href = "begin.html";
        return;
      }

      const nextLocalJoin = localJoins + 1;
      const number = base + nextLocalJoin;
      localStorage.setItem("aoLocalJoinCount", String(nextLocalJoin));
      localStorage.setItem("aoObserverNumber", String(number));
      renderCount(number);

      if (assignedNumber) assignedNumber.textContent = number.toLocaleString("en-US");
      if (result) result.classList.add("show");
      joinButton.textContent = "Begin Observing";
    });
  }

  document.querySelectorAll("[data-config-link]").forEach(function (link) {
    const key = link.getAttribute("data-config-link");
    const url = cfg[key];
    if (url && url !== "#") {
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener";
    } else {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        alert("Add this destination in config.js before publishing.");
      });
    }
  });
})();
