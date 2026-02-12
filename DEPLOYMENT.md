# 🚀 DEPLOYMENT GUIDE - Vercel + Namecheap

## Overview

- **Frontend**: Vercel (Free tier)
- **Backend**: Vercel Serverless Functions (Free tier)
- **Domain**: Namecheap
- **Database**: Supabase (Free tier) - Optional
- **Cache**: Upstash Redis (Free tier) - Optional
- **LLM**: Google Gemini Flash (FREE) or Groq (FREE)

---

## 📋 Pre-Deployment Checklist

### 1. Get Free API Keys

#### Razorpay (Required)
- Sign up: https://dashboard.razorpay.com/
- Get test keys from Settings → API Keys
- Complete KYC before going live

#### Google Gemini (Recommended - FREE)
- Go to: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy the key
- **Limits**: 15 requests/min, 1M tokens/day (enough for 1000+ docs/day)

**OR**

#### Groq (Alternative - FREE)
- Sign up: https://console.groq.com/
- Get API key
- **Limits**: 30 requests/min, 14,400 requests/day
- **Advantage**: Very fast responses

#### Upstash Redis (Optional - for caching)
- Sign up: https://upstash.com/
- Create Redis database
- Copy connection details
- **Free tier**: 10,000 commands/day

---

## 🌐 Domain Setup (Namecheap)

### 1. Purchase Domain
- Go to Namecheap.com
- Search for your domain (e.g., `tamillegaldocs.com`)
- Purchase (~₹500-800/year)

### 2. Configure DNS
After purchasing, go to Domain List → Manage → Advanced DNS:

Add these records:
```
Type: CNAME
Host: www
Value: cname.vercel-dns.com
TTL: Automatic

Type: A
Host: @
Value: 76.76.21.21
TTL: Automatic
```

---

## 🚀 Vercel Deployment

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy Frontend

```bash
cd frontend
vercel --prod
```

Follow prompts:
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name? **tamil-legal-docs**
- Directory? **./frontend**
- Override settings? **N**

### Step 4: Add Environment Variables

Go to Vercel Dashboard → Your Project → Settings → Environment Variables

Add these:

```
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxx
GOOGLE_API_KEY=xxxxx
ENCRYPTION_KEY=xxxxx
```

### Step 5: Connect Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your Namecheap domain: `tamillegaldocs.com`
3. Add www subdomain: `www.tamillegaldocs.com`
4. Vercel will auto-configure SSL (HTTPS)

### Step 6: Redeploy

```bash
vercel --prod
```

---

## 💰 Cost Breakdown (Monthly)

### FREE Tier (Recommended for MVP)

| Service | Cost | Limits |
|---------|------|--------|
| Vercel Hosting | ₹0 | 100GB bandwidth, 100 serverless executions |
| Google Gemini | ₹0 | 1M tokens/day (~1000 docs) |
| Namecheap Domain | ₹50/mo | (₹600/year) |
| Upstash Redis | ₹0 | 10K commands/day |
| **TOTAL** | **₹50/mo** | **Perfect for MVP** |

### Paid Tier (If you exceed free limits)

| Service | Cost | Limits |
|---------|------|--------|
| Vercel Pro | ₹1,650/mo | Unlimited bandwidth |
| OpenAI GPT-4o-mini | ₹0.15/doc | ~₹450/mo for 100 docs/day |
| Supabase Pro | ₹2,100/mo | 8GB database |
| **TOTAL** | **₹4,200/mo** | **For scale** |

---

## 🔧 Backend Deployment (Vercel Serverless)

Vercel automatically deploys your FastAPI backend as serverless functions.

### File Structure for Vercel:

```
Tamil OCR/
├── vercel.json          ✅ Already created
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── frontend/
    └── ...
```

### Vercel Configuration (`vercel.json`):

Already created! It tells Vercel to:
1. Deploy backend as Python serverless function
2. Route `/api/*` requests to backend
3. Load environment variables

---

## 🧪 Testing Deployment

### 1. Test Frontend
```
https://your-project.vercel.app
```

### 2. Test Backend API
```
https://your-project.vercel.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "tamil-legal-doc-summarizer",
  "version": "1.0.0"
}
```

### 3. Test Upload Flow
1. Upload a PDF
2. Check if preview appears
3. Test payment (use Razorpay test cards)
4. Verify summary generation

---

## 📊 Monitoring & Analytics

### Free Tools:

1. **Vercel Analytics** (Built-in)
   - Page views
   - Performance metrics
   - Error tracking

2. **Google Analytics** (Free)
   - Add tracking code to `frontend/index.html`

3. **Sentry** (Free tier)
   - Error tracking
   - 5,000 events/month free

---

## 🔐 Security Checklist

- [ ] Environment variables set in Vercel (not in code)
- [ ] HTTPS enabled (automatic with Vercel)
- [ ] Razorpay webhook signature verification enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] File upload size limits enforced

---

## 🚨 Common Issues & Solutions

### Issue: "Module not found" error
**Solution**: Make sure `requirements.txt` is in `backend/` folder

### Issue: API routes not working
**Solution**: Check `vercel.json` routes configuration

### Issue: Environment variables not loading
**Solution**: Redeploy after adding env vars in Vercel dashboard

### Issue: Gemini API rate limit exceeded
**Solution**: 
- Implement request queue
- Or switch to Groq (30 req/min vs Gemini's 15)
- Or upgrade to paid tier

---

## 📈 Scaling Strategy

### When to Upgrade:

**Month 1** (Free tier):
- 0-50 docs/day
- Cost: ₹50/mo (domain only)

**Month 2-3** (Still free tier):
- 50-500 docs/day
- Cost: ₹50/mo
- Gemini free tier handles this easily

**Month 4+** (Consider paid):
- 500+ docs/day
- Upgrade to Vercel Pro: ₹1,650/mo
- Consider OpenAI for better quality: +₹450/mo
- Add Supabase for Pro features: +₹2,100/mo

---

## 🎯 Next Steps

1. **Get API Keys** (30 mins)
   - Razorpay test keys
   - Google Gemini API key
   - Upstash Redis (optional)

2. **Deploy to Vercel** (15 mins)
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configure Domain** (10 mins)
   - Add DNS records in Namecheap
   - Connect domain in Vercel

4. **Test Everything** (30 mins)
   - Upload test documents
   - Test payment flow
   - Verify summary generation

5. **Go Live!** 🚀
   - Switch Razorpay to live mode
   - Start marketing

---

## 💡 Pro Tips

1. **Use Gemini Flash**: It's free and good enough for MVP
2. **Monitor Usage**: Check Vercel analytics daily
3. **Collect Feedback**: Add feedback form in summary page
4. **Optimize Costs**: Only upgrade when you hit limits
5. **Cache Aggressively**: Use Redis to reduce LLM calls

---

## 📞 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Gemini API**: https://ai.google.dev/docs
- **Razorpay Docs**: https://razorpay.com/docs/
- **Namecheap Support**: https://www.namecheap.com/support/

---

**You're ready to deploy! 🎉**

Total setup time: ~1-2 hours
Monthly cost: ₹50 (domain only)
