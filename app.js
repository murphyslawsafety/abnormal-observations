(function () {
  const cfg = window.AO_CONFIG || {};
  const countEl = document.querySelector("[data-observer-count]");
  const joinButton = document.querySelector("[data-join]");
  const result = document.querySelector("[data-observer-result]");
  const assignedNumber = document.querySelector("[data-observer-number]");

  const base = Number(cfg.startingObserverCount || 1);
  const counterApiUrl = cfg.counterApiUrl || "";
  const JOINED_KEY = "aoObserverNumber";
  const GLOBAL_JOIN_KEY = "aoJoinedGlobally";
  const AUTO_JOIN_DELAY_MS = 1800;

  let stored = localStorage.getItem(JOINED_KEY);
  let joinedGlobally = localStorage.getItem(GLOBAL_JOIN_KEY) === "1";
  let joinInFlight = false;

  function renderCount(value) {
    if (!countEl) return;
    countEl.textContent = Number(value).toLocaleString("en-US");
  }

  function showAssignedObserver(number) {
    if (!result || !assignedNumber) return;
    assignedNumber.textContent = Number(number).toLocaleString("en-US");
    result.classList.add("show");
    if (joinButton) joinButton.textContent = "Continue";
  }

  function persistGlobalObserver(number) {
    localStorage.setItem(JOINED_KEY, String(number));
    localStorage.setItem(GLOBAL_JOIN_KEY, "1");
    stored = String(number);
    joinedGlobally = true;
    renderCount(number);
    showAssignedObserver(number);
    if (joinButton) joinButton.textContent = "Begin Observing";
  }

  function clearLocalPreviewJoin() {
    localStorage.removeItem(JOINED_KEY);
    localStorage.removeItem("aoLocalJoinCount");
    localStorage.removeItem(GLOBAL_JOIN_KEY);
    stored = null;
    joinedGlobally = false;
    if (result) result.classList.remove("show");
    if (joinButton) joinButton.textContent = "Become One";
  }

  async function loadGlobalCount() {
    if (!counterApiUrl || !countEl) return false;

    try {
      const response = await fetch(counterApiUrl, {
        method: "GET",
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return false;
      const data = await response.json();
      if (typeof data.count !== "number") return false;

      // After joining, keep personal number visible but sync public total from server.
      if (!(stored && joinedGlobally)) {
        renderCount(data.count);
      } else {
        renderCount(data.count);
        showAssignedObserver(stored);
      }

      // Old local-only joins were never part of the real global count.
      if (stored && !joinedGlobally) {
        clearLocalPreviewJoin();
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  async function joinGlobally() {
    if (joinInFlight) return null;
    if (stored && joinedGlobally) return Number(stored);

    joinInFlight = true;

    try {
      const response = await fetch(counterApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        cache: "no-store",
        body: "{}",
      });

      if (!response.ok) {
        throw new Error("Counter request failed (" + response.status + ")");
      }

      const data = await response.json();
      if (typeof data.observerNumber !== "number") {
        throw new Error("Counter response invalid");
      }

      persistGlobalObserver(data.observerNumber);
      return data.observerNumber;
    } finally {
      joinInFlight = false;
    }
  }

  function scheduleAutoJoin() {
    // First real visit claims an observer number automatically.
    // Requires JS + a visible tab so casual crawlers are less likely to inflate the count.
    if (!counterApiUrl) return;
    if (stored && joinedGlobally) return;

    let done = false;

    function attempt() {
      if (done) return;
      if (document.visibilityState !== "visible") return;
      done = true;
      joinGlobally().catch(function () {
        // Leave Become One available as a manual retry on the homepage.
        done = false;
      });
    }

    setTimeout(attempt, AUTO_JOIN_DELAY_MS);
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        setTimeout(attempt, 400);
      }
    });
  }

  renderCount(base);

  loadGlobalCount().finally(function () {
    if (stored && joinedGlobally) {
      showAssignedObserver(stored);
    }
    // Enroll from any page so links to Begin / Works still assign a number.
    scheduleAutoJoin();
  });

  // Keep the public total fresh while the page stays open.
  if (countEl && counterApiUrl) {
    setInterval(function () {
      loadGlobalCount();
    }, 20000);
    window.addEventListener("focus", function () {
      loadGlobalCount();
    });
  }

  if (joinButton) {
    joinButton.addEventListener("click", async function () {
      if (stored && joinedGlobally) {
        window.location.href = "begin.html";
        return;
      }

      if (!counterApiUrl) {
        alert("Observer counter is not configured yet.");
        return;
      }

      joinButton.disabled = true;
      const previousLabel = joinButton.textContent;
      joinButton.textContent = "Connecting…";

      try {
        await joinGlobally();
      } catch (error) {
        joinButton.textContent = previousLabel;
        alert("Could not reach the observer counter. Please try again in a moment.");
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
