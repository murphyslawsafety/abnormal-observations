(function () {
  const cfg = window.AO_CONFIG || {};
  const countEl = document.querySelector("[data-observer-count]");
  const joinButton = document.querySelector("[data-join]");
  const result = document.querySelector("[data-observer-result]");
  const assignedNumber = document.querySelector("[data-observer-number]");

  const base = Number(cfg.startingObserverCount || 1);
  const stored = localStorage.getItem("aoObserverNumber");
  const localJoins = Number(localStorage.getItem("aoLocalJoinCount") || 0);
  const counterApiUrl = cfg.counterApiUrl || "";
  let globalCount = null;

  function renderCount(value) {
    if (!countEl) return;
    countEl.textContent = Number(value).toLocaleString("en-US");
  }

  function showStoredObserver() {
    if (!stored || !result || !assignedNumber) return;
    assignedNumber.textContent = Number(stored).toLocaleString("en-US");
    result.classList.add("show");
    if (joinButton) joinButton.textContent = "Continue";
  }

  function persistObserver(number) {
    localStorage.setItem("aoObserverNumber", String(number));
    renderCount(number);
    if (assignedNumber) assignedNumber.textContent = Number(number).toLocaleString("en-US");
    if (result) result.classList.add("show");
    if (joinButton) joinButton.textContent = "Begin Observing";
  }

  function joinLocally() {
    const nextLocalJoin = localJoins + 1;
    const number = base + nextLocalJoin;
    localStorage.setItem("aoLocalJoinCount", String(nextLocalJoin));
    persistObserver(number);
  }

  async function loadGlobalCount() {
    if (!counterApiUrl || !countEl) return false;

    try {
      const response = await fetch(counterApiUrl, { method: "GET" });
      if (!response.ok) return false;
      const data = await response.json();
      if (typeof data.count !== "number") return false;
      globalCount = data.count;
      renderCount(globalCount);
      return true;
    } catch (error) {
      return false;
    }
  }

  async function joinGlobally() {
    const response = await fetch(counterApiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error("Counter request failed");
    }

    const data = await response.json();
    if (typeof data.observerNumber !== "number") {
      throw new Error("Counter response invalid");
    }

    persistObserver(data.observerNumber);
  }

  renderCount(base + localJoins);
  loadGlobalCount().finally(function () {
    showStoredObserver();
  });

  if (joinButton) {
    joinButton.addEventListener("click", async function () {
      if (stored) {
        window.location.href = "begin.html";
        return;
      }

      joinButton.disabled = true;

      if (counterApiUrl) {
        try {
          await joinGlobally();
        } catch (error) {
          joinLocally();
        }
      } else {
        joinLocally();
      }

      joinButton.disabled = false;
    });
  }

  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".nav-links");

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", function () {
      const isOpen = navLinks.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
      navToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    });

    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        navLinks.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        navToggle.setAttribute("aria-label", "Open menu");
      });
    });
  }

  document.querySelectorAll("[data-config-link]").forEach(function (link) {
    const key = link.getAttribute("data-config-link");
    const url = cfg[key];
    if (url && url !== "#") {
      link.href = url;
      if (/^https?:\/\//i.test(url)) {
        link.target = "_blank";
        link.rel = "noopener";
      }
    } else {
      link.addEventListener("click", function (event) {
        event.preventDefault();
        alert("Add this destination in config.js before publishing.");
      });
    }
  });
})();
