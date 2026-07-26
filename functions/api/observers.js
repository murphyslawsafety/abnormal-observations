const JSON_HEADERS = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const COUNT_KEY = "observer_count";

function startingCount(env) {
  return Number(env.STARTING_OBSERVER_COUNT || "1");
}

async function readCount(kv, env) {
  const stored = await kv.get(COUNT_KEY);
  if (stored === null) {
    const seed = startingCount(env);
    await kv.put(COUNT_KEY, String(seed));
    return seed;
  }
  return Number(stored);
}

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method === "OPTIONS") {
    return new Response(null, { headers: JSON_HEADERS });
  }

  if (!env.OBSERVER_KV) {
    return new Response(
      JSON.stringify({ error: "Observer counter KV is not configured." }),
      { status: 503, headers: JSON_HEADERS }
    );
  }

  if (request.method === "GET") {
    const count = await readCount(env.OBSERVER_KV, env);
    return new Response(JSON.stringify({ count }), { headers: JSON_HEADERS });
  }

  if (request.method === "POST") {
    const current = await readCount(env.OBSERVER_KV, env);
    const next = current + 1;
    await env.OBSERVER_KV.put(COUNT_KEY, String(next));
    return new Response(
      JSON.stringify({ count: next, observerNumber: next }),
      { headers: JSON_HEADERS }
    );
  }

  return new Response(JSON.stringify({ error: "Method not allowed" }), {
    status: 405,
    headers: JSON_HEADERS,
  });
}
