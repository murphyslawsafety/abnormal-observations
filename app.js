(function () {
  const cfg = window.AO_CONFIG || {};
  const countEl = document.querySelector("[data-observer-count]");
  const joinButton = document.querySelector("[data-join]");
  const result = document.querySelector("[data-observer-result]");
  const assignedNumber = document.querySelector("[data-observer-number]");
  const observerBadge = document.querySelector("[data-observer-badge]");

  const counterApiUrl = cfg.counterApiUrl || "";
  const VISITOR_KEY = "aoVisitorId";
  const NUMBER_KEY = "aoObserverNumber";
  const CLAIMED_KEY = "aoObserverClaimed";
  const AUTO_CLAIM_DELAY_MS = 1200;

  let claimInFlight = false;
  let syncedThisSession = false;

  function migrateLegacyKeys() {
    if (localStorage.getItem("aoJoinedGlobally") === "1") {
      localStorage.setItem(CLAIMED_KEY, "1");
    }
  }

  function getVisitorId() {
    let id = localStorage.getItem(VISITOR_KEY);
    if (!id) {
      id =
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : "ao-" + Date.now() + "-" + Math.random().toString(16).slice(2);
      localStorage.setItem(VISITOR_KEY, id);
    }
    return id;
  }

  function getStoredNumber() {
    const n = Number(localStorage.getItem(NUMBER_KEY));
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  function renderCount(value) {
    if (!countEl) return;
    countEl.textContent = Number(value).toLocaleString("en-US");
  }

  function renderPersonalNumber(number) {
    const formatted = Number(number).toLocaleString("en-US");
    if (assignedNumber) assignedNumber.textContent = formatted;
    if (observerBadge) {
      observerBadge.textContent = "Observer " + formatted;
      observerBadge.hidden = false;
    }
    if (result) result.classList.add("show");
    if (joinButton) joinButton.textContent = "Continue";
  }

  function persistClaim(data) {
    localStorage.setItem(NUMBER_KEY, String(data.observerNumber));
    localStorage.setItem(CLAIMED_KEY, "1");
    syncedThisSession = true;
    renderCount(data.count);
    renderPersonalNumber(data.observerNumber);
  }

  async function fetchPublicCount() {
    if (!counterApiUrl) return false;

    try {
      const response = await fetch(counterApiUrl, {
        method: "GET",
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return false;
      const data = await response.json();
      if (typeof data.count !== "number") return false;
      renderCount(data.count);
      return true;
    } catch (error) {
      return false;
    }
  }

  async function syncObserver(silent) {
    if (!counterApiUrl) {
      if (!silent) alert("Observer counter is not configured yet.");
      return null;
    }

    if (claimInFlight) return getStoredNumber();
    claimInFlight = true;

    migrateLegacyKeys();

    const payload = { visitorId: getVisitorId() };
    const legacy = getStoredNumber();
    if (legacy) payload.legacyObserverNumber = legacy;

    try {
      const response = await fetch(counterApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        cache: "no-store",
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Counter request failed (" + response.status + ")");
      }

      const data = await response.json();
      if (typeof data.observerNumber !== "number") {
        throw new Error("Counter response invalid");
      }

      persistClaim(data);
      return data.observerNumber;
    } catch (error) {
      if (legacy && localStorage.getItem(CLAIMED_KEY) === "1") {
        renderPersonalNumber(legacy);
        await fetchPublicCount();
        return legacy;
      }
      if (!silent) {
        alert("Could not reach the observer counter. Please try again in a moment.");
      }
      return null;
    } finally {
      claimInFlight = false;
    }
  }

  function scheduleAutoClaim() {
    if (!counterApiUrl || syncedThisSession) return;
    if (getStoredNumber()) {
      syncObserver(true);
      return;
    }

    let done = false;

    function attempt() {
      if (done || syncedThisSession) return;
      if (document.visibilityState !== "visible") return;
      done = true;
      syncObserver(true).catch(function () {
        done = false;
      });
    }

    setTimeout(attempt, AUTO_CLAIM_DELAY_MS);
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        setTimeout(attempt, 300);
      }
    });
  }

  migrateLegacyKeys();
  renderCount(Number(cfg.startingObserverCount || 1));

  fetchPublicCount().finally(function () {
    if (getStoredNumber() || localStorage.getItem(CLAIMED_KEY) === "1") {
      syncObserver(true);
    } else {
      scheduleAutoClaim();
    }
  });

  if (countEl && counterApiUrl) {
    setInterval(fetchPublicCount, 20000);
    window.addEventListener("focus", function () {
      fetchPublicCount();
      if (getStoredNumber() || localStorage.getItem(CLAIMED_KEY) === "1") {
        syncObserver(true);
      }
    });
  }

  if (joinButton) {
    joinButton.addEventListener("click", async function () {
      if (syncedThisSession && getStoredNumber()) {
        window.location.href = "begin.html";
        return;
      }

      joinButton.disabled = true;
      const previousLabel = joinButton.textContent;
      joinButton.textContent = "Claiming…";

      await syncObserver(false);

      joinButton.textContent = getStoredNumber() ? "Continue" : previousLabel;
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
