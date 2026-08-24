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

function visitorKey(id) {
  return `visitor:${id}`;
}

function numberKey(n) {
  return `num:${n}`;
}

function isReleasableHolder(holder) {
  return typeof holder === "string" && holder.startsWith("test-restore-");
}

/** Shared global observer registry (one Durable Object for the whole site). */
export class ObserverCounter {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async getCount() {
    const baseline = startingCount(this.env);
    let stored = await this.state.storage.get("count");

    if (typeof stored !== "number" || stored < baseline) {
      stored = baseline;
      await this.state.storage.put("count", stored);
    }

    return stored;
  }

  async bindNumber(visitorId, observerNumber, options = {}) {
    const count = await this.getCount();
    const finalCount = Math.max(count, observerNumber);

    await this.state.storage.put("count", finalCount);
    await this.state.storage.put(visitorKey(visitorId), observerNumber);
    await this.state.storage.put(numberKey(observerNumber), visitorId);

    const existingMeta = (await this.state.storage.get(`meta:${observerNumber}`)) || {};
    if (!existingMeta.assignedAt) {
      await this.state.storage.put(`meta:${observerNumber}`, {
        assignedAt: Date.now(),
        restored: Boolean(options.restored),
      });
    }

    return json({
      count: finalCount,
      observerNumber,
      returning: Boolean(options.returning),
      restored: Boolean(options.restored),
    });
  }

  async releaseVisitorAssignment(visitorId, observerNumber) {
    const mapped = await this.state.storage.get(numberKey(observerNumber));
    if (mapped === visitorId) {
      await this.state.storage.delete(numberKey(observerNumber));
    }
  }

  async setCount(value) {
    const next = Math.max(startingCount(this.env), Math.floor(Number(value)));
    if (!Number.isFinite(next)) {
      return json({ error: "Invalid count" }, 400);
    }
    await this.state.storage.put("count", next);
    return json({ count: next });
  }

  async releaseNumber(observerNumber) {
    const n = Math.floor(Number(observerNumber));
    if (!Number.isFinite(n) || n < 1) {
      return json({ error: "Invalid observer number." }, 400);
    }

    const holder = await this.state.storage.get(numberKey(n));
    if (holder) {
      await this.state.storage.delete(visitorKey(holder));
    }
    await this.state.storage.delete(numberKey(n));
    await this.state.storage.delete(`meta:${n}`);

    return json({ released: n });
  }

  async claimVisitor(visitorId, legacyObserverNumber, reclaim = false) {
    if (!visitorId || typeof visitorId !== "string" || visitorId.length < 8) {
      return json({ error: "A valid visitorId is required." }, 400);
    }

    const baseline = startingCount(this.env);
    const existing = await this.state.storage.get(visitorKey(visitorId));
    const legacy = Math.floor(Number(legacyObserverNumber));

    if (typeof existing === "number" && !reclaim) {
      const count = await this.getCount();
      return json({
        count,
        observerNumber: existing,
        returning: true,
      });
    }

    if (Number.isFinite(legacy) && legacy >= 1 && (reclaim || legacy <= baseline)) {
      const holder = await this.state.storage.get(numberKey(legacy));
      const canTake =
        !holder ||
        holder === visitorId ||
        isReleasableHolder(holder) ||
        (reclaim && legacy <= baseline && typeof existing === "number" && existing > baseline);

      if (canTake) {
        if (holder && holder !== visitorId) {
          await this.state.storage.delete(visitorKey(holder));
        }
        if (typeof existing === "number" && existing !== legacy) {
          await this.releaseVisitorAssignment(visitorId, existing);
        }
        return this.bindNumber(visitorId, legacy, {
          returning: existing === legacy,
          restored: true,
        });
      }

      if (reclaim) {
        return json({ error: "That Observer number is already claimed by someone else." }, 409);
      }
    }

    if (typeof existing === "number") {
      const count = await this.getCount();
      return json({
        count,
        observerNumber: existing,
        returning: true,
      });
    }

    const count = await this.getCount();
    const observerNumber = count + 1;
    return this.bindNumber(visitorId, observerNumber, { returning: false });
  }

  async lookupNumber(observerNumber) {
    const n = Math.floor(Number(observerNumber));
    if (!Number.isFinite(n) || n < 1) {
      return json({ error: "Invalid observer number." }, 400);
    }

    const visitorId = await this.state.storage.get(numberKey(n));
    if (!visitorId) {
      return json({ error: "Observer number not assigned." }, 404);
    }

    const meta = (await this.state.storage.get(`meta:${n}`)) || {};
    return json({
      observerNumber: n,
      visitorId,
      assignedAt: meta.assignedAt || null,
      restored: Boolean(meta.restored),
    });
  }

  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.searchParams.has("number")) {
      return this.lookupNumber(url.searchParams.get("number"));
    }

    if (request.method === "GET") {
      const count = await this.getCount();
      const visitorId = url.searchParams.get("visitorId");
      if (visitorId) {
        const existing = await this.state.storage.get(visitorKey(visitorId));
        if (typeof existing === "number") {
          return json({ count, observerNumber: existing, returning: true });
        }
      }
      return json({ count });
    }

    if (request.method === "POST") {
      let body = {};
      try {
        body = await request.json();
      } catch (error) {
        return json({ error: "Expected JSON body with visitorId." }, 400);
      }
      return this.claimVisitor(
        body.visitorId,
        body.legacyObserverNumber,
        Boolean(body.reclaim)
      );
    }

    if (request.method === "PUT") {
      let body = {};
      try {
        body = await request.json();
      } catch (error) {
        return json({ error: "Expected JSON body." }, 400);
      }
      if (body.release !== undefined) {
        return this.releaseNumber(body.release);
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

  const url = new URL(request.url);
  const needsAdmin =
    request.method === "PUT" ||
    (request.method === "GET" && url.searchParams.has("number"));

  if (needsAdmin && !adminAuthorized(request, env)) {
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
