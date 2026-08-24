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

  async function restoreExistingClaim() {
    if (!counterApiUrl) return false;

    const visitorId = getVisitorId();
    const stored = getStoredNumber();

    try {
      const response = await fetch(
        counterApiUrl + "?visitorId=" + encodeURIComponent(visitorId),
        {
          method: "GET",
          cache: "no-store",
          headers: { Accept: "application/json" },
        }
      );

      if (!response.ok) return false;
      const data = await response.json();

      if (typeof data.observerNumber === "number") {
        persistClaim(data);
        return true;
      }

      // Local number from an old session — re-claim under this visitor id.
      if (stored && localStorage.getItem(CLAIMED_KEY) === "1") {
        return claimObserver(true);
      }

      return false;
    } catch (error) {
      if (stored && localStorage.getItem(CLAIMED_KEY) === "1") {
        renderPersonalNumber(stored);
        return true;
      }
      return false;
    }
  }

  async function claimObserver(silent) {
    if (!counterApiUrl) {
      if (!silent) alert("Observer counter is not configured yet.");
      return null;
    }

    if (claimInFlight) return getStoredNumber();
    if (getStoredNumber() && localStorage.getItem(CLAIMED_KEY) === "1") {
      return getStoredNumber();
    }

    claimInFlight = true;

    try {
      const response = await fetch(counterApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        cache: "no-store",
        body: JSON.stringify({ visitorId: getVisitorId() }),
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
      if (!silent) {
        alert("Could not reach the observer counter. Please try again in a moment.");
      }
      return null;
    } finally {
      claimInFlight = false;
    }
  }

  function scheduleAutoClaim() {
    if (!counterApiUrl) return;
    if (getStoredNumber() && localStorage.getItem(CLAIMED_KEY) === "1") return;

    let done = false;

    function attempt() {
      if (done) return;
      if (document.visibilityState !== "visible") return;
      done = true;
      claimObserver(true).catch(function () {
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

  const fallback = Number(cfg.startingObserverCount || 1);
  renderCount(fallback);

  restoreExistingClaim()
    .finally(function () {
      fetchPublicCount();
      scheduleAutoClaim();
    });

  if (countEl && counterApiUrl) {
    setInterval(fetchPublicCount, 20000);
    window.addEventListener("focus", fetchPublicCount);
  }

  if (joinButton) {
    joinButton.addEventListener("click", async function () {
      if (getStoredNumber() && localStorage.getItem(CLAIMED_KEY) === "1") {
        window.location.href = "begin.html";
        return;
      }

      joinButton.disabled = true;
      const previousLabel = joinButton.textContent;
      joinButton.textContent = "Claiming…";

      await claimObserver(false);

      joinButton.textContent =
        getStoredNumber() && localStorage.getItem(CLAIMED_KEY) === "1"
          ? "Continue"
          : previousLabel;
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
