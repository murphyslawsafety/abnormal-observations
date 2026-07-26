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

The included counter works inside each visitor's browser. It is suitable for previewing the experience, but it is **not yet a shared global counter**.

A real global count requires a tiny free database or serverless function. The cleanest next step is Cloudflare Pages + a free Worker/KV or Supabase. Do not publicly advertise the browser-only count as a verified worldwide number.

## Edit your links

Open `config.js` and replace the placeholder links with:

- YouTube channel
- DON'T THINK playlist
- Amazon or sales pages for all four works
- Optional email signup

You can also change `startingObserverCount`.

## Free deployment option: Cloudflare Pages

This repo is a **Pages** project (static site + `/functions` API), not a Worker.

### Git-connected build settings

In **Workers & Pages → your project → Settings → Builds**:

| Setting | Value |
|---|---|
| Build command | *(leave empty)* |
| Deploy command | `npx wrangler pages deploy .` |
| Non-production branch deploy command | `npx wrangler pages deploy .` |
| Path / Root directory | `/` |

Do **not** use `npx wrangler deploy` — that is for Workers and will fail.

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