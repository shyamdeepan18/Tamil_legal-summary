# Hosting & Testing Guide

## ⚠️ Prerequisite Checks

### 1. Database (Crucial)
You are using a serverless environment (Vercel). You **CANNOT** use SQLite (local file) for the database because Vercel files are read-only and ephemeral.
**You MUST use Supabase (PostgreSQL).**
*   Ensure you have your Supabase connection string: `postgresql://postgres:[PASSWORD]@db.supabase.co:5432/postgres`

### 2. OCR Limitations
Vercel Serverless Function size limit is 250MB. Heavy AI libraries like `torch` (PyTorch) or `ocr_tamil` often exceed this.
**The Current Setup**: We have configured the app to use a lightweight fallback (`PyPDF2`) if the heavy OCR is missing. This means:
*   **Works**: Digital PDFs (text selectable).
*   **Won't Work**: Scanned images (will return "insufficient text" error).
*   **Solution**: For full scan support, you would need to host the backend on a container platform like **Render**, **Railway**, or **AWS**, OR use the Google Gemini API directly for text extraction (multimodal).

---

## 🚀 Step 1: Deploy Backend (API)

We will deploy the backend as a separate service first.

1.  **Prepare Environment**:
    We have optimized `requirements.txt` to exclude heavy libraries for Vercel compatibility.

2.  **Deploy via Vercel CLI**:
    Run this in your terminal from the root folder (`Tamil OCR/`):
    ```bash
    npm i -g vercel  # Install Vercel CLI if missing (requires Node)
    # Since you don't have Node installed locally, use the web dashboard:
    ```

    **Web Dashboard Method (Recommended for you):**
    1.  Push your code to **GitHub**.
    2.  Go to [Vercel Dashboard](https://vercel.com/new).
    3.  Import your repository `Tamil-OCR`.
    4.  **Project Name**: `tamil-ocr-backend`
    5.  **Root Directory**: Leave as `./`
    6.  **Framework Preset**: Select "Other" -> It should detect Python or use `vercel.json` configuration automatically.
    7.  **Environment Variables**: Add these in the Vercel UI:
        *   `DATABASE_URL`: `postgresql://...` (Your Supabase URL)
        *   `RAZORPAY_KEY_ID`: `...`
        *   `RAZORPAY_KEY_SECRET`: `...`
        *   `GOOGLE_API_KEY`: `...` (For Gemini)
    8.  Click **Deploy**.

    *Note: If build fails due to missing `ocr_tamil`, ensure `requirements.txt` has commented out `ocr_tamil` or it is handled gracefully.*

---

## 🌐 Step 2: Deploy Frontend

Now we deploy the UI and connect it to the Backend.

1.  **Update Config**:
    In `frontend/vite.config.js`, the proxy points to `localhost:8000`. In production, Vite needs the real backend URL.
    *   Create a file `.env.production` in `frontend/` folder with:
        ```
        VITE_API_URL=https://tamil-ocr-backend.vercel.app/api
        ```
    *   Update your `App.jsx` or API calls to use this `import.meta.env.VITE_API_URL` prefix instead of relative paths, OR configure Vercel Rewrites in `frontend/vercel.json`.

2.  **Deploy via Vercel**:
    1.  Go to Vercel Dashboard -> **Add New Project**.
    2.  Import the **SAME repository**.
    3.  **Project Name**: `tamil-ocr-frontend`
    4.  **Root Directory**: Click "Edit" and select `frontend`.
    5.  **Framework Preset**: Vite (should auto-detect).
    6.  **Environment Variables**:
        *   `VITE_API_URL`: The URL from Step 1 (e.g., `https://tamil-ocr-backend.vercel.app`)
    7.  Click **Deploy**.

---

## 🧪 How to Test (Locally & Remote)

### Local Testing (Backend Only)
Since instructions showed you don't have `Node.js` installed, you cannot run the frontend locally. However, the backend is **currently running** on your machine at port 8000.

**Test Health**:
```bash
curl http://localhost:8000/health
```

**Test User Logic**:
You can use `curl` or Postman to test endpoints:
```bash
# Get Root
curl http://localhost:8000/

# Create Order (Mock)
curl -X POST http://localhost:8000/api/create-order \
   -H "Content-Type: application/json" \
   -d '{"amount": 4900, "user_id": "test_user", "upload_id": "test_doc", "plan": "quick_check"}'
```

### Full Testing
Once deployed to Vercel:
1.  Open your frontend URL (`https://tamil-ocr-frontend.vercel.app`).
2.  Upload a **Digital PDF** (not scanned) to test the flow.
3.  The backend `PyPDF2` fallback should extract text.
4.  Proceed to the logic.

---

## 🛠️ Pending Actions for You
1.  **Push to GitHub**: Essential for Vercel deployment.
2.  **Get Supabase URL**: You need the connection string.
3.  **Install Node.js** (Optional): If you want to develop the frontend locally later.
