# MAMA-LENS AI — Deployment Guide
## Netlify (Frontend) + Render (Backend) + MongoDB Atlas

---

## Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — MAMA-LENS AI"
git remote add origin https://github.com/YOUR_USERNAME/mama-lens-ai.git
git push -u origin main
```

---

## Step 2 — Deploy Backend on Render

1. Go to **https://render.com** → Sign up / Log in
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Configure:

| Setting | Value |
|---|---|
| **Name** | `mamalens-api` |
| **Root Directory** | `backend/api` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

5. Click **Advanced** → **Add Environment Variables**:

| Key | Value |
|---|---|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `MONGODB_URI` | `mongodb://BrianGithinji:BrianMAMA@ac-d88dmls-shard-00-00...` (your Atlas URI) |
| `MONGODB_DB_NAME` | `mamalens` |
| `SECRET_KEY` | *(click Generate)* |
| `JWT_SECRET_KEY` | *(click Generate)* |
| `ALLOWED_ORIGINS` | `["https://YOUR-SITE.netlify.app"]` |

6. Click **Deploy** — wait ~3 minutes
7. Copy your service URL e.g. `https://mamalens-api.onrender.com`

---

## Step 3 — Update Frontend API URL

Edit `apps/web/.env.production`:
```
VITE_API_URL=https://mamalens-api.onrender.com/api/v1
```

Commit and push:
```bash
git add apps/web/.env.production
git commit -m "Set Render API URL"
git push
```

---

## Step 4 — Deploy Frontend on Netlify

1. Go to **https://netlify.com** → **Add new site** → **Import from Git**
2. Connect GitHub → select your repo
3. Build settings (auto-detected from `netlify.toml`):

| Setting | Value |
|---|---|
| **Base directory** | `apps/web` |
| **Build command** | `npm run build` |
| **Publish directory** | `dist` |

4. Click **Deploy site**
5. Your site is live at `https://random-name.netlify.app`

---

## Step 5 — Update CORS on Render

In Render dashboard → your service → Environment:

```
ALLOWED_ORIGINS = ["https://your-site.netlify.app"]
```

Render auto-redeploys.

---

## Verify

```
https://mama-lens-ai.onrender.com/health
```
→ `{"status":"healthy","database":"MongoDB Atlas","db_ready":true}` ✅ **LIVE**

Then open your Netlify URL and register.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| CORS error | Update `ALLOWED_ORIGINS` on Render with exact Netlify URL |
| Backend sleeping | Free tier sleeps after 15 min. First request takes ~30s. Upgrade to Starter ($7/mo) |
| MongoDB connection failed | Check `MONGODB_URI` is set correctly in Render env vars |
| Build fails on Netlify | Ensure `VITE_API_URL` is set in `apps/web/.env.production` |
