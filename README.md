# Abnormal Observations — Website Starter

## What it includes

- Mystery-first landing page
- Observer count
- "Become One" interaction
- First observation page
- Four-book pathway
- Mobile-responsive layout
- No framework, database, or paid software required

## Important note about the counter

The observer count is a **shared global counter** powered by a Cloudflare Durable Object (`/api/observers`).

- Every visitor sees the same public total.
- A first homepage visit (visible tab, JavaScript on) automatically claims the next Observer number after a short delay.
- **Become One** claims immediately if auto-join has not finished yet, or continues into the site once assigned.
- Cloudflare page views alone are not the same as observer designations — bots and bounced hits do not all become numbers.
- Verify live: `GET https://abnormalobservations.com/api/observers`

`STARTING_OBSERVER_COUNT` in `wrangler.toml` seeds the counter the first time it is created.

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