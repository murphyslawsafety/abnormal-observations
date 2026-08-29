(function () {
  const cfg = window.AO_CONFIG || {};
  const countEl = document.querySelector("[data-observer-count]");
  const joinButton = document.querySelector("[data-join]");
  const result = document.querySelector("[data-observer-result]");
  const assignedNumber = document.querySelector("[data-observer-number]");
  const observerBadge = document.querySelector("[data-observer-badge]");
  const reclaimPanel = document.querySelector("[data-reclaim-panel]");
  const reclaimInput = document.querySelector("[data-reclaim-input]");
  const reclaimButton = document.querySelector("[data-reclaim-restore]");
  const reclaimMessage = document.querySelector("[data-reclaim-message]");
  const restoreToggle = document.querySelector("[data-reclaim-toggle]");

  const counterApiUrl = cfg.counterApiUrl || "";
  const baseline = Number(cfg.startingObserverCount || 1);
  const VISITOR_KEY = "aoVisitorId";
  const NUMBER_KEY = "aoObserverNumber";
  const CLAIMED_KEY = "aoObserverClaimed";
  const HIT_KEY = "aoVisitHit";

  let claimInFlight = false;
  let hasNumber = false;

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
    hasNumber = true;
    if (assignedNumber) assignedNumber.textContent = formatted;
    if (observerBadge) {
      observerBadge.textContent = "Observer " + formatted;
      observerBadge.hidden = false;
    }
    if (result) result.classList.add("show");
    if (joinButton) joinButton.textContent = "Continue";
  }

  function setReclaimMessage(message, isError) {
    if (!reclaimMessage) return;
    reclaimMessage.textContent = message;
    reclaimMessage.classList.toggle("is-error", Boolean(isError));
  }

  function showReclaimPanel(message) {
    if (!reclaimPanel) return;
    reclaimPanel.hidden = false;
    if (message) setReclaimMessage(message, false);
  }

  function persistClaim(data) {
    localStorage.setItem(NUMBER_KEY, String(data.observerNumber));
    localStorage.setItem(CLAIMED_KEY, "1");
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

  /**
   * Record one site view. Runs once per page load.
   * Server increments the public total; first visit also assigns Observer #.
   */
  async function recordVisit(options) {
    const silent = !options || options.silent !== false;
    const reclaim = Boolean(options && options.reclaim);
    const legacyOverride = options && options.legacy;

    if (!counterApiUrl) {
      if (!silent) alert("Visit counter is not configured yet.");
      return null;
    }

    if (claimInFlight) return getStoredNumber();
    claimInFlight = true;
    migrateLegacyKeys();

    const payload = {
      visitorId: getVisitorId(),
      reclaim: reclaim,
    };

    const legacy = legacyOverride || (reclaim ? getStoredNumber() : null);
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

      const data = await response.json();

      if (!response.ok) {
        if (typeof data.count === "number") renderCount(data.count);
        if (response.status === 409 && reclaim) {
          setReclaimMessage(
            "Observer " + legacy + " is already claimed on another device.",
            true
          );
        }
        throw new Error(data.error || "Counter request failed");
      }

      if (typeof data.count === "number") renderCount(data.count);

      if (typeof data.observerNumber !== "number") {
        throw new Error("Counter response invalid");
      }

      persistClaim(data);

      if (reclaim && legacy && data.observerNumber !== legacy) {
        setReclaimMessage(
          "Could not restore Observer " +
            legacy +
            ". This device kept Observer " +
            data.observerNumber +
            ".",
          true
        );
        return null;
      }
      if (reclaim) {
        setReclaimMessage(
          "Observer " + data.observerNumber + " restored.",
          false
        );
        if (reclaimPanel) reclaimPanel.hidden = true;
      }
      return data.observerNumber;
    } catch (error) {
      if (!silent && !reclaim) {
        alert("Could not reach the visit counter. Please try again in a moment.");
      }
      return null;
    } finally {
      claimInFlight = false;
    }
  }

  async function initObserver() {
    migrateLegacyKeys();
    renderCount(getStoredNumber() || baseline);
    await fetchPublicCount();

    const params = new URLSearchParams(window.location.search);
    const restoreParam = Number(params.get("restore"));
    if (Number.isFinite(restoreParam) && restoreParam > 0) {
      showReclaimPanel();
      const restored = await recordVisit({
        silent: false,
        reclaim: true,
        legacy: restoreParam,
      });
      if (restored === restoreParam) return;
      if (result) result.classList.remove("show");
      if (observerBadge) observerBadge.hidden = true;
      setReclaimMessage(
        "Observer " +
          restoreParam +
          " is already on another device. Open ?restore=" +
          restoreParam +
          " in that phone's browser, or enter your number below.",
        true
      );
      return;
    }

    // One hit per page load — classic traffic counter.
    // Skip duplicate only if this exact document already recorded (bfcache/reload guards).
    if (!window[HIT_KEY]) {
      window[HIT_KEY] = true;
      await recordVisit({ silent: true });
    }

    const stored = getStoredNumber();
    if (stored) renderPersonalNumber(stored);
  }

  renderCount(baseline);
  initObserver();

  if (countEl && counterApiUrl) {
    setInterval(fetchPublicCount, 30000);
    window.addEventListener("focus", fetchPublicCount);
  }

  if (restoreToggle && reclaimPanel) {
    restoreToggle.addEventListener("click", function () {
      reclaimPanel.hidden = !reclaimPanel.hidden;
    });
  }

  if (reclaimButton && reclaimInput) {
    reclaimButton.addEventListener("click", async function () {
      const legacy = Number(reclaimInput.value);
      if (!Number.isFinite(legacy) || legacy < 1) {
        setReclaimMessage("Enter a valid Observer number.", true);
        return;
      }

      reclaimButton.disabled = true;
      reclaimButton.textContent = "Restoring…";
      await recordVisit({ silent: false, reclaim: true, legacy: legacy });
      reclaimButton.textContent = "Restore my number";
      reclaimButton.disabled = false;
    });
  }

  if (joinButton) {
    joinButton.addEventListener("click", async function () {
      if (hasNumber || getStoredNumber()) {
        window.location.href = "begin.html";
        return;
      }

      joinButton.disabled = true;
      const previousLabel = joinButton.textContent;
      joinButton.textContent = "Joining…";

      await recordVisit({ silent: false });

      joinButton.textContent = getStoredNumber() ? "Continue" : previousLabel;
      joinButton.disabled = false;

      if (getStoredNumber()) {
        window.location.href = "begin.html";
      }
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
