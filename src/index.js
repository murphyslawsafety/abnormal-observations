const JSON_HEADERS = {
  "Content-Type": "application/json",
  "Cache-Control": "no-store, no-cache, must-revalidate",
  "Pragma": "no-cache",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

function startingCount(env) {
  const n = Number(env.STARTING_OBSERVER_COUNT || "1");
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : 1;
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: JSON_HEADERS,
  });
}

/** Shared global observer counter (one Durable Object for the whole site). */
export class ObserverCounter {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async getCount() {
    const baseline = startingCount(this.env);
    let stored = await this.state.storage.get("count");

    // Floor raises the public total when STARTING_OBSERVER_COUNT is increased
    // (used to restore interest lost while the counter was broken).
    if (typeof stored !== "number" || stored < baseline) {
      stored = baseline;
      await this.state.storage.put("count", stored);
    }

    return stored;
  }

  async setCount(value) {
    const next = Math.max(1, Math.floor(Number(value)));
    if (!Number.isFinite(next)) {
      return json({ error: "Invalid count" }, 400);
    }
    await this.state.storage.put("count", next);
    return json({ count: next });
  }

  async fetch(request) {
    if (request.method === "GET") {
      const count = await this.getCount();
      return json({ count });
    }

    if (request.method === "POST") {
      const current = await this.getCount();
      const next = current + 1;
      await this.state.storage.put("count", next);
      return json({ count: next, observerNumber: next });
    }

    if (request.method === "PUT") {
      let body = {};
      try {
        body = await request.json();
      } catch (error) {
        return json({ error: "Expected JSON body with count" }, 400);
      }
      return this.setCount(body.count);
    }

    return json({ error: "Method not allowed" }, 405);
  }
}

function adminAuthorized(request, env) {
  const secret = env.OBSERVER_ADMIN_SECRET;
  if (!secret) return false;
  const header = request.headers.get("Authorization") || "";
  return header === "Bearer " + secret;
}

async function handleObservers(request, env) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: JSON_HEADERS });
  }

  if (!env.OBSERVER_COUNTER) {
    return json({ error: "Observer counter is not configured." }, 503);
  }

  if (request.method === "PUT" && !adminAuthorized(request, env)) {
    return json({ error: "Unauthorized" }, 401);
  }

  const id = env.OBSERVER_COUNTER.idFromName("global");
  const stub = env.OBSERVER_COUNTER.get(id);
  return stub.fetch(request.url, {
    method: request.method,
    headers: request.headers,
    body:
      request.method === "POST" || request.method === "PUT"
        ? await request.text()
        : undefined,
  });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);

    if (pathname === "/api/observers" || pathname === "/api/observers/") {
      return handleObservers(request, env);
    }

    return env.ASSETS.fetch(request);
  },
};
