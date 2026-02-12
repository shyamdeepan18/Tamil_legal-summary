# Tamil Legal Document Summarizer MVP

A privacy-focused Tamil legal document analysis platform that helps users understand legal documents in simple Tamil and English.

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run server
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📋 Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Razorpay
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# OpenAI
OPENAI_API_KEY=your_openai_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Encryption
ENCRYPTION_KEY=your_fernet_key
```

## 🏗️ Project Structure

```
Tamil OCR/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── api/
│   │   ├── upload.py           # File upload endpoint
│   │   ├── payment.py          # Razorpay integration
│   │   └── summary.py          # Summary retrieval
│   └── services/
│       ├── ocr_service.py      # Tamil OCR processing
│       ├── classifier.py       # Document classification
│       ├── preview_generator.py # Pre-payment preview
│       ├── red_flags.py        # Red flags detection
│       └── llm_service.py      # LLM summarization
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── UploadPage.jsx  # Main upload page
    │   │   └── SummaryPage.jsx # Summary display
    │   └── components/
    │       ├── FileUpload.jsx  # Drag-and-drop upload
    │       ├── PreviewModal.jsx # Preview before payment
    │       └── PaymentButton.jsx # Razorpay payment
    └── package.json
```

## 🔑 Key Features

- **Privacy-First**: Auto-delete documents after 15 minutes
- **Pre-Payment Preview**: See document quality before paying
- **Red Flags Detection**: Automatic detection of concerning patterns
- **Bilingual**: Tamil + English mixed naturally
- **Document Types**: Sale Deeds, Agreements, EC, POA, Court Orders, etc.
- **Pricing**: ₹49 Quick Check | ₹99 Standard | ₹1,999/mo Pro

## 📝 API Endpoints

- `POST /api/upload` - Upload and validate PDF
- `POST /api/create-order` - Create Razorpay order
- `POST /api/verify-payment` - Verify payment
- `GET /api/summary/{upload_id}` - Get summary
- `POST /api/webhook` - Razorpay webhook

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

### Backend (Recommended: AWS Mumbai / Google Cloud India)

```bash
# Using Docker
docker build -t tamil-doc-backend .
docker run -p 8000:8000 tamil-doc-backend

# Or using PM2
pm2 start main.py --name tamil-doc-api
```

### Frontend

```bash
# Build for production
npm run build

# Deploy to Vercel/Netlify
# Or serve with nginx
```

## 📊 Success Metrics

| Metric | Week 1 | Month 1 | Month 3 |
|--------|--------|---------|---------|
| Uploads | 50 | 500 | 2,000 |
| Paid Conversions | 10 | 100 | 500 |
| Revenue | ₹500 | ₹11,000 | ₹60,000 |

## ⚠️ Important Notes

1. **OCR Integration**: Replace placeholder OCR in `services/ocr_service.py` with your Tamil OCR code
2. **Razorpay**: Complete KYC before going live
3. **Privacy**: Ensure cleanup cron runs every 5 minutes
4. **Disclaimer**: Always display "not legal advice" prominently

## 📞 Support

For issues or questions, contact: [your-email]

## 📄 License

Proprietary - All rights reserved
