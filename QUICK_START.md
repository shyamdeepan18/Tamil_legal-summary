# 🚀 QUICK START GUIDE

## Get Your MVP Running in 1 Hour!

---

## ✅ Step 1: Get FREE API Keys (15 minutes)

### 1.1 Razorpay (Required - for payments)
1. Go to: https://dashboard.razorpay.com/
2. Sign up with email
3. Go to Settings → API Keys
4. Copy **Key ID** and **Key Secret** (test mode)
5. Save these for later

### 1.2 Google Gemini (Required - for summaries, 100% FREE!)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Save for later

### 1.3 Upstash Redis (Optional - for caching)
1. Go to: https://upstash.com/
2. Sign up (free)
3. Create Redis database
4. Copy connection details
5. Save for later

---

## ✅ Step 2: Setup Backend (10 minutes)

```bash
# Navigate to backend
cd "Tamil OCR/backend"

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use any text editor
```

### Add your keys to `.env`:
```env
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
GOOGLE_API_KEY=xxxxx
ENCRYPTION_KEY=generate_this_below
```

### Generate encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and paste in `.env` as `ENCRYPTION_KEY`

---

## ✅ Step 3: Setup Frontend (5 minutes)

```bash
# Open new terminal
cd "Tamil OCR/frontend"

# Install dependencies
npm install

# Done!
```

---

## ✅ Step 4: Run Locally (2 minutes)

### Terminal 1 - Backend:
```bash
cd "Tamil OCR/backend"
source venv/bin/activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Frontend:
```bash
cd "Tamil OCR/frontend"
npm run dev
```

You should see:
```
VITE ready in 500 ms
Local: http://localhost:3000
```

---

## ✅ Step 5: Test It! (5 minutes)

1. **Open browser**: http://localhost:3000

2. **Upload a PDF**:
   - Drag and drop any PDF
   - Should show preview with document type

3. **Test Payment** (Test Mode):
   - Click "Pay ₹49"
   - Use test card: `4111 1111 1111 1111`
   - CVV: any 3 digits
   - Expiry: any future date
   - Should redirect to summary page

4. **Check Summary**:
   - Should show document analysis
   - Red flags (if any)
   - Detailed summary in Tamil + English

---

## ✅ Step 6: Deploy to Vercel (20 minutes)

### 6.1 Install Vercel CLI
```bash
npm install -g vercel
```

### 6.2 Login
```bash
vercel login
```

### 6.3 Deploy
```bash
cd "Tamil OCR"
vercel --prod
```

Follow prompts:
- Project name: `tamil-legal-docs`
- Directory: `./`
- Settings: Use defaults

### 6.4 Add Environment Variables

1. Go to: https://vercel.com/dashboard
2. Click your project
3. Go to Settings → Environment Variables
4. Add all your keys from `.env`

### 6.5 Redeploy
```bash
vercel --prod
```

---

## ✅ Step 7: Connect Domain (10 minutes)

### 7.1 Buy Domain (Namecheap)
1. Go to: https://www.namecheap.com/
2. Search for domain (e.g., `tamillegaldocs.com`)
3. Purchase (~₹500-800/year)

### 7.2 Configure DNS
1. Go to Namecheap → Domain List → Manage
2. Click "Advanced DNS"
3. Add records:
   ```
   Type: CNAME
   Host: www
   Value: cname.vercel-dns.com

   Type: A
   Host: @
   Value: 76.76.21.21
   ```

### 7.3 Add to Vercel
1. Vercel Dashboard → Your Project → Settings → Domains
2. Add domain: `yourdomain.com`
3. Add www: `www.yourdomain.com`
4. Wait 5-10 minutes for DNS propagation

---

## 🎉 You're Live!

Your app is now running at:
- **Local**: http://localhost:3000
- **Vercel**: https://your-project.vercel.app
- **Custom Domain**: https://yourdomain.com

---

## 💰 Monthly Costs

| Item | Cost |
|------|------|
| Vercel Hosting | ₹0 (free tier) |
| Google Gemini | ₹0 (free tier) |
| Domain (Namecheap) | ₹50/mo |
| **TOTAL** | **₹50/mo** |

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

### Frontend won't start
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API calls failing
- Check backend is running on port 8000
- Check `.env` file has all required keys
- Check Razorpay keys are test mode keys

### Vercel deployment fails
- Make sure `vercel.json` is in root directory
- Check `requirements.txt` is in `backend/` folder
- Verify all environment variables are set in Vercel dashboard

---

## 📞 Need Help?

1. Check `DEPLOYMENT.md` for detailed guide
2. Check `FREE_LLM_ALTERNATIVES.md` for LLM setup
3. Review error logs in terminal
4. Check Vercel deployment logs

---

## 🎯 Next Steps

1. ✅ Test with real Tamil legal documents
2. ✅ Integrate your Tamil OCR code
3. ✅ Switch Razorpay to live mode
4. ✅ Start marketing!

**You're ready to launch! 🚀**
