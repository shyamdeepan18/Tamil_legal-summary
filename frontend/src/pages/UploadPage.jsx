import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, Shield, CheckCircle, AlertCircle } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import PreviewModal from '../components/PreviewModal'
import PasswordPrompt from '../components/PasswordPrompt'
import PaymentButton from '../components/PaymentButton'
import heroBg from '../assets/hero-bg.png'

export default function UploadPage() {
    const [uploadState, setUploadState] = useState('idle') // idle, uploading, preview, processing, password_required
    const [previewData, setPreviewData] = useState(null)
    const [error, setError] = useState(null)
    const [currentFile, setCurrentFile] = useState(null)
    const [passwordError, setPasswordError] = useState(null)
    const navigate = useNavigate()

    const handleFileSelect = async (file, password = null) => {
        setUploadState('uploading')
        setError(null)
        setPasswordError(null)

        // Store file for retry with password
        if (!currentFile) {
            setCurrentFile(file)
        }

        const formData = new FormData()
        formData.append('file', file)
        if (password) {
            formData.append('password', password)
        }

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            })

            const data = await response.json()

            if (!response.ok) {
                // Check if password is required
                if (data.detail?.requires_password) {
                    setUploadState('password_required')
                    if (password) {
                        // Incorrect password
                        setPasswordError(data.detail?.message || 'Incorrect password')
                    }
                    return
                }

                throw new Error(data.detail?.message || 'Upload failed')
            }

            // Show preview
            setPreviewData(data)
            setUploadState('preview')
            setCurrentFile(null) // Clear stored file
        } catch (err) {
            setError(err.message)
            setUploadState('idle')
            setCurrentFile(null)
        }
    }

    const handlePasswordSubmit = async (password) => {
        if (currentFile) {
            await handleFileSelect(currentFile, password)
        }
    }

    const handlePasswordCancel = () => {
        setUploadState('idle')
        setCurrentFile(null)
        setPasswordError(null)
    }

    const handlePaymentSuccess = (uploadId) => {
        setUploadState('processing')
        // Navigate to summary page
        navigate(`/summary/${uploadId}`)
    }



    return (
        <div
            className="min-h-screen bg-cover bg-center bg-fixed"
            style={{
                backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), url(${heroBg})`
            }}
        >
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <FileText className="w-8 h-8 text-primary" />
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">
                                    Tamil Legal Document Summarizer
                                </h1>
                                <p className="text-sm text-gray-600 tamil-text">
                                    தமிழ் சட்ட ஆவண சுருக்கம்
                                </p>
                            </div>
                        </div>
                        {localStorage.getItem('token') ? (
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="text-primary hover:text-opacity-80 font-semibold"
                            >
                                Dashboard
                            </button>
                        ) : (
                            <button
                                onClick={() => navigate('/login')}
                                className="text-primary hover:text-opacity-80 font-semibold"
                            >
                                Login
                            </button>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
                {/* Hero Section */}
                <div className="text-center mb-12">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                        📄 Understand Your Legal Documents in 60 Seconds
                    </h2>
                    <p className="text-xl text-gray-600 mb-2">
                        Upload → ₹49 → Get Summary
                    </p>
                    <p className="text-lg text-gray-500 tamil-text">
                        உங்கள் சட்ட ஆவணங்களை 60 வினாடிகளில் புரிந்து கொள்ளுங்கள்
                    </p>
                </div>

                {/* Upload Section */}
                <div className="max-w-3xl mx-auto">
                    <FileUpload
                        onFileSelect={handleFileSelect}
                        isUploading={uploadState === 'uploading'}
                        error={error}
                    />

                    {/* Trust Signals */}
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="flex items-start space-x-3">
                            <Shield className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                            <div>
                                <h3 className="font-semibold text-gray-900">Auto-Deleted</h3>
                                <p className="text-sm text-gray-600">
                                    Your document is deleted after 15 minutes
                                </p>
                                <p className="text-sm text-gray-500 tamil-text">
                                    15 நிமிடங்களில் தானாக நீக்கப்படும்
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-3">
                            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                            <div>
                                <h3 className="font-semibold text-gray-900">No Storage</h3>
                                <p className="text-sm text-gray-600">
                                    We don't store your PDFs permanently
                                </p>
                                <p className="text-sm text-gray-500 tamil-text">
                                    நிரந்தர சேமிப்பு இல்லை
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-3">
                            <AlertCircle className="w-6 h-6 text-blue-500 flex-shrink-0 mt-1" />
                            <div>
                                <h3 className="font-semibold text-gray-900">Red Flags Detection</h3>
                                <p className="text-sm text-gray-600">
                                    Automatic detection of concerning patterns
                                </p>
                                <p className="text-sm text-gray-500 tamil-text">
                                    சிக்கல்களை தானாக கண்டறியும்
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Pricing Cards */}
                    <div className="mt-12">
                        <h3 className="text-2xl font-bold text-center mb-6">💰 Flexible Pricing Plans</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {/* Free Trial */}
                            <div className="card border-2 border-gray-200 hover:border-gray-300 transition-all duration-300 bg-white">
                                <div className="text-center p-4">
                                    <h4 className="text-lg font-bold mb-2">Free Trial</h4>
                                    <p className="text-3xl font-bold text-gray-500 mb-4">₹0</p>
                                    <ul className="text-sm text-left space-y-3 mb-6">
                                        <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> 2 pages / per user</li>
                                        <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Basic Summary</li>
                                        <li className="flex items-center"><span className="text-red-500 mr-2">✗</span> No history saved</li>
                                    </ul>
                                    <button
                                        onClick={() => navigate('/signup')}
                                        className="w-full py-2 rounded-lg bg-gray-100 text-gray-700 font-semibold hover:bg-gray-200 transition-colors"
                                    >
                                        Try for Free
                                    </button>
                                </div>
                            </div>

                            {/* Quick Check */}
                            <div className="card border-2 border-primary shadow-xl transform scale-105 relative z-10 bg-white">
                                <div className="absolute top-0 right-0 bg-primary text-white px-3 py-1 text-xs font-bold rounded-bl-lg">
                                    POPULAR
                                </div>
                                <div className="text-center p-4">
                                    <h4 className="text-lg font-bold mb-2 text-primary">Quick Check</h4>
                                    <p className="text-3xl font-bold text-gray-900 mb-4">₹49<span className="text-sm text-gray-500 font-normal"> / doc</span></p>
                                    <ul className="text-sm text-left space-y-3 mb-6">
                                        <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Single Document</li>
                                        <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Red Flags Detection</li>
                                        <li className="flex items-center"><span className="text-green-500 mr-2">✓</span> Tamil+English Summary</li>
                                        <li className="flex items-center"><span className="text-red-500 mr-2">✗</span> No history saved</li>
                                    </ul>
                                    <PaymentButton
                                        amount={4900}
                                        plan="quick_check"
                                        className="w-full py-2 rounded-lg bg-primary text-white font-semibold hover:bg-opacity-90 transition-colors shadow-lg"
                                    >
                                        Check Now
                                    </PaymentButton>
                                </div>
                            </div>

                            {/* Monthly Pack */}
                            <div className="card border-2 border-secondary hover:shadow-lg transition-all duration-300 bg-white">
                                <div className="text-center p-4">
                                    <h4 className="text-lg font-bold mb-2 text-secondary">Monthly Pack</h4>
                                    <p className="text-3xl font-bold text-gray-900 mb-4">₹499<span className="text-sm text-gray-500 font-normal"> / mo</span></p>
                                    <ul className="text-sm text-left space-y-3 mb-6">
                                        <li className="flex items-center"><span className="text-secondary mr-2">✦</span> 15 Documents</li>
                                        <li className="flex items-center"><span className="text-secondary mr-2">✦</span> 30 Days Validity</li>
                                        <li className="flex items-center"><span className="text-secondary mr-2">✦</span> Save 33%</li>
                                        <li className="flex items-center"><span className="text-red-500 mr-2">✗</span> No history saved</li>
                                    </ul>
                                    <PaymentButton
                                        amount={49900}
                                        plan="monthly_pack"
                                        className="w-full py-2 rounded-lg bg-secondary text-white font-semibold hover:bg-opacity-90 transition-colors"
                                    >
                                        Get Monthly Pack
                                    </PaymentButton>
                                </div>
                            </div>

                            {/* Pro (Brokers) */}
                            <div className="card border border-gray-200 hover:border-gray-800 transition-all duration-300 bg-gray-50">
                                <div className="text-center p-4">
                                    <h4 className="text-lg font-bold mb-2 text-gray-800">Pro (Brokers)</h4>
                                    <p className="text-3xl font-bold text-gray-900 mb-4">₹1,999<span className="text-sm text-gray-500 font-normal"> / mo</span></p>
                                    <ul className="text-sm text-left space-y-3 mb-6">
                                        <li className="flex items-center"><span className="text-gray-800 mr-2">★</span> Unlimited / 200 Docs</li>
                                        <li className="flex items-center"><span className="text-gray-800 mr-2">★</span> Comparison Table</li>
                                        <li className="flex items-center"><span className="text-gray-800 mr-2">★</span> History & Search</li>
                                        <li className="text-xs text-blue-600 mt-2">Ideal for Lawyers, Govt Officers & Professionals</li>
                                    </ul>
                                    <PaymentButton
                                        amount={199900}
                                        plan="premium"
                                        className="w-full py-2 rounded-lg bg-gray-800 text-white font-semibold hover:bg-opacity-90 transition-colors"
                                    >
                                        Go Pro
                                    </PaymentButton>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Testimonials */}
                    <div className="mt-12 bg-white rounded-lg shadow-md p-8">
                        <h3 className="text-xl font-bold text-center mb-6">💬 What Users Say</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="border-l-4 border-primary pl-4">
                                <p className="text-gray-700 mb-2">
                                    "Found a court case I didn't know about! Saved me from a bad purchase."
                                </p>
                                <p className="text-sm text-gray-500">- Ramesh K., Chennai</p>
                            </div>
                            <div className="border-l-4 border-primary pl-4">
                                <p className="text-gray-700 mb-2">
                                    "Saved ₹5,000 on lawyer fees. Quick and accurate!"
                                </p>
                                <p className="text-sm text-gray-500">- Priya S., Coimbatore</p>
                            </div>
                        </div>
                    </div>

                    {/* Supported Documents */}
                    <div className="mt-8 text-center text-sm text-gray-600">
                        <p className="font-semibold mb-2">Supported Documents:</p>
                        <p>
                            Sale Deeds (விற்பனை பத்திரம்) • Agreements (ஒப்பந்தம்) •
                            Encumbrance Certificates • Power of Attorney • Court Orders •
                            Loan/Lease Documents
                        </p>
                    </div>
                </div>
            </main>

            {/* Preview Modal */}
            {uploadState === 'preview' && previewData && (
                <PreviewModal
                    data={previewData}
                    onClose={() => {
                        setUploadState('idle')
                        setPreviewData(null)
                    }}
                    onPaymentSuccess={handlePaymentSuccess}
                />
            )}

            {/* Password Prompt Modal */}
            {uploadState === 'password_required' && (
                <PasswordPrompt
                    onSubmit={handlePasswordSubmit}
                    onCancel={handlePasswordCancel}
                    error={passwordError}
                />
            )}

            {/* Footer */}
            <footer className="mt-20 bg-gray-900 text-white py-8">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <p className="text-sm">
                        ⚖️ Disclaimer: This is automated analysis, not legal advice.
                        Consult a lawyer for important decisions.
                    </p>
                    <p className="text-xs text-gray-400 mt-2 tamil-text">
                        இது தானியங்கி பகுப்பாய்வு, சட்ட ஆலோசனை அல்ல
                    </p>
                    <div className="mt-4 space-x-4 text-sm">
                        <a href="/privacy" className="hover:text-primary">Privacy Policy</a>
                        <a href="/terms" className="hover:text-primary">Terms of Service</a>
                        <a href="/refund" className="hover:text-primary">Refund Policy</a>
                    </div>
                </div>
            </footer>
        </div>
    )
}
