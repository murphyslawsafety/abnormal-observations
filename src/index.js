const JSON_HEADERS = {
  "Content-Type": "application/json",
  "Cache-Control": "no-store, no-cache, must-revalidate",
  "Pragma": "no-cache",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function startingCount(env) {
  return Number(env.STARTING_OBSERVER_COUNT || "1");
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
    const stored = await this.state.storage.get("count");
    if (typeof stored === "number") return stored;

    const seed = startingCount(this.env);
    await this.state.storage.put("count", seed);
    return seed;
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

    return json({ error: "Method not allowed" }, 405);
  }
}

async function handleObservers(request, env) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: JSON_HEADERS });
  }

  if (!env.OBSERVER_COUNTER) {
    return json({ error: "Observer counter is not configured." }, 503);
  }

  const id = env.OBSERVER_COUNTER.idFromName("global");
  const stub = env.OBSERVER_COUNTER.get(id);
  // Forward method/body explicitly so POST is never dropped.
  return stub.fetch(request.url, {
    method: request.method,
    headers: request.headers,
    body: request.method === "POST" ? await request.text() : undefined,
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
