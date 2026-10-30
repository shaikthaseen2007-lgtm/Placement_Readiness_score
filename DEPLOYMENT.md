# Deploy ReadySet so other people can use it

The local `localhost` address is only reachable from your own computer. Public access requires deploying the frontend and API to internet hosting.

## Recommended setup
- **Frontend:** Vercel (React/Vite static site)
- **Backend + trained models:** Render (FastAPI)
- **Database:** SQLite on a Render persistent disk for this starter deployment. Keep the disk enabled; without persistent storage, accounts/history can be lost on redeploy/restart. For a larger production app, migrate to managed PostgreSQL.

## 1. Put the project on GitHub
1. Create a GitHub repository and upload the contents of this project folder.
2. Do not upload `.venv`, `node_modules`, `.env` files, API keys, or the local database.
3. The included `render.yaml` defines the API service. Render persistent disks require a paid service plan; choose a plan that supports disks if you want persistent SQLite storage.

## 2. Deploy the backend on Render
1. In Render, choose **New + → Blueprint** and connect the GitHub repository containing `render.yaml`.
2. Deploy the `readyset-placement-api` service. It installs dependencies and starts FastAPI.
3. Wait for the service to become healthy. Test `https://YOUR-BACKEND.onrender.com/api/health` and `https://YOUR-BACKEND.onrender.com/docs`.
4. Copy the backend base URL, e.g. `https://readyset-placement-api.onrender.com` (do not include `/api` yet).
5. In Render → service → Environment, set `CORS_ORIGINS` to the eventual Vercel URL, e.g. `https://readyset-placement.vercel.app`. You can temporarily include `http://localhost:5173` for local development, separated by commas. Save/redeploy after the frontend URL is known.

## 3. Deploy the frontend on Vercel
1. In Vercel, import the same GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite**. Build command: `npm run build`. Output directory: `dist`.
4. Add environment variable `VITE_API_URL` with the full API prefix, e.g. `https://readyset-placement-api.onrender.com/api`.
5. Deploy. Copy the generated Vercel URL and add that exact origin to Render's `CORS_ORIGINS`, then redeploy the backend.

## 4. Verify the public app
- Open the Vercel URL in a private/incognito browser window.
- Create a test account, complete an assessment, check the radar/bar charts, resume analyzer, roadmap, quiz, and history.
- Test the API health URL. If the frontend says “Failed to fetch”, check `VITE_API_URL`, that the backend is awake, and that `CORS_ORIGINS` exactly matches the Vercel origin (no trailing slash).

## Notes
- The trained `.joblib` models are included and loaded by the API. Predictions are estimates, not guarantees.
- Never share your local `127.0.0.1` URL as a public link; it is local to your machine.
- The bundled database is user-specific and should not be committed. The Render disk is configured at `/var/data/placement_readiness.db`.
- Before a public launch, use a unique `APP_SECRET_KEY`, HTTPS (provided by the hosts), rate limiting, backups, and managed PostgreSQL if multiple concurrent users or durable production data are important.
