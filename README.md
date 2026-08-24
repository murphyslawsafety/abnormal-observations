# Abnormal Observations — Website Starter

## What it includes

- Mystery-first landing page
- Observer count
- "Become One" interaction
- First observation page
- Four-book pathway
- Mobile-responsive layout
- No framework, database, or paid software required

## Observer counter model

- **Current Observers** = total unique observers (public count).
- **Your number** = permanent designation, tied to this browser via a private visitor id.
- Baseline restored to **2,740** (Cloudflare unique visitors: ~1,570 on `.com` + ~1,170 on `.org`).
- New visitors receive **1571, 1572, …** and keep that number on return visits.

### Lucky-number promotions

Set `OBSERVER_ADMIN_SECRET` in the Cloudflare Worker dashboard, then:

```bash
curl "https://abnormalobservations.com/api/observers?number=13" \
  -H "Authorization: Bearer YOUR_SECRET"
```

Returns the anonymous visitor id assigned to Observer 13 (for verification when someone claims the prize).

### .org traffic (connect the same Worker)

`.com` runs the `cj` Worker. `.org` must use the **same Worker** or it will not share the counter.

**Option A — Dashboard (matches your screenshot):**

1. Open **abnormalobservations.org → Overview**
2. Under **Connect a Worker**, click **Connect Worker**
3. Select **`cj`** (the same Worker as `.com`)
4. Save

**Option B — Automatic on deploy:**  
`wrangler.toml` now includes routes for both `.com` and `.org`. The next deploy attaches them if both zones are in your Cloudflare account.

After connecting, verify: `https://abnormalobservations.org/api/observers`  
Should return the same count as `.com`.

## Edit your links

Open `config.js` and replace the placeholder links with:

- YouTube channel
- DON'T THINK playlist
- Amazon or sales pages for all four works
- Optional email signup

You can also change `startingObserverCount`.

## Free deployment option: Cloudflare Workers (+ static assets)

This site deploys as a **Worker with static assets** (project name: `cj`).

### Use your existing project — do not create a new one

1. Open **Workers & Pages → cj → Settings → Builds**
2. Set:

| Setting | Value |
|---|---|
| Build command | *(leave empty)* |
| Deploy command | `npx wrangler deploy` |
| Non-production branch deploy command | `npx wrangler versions upload` |
| Path / Root directory | `/` |

3. Save, then **Deployments → Retry deployment** (or push to GitHub).

### Global observer counter

Deployed automatically with the Worker via a Durable Object binding (`OBSERVER_COUNTER`). No separate KV setup is required.

After deploy, verify:

```
https://abnormalobservations.com/api/observers
```

Should return JSON like `{"count":1}`.

### Manual upload alternative

1. Create a free Cloudflare account.
2. Open **Workers & Pages**.
3. Choose **Create application → Pages → Upload assets**.
4. Upload the contents of this folder, or drag in the ZIP after extracting it.
5. Cloudflare gives you a free `pages.dev` address.
6. A custom domain can be connected later, but the domain itself is not free.

## Free deployment option: GitHub Pages

GitHub Pages can host static HTML/CSS/JavaScript from a public repository. It is best used as a project/personal site rather than as a transaction-processing storefront. Link to Amazon or another checkout provider rather than collecting payments on the site.

## Replace the video placeholder

After publishing the first video, replace the `video-placeholder` block in `begin.html` with:

```html
<iframe
  width="100%"
  height="100%"
  src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
  title="Observation One"
  frameborder="0"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  allowfullscreen>
</iframe>
```

## Recommended next upgrade

Add a real global Observer counter and optional email capture without changing the mystery-first landing page.