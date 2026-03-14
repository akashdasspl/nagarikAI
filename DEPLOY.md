# NagarikAI Platform — Deployment Guide

This guide covers deploying the backend to Railway and the frontend to Vercel.

---

## Backend — Railway

### 1. Sign up & connect repo
1. Go to [railway.app](https://railway.app) and sign up (GitHub login recommended).
2. Click **New Project → Deploy from GitHub repo** and select this repository.
3. Set the **Root Directory** to `backend`.

### 2. Set environment variables
In the Railway project dashboard → **Variables**, add:

| Variable | Value |
|----------|-------|
| `PORT` | `8000` (Railway sets this automatically) |

No other env vars are required for the MVP demo (uses in-memory data).

### 3. Deploy
Railway will auto-detect the `Procfile` and `railway.json` and start the build.
The build command installs `requirements.txt`; the start command runs:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Get the public URL
After deployment, Railway shows a public URL like:
```
https://nagarik-ai-backend-production.up.railway.app
```
Copy this — you'll need it for the frontend.

---

## Frontend — Vercel

### 1. Sign up & connect repo
1. Go to [vercel.com](https://vercel.com) and sign up (GitHub login recommended).
2. Click **Add New → Project** and import this repository.
3. Set the **Root Directory** to `frontend`.

### 2. Set environment variables
In the Vercel project settings → **Environment Variables**, add:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Railway backend URL, e.g. `https://nagarik-ai-backend-production.up.railway.app` |

### 3. Deploy
Vercel auto-detects Vite. The build command is `npm run build` and the output directory is `dist`.

The `vercel.json` rewrites `/api/*` requests to your backend URL, so the frontend
never needs to be rebuilt when the backend URL changes — just update the env var and redeploy.

### 4. Get the public URL
After deployment, Vercel provides a URL like:
```
https://nagarik-ai-platform.vercel.app
```

---

## Update CORS for production

Before deploying, add your Vercel URL to the CORS `allow_origins` list in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://nagarik-ai-platform.vercel.app",  # add your Vercel URL
    ],
    ...
)
```

Redeploy the backend after this change.

---

## Testing the deployed demo

1. Open the Vercel URL in a browser.
2. Check the backend health endpoint directly:
   ```
   https://<your-railway-url>/api/health
   ```
   Expected response: `{"status":"healthy", ...}`
3. Test each feature tab in the UI:
   - **Beneficiary Discovery** — submit a sample death record
   - **Grievance Portal** — submit a Hindi or English grievance
   - **Operator Assistant** — fill in an application form and check the risk score
4. Check the Railway logs for any backend errors.

---

## Local development (unchanged)

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api/*` to `http://localhost:8000` by default
(falls back when `VITE_API_URL` is not set).
