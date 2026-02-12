import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn, Mail, Phone, ArrowRight, CheckCircle } from 'lucide-react'

export default function LoginPage() {
    const navigate = useNavigate()
    const [method, setMethod] = useState('email') // email, phone
    const [step, setStep] = useState(1) // 1: Input, 2: OTP
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    // Inputs
    const [email, setEmail] = useState('')
    const [phone, setPhone] = useState('')
    const [otp, setOtp] = useState('')
    const [userId, setUserId] = useState(null)
    const [rememberMe, setRememberMe] = useState(true)

    const handleSendOtp = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const endpoint = method === 'email' ? '/api/auth/login/email' : '/api/auth/login/phone'
            const body = method === 'email' ? { email } : { phone }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            })

            const data = await response.json()

            if (!response.ok) throw new Error(data.detail || 'Login failed')

            setUserId(data.user_id)
            setStep(2)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleVerifyOtp = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const deviceFingerprint = "browser-" + Date.now()

            const response = await fetch('/api/auth/verify-login-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    otp_type: method === 'email' ? 'email_login' : 'phone_login',
                    otp: otp,
                    device_fingerprint: deviceFingerprint,
                    remember_me: rememberMe
                })
            })

            const data = await response.json()

            if (!response.ok) throw new Error(data.detail || 'Verification failed')

            // Success
            localStorage.setItem('token', data.session_token)
            localStorage.setItem('user', JSON.stringify(data.user))

            navigate('/dashboard')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleGoogleLogin = () => {
        // Redirect to backend endpoint
        window.location.href = 'http://localhost:8000/api/auth/google/login'
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <LogIn className="w-12 h-12 text-primary mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900">Welcome Back</h2>
                    <p className="text-gray-600">Access your saved summaries</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-center">
                        {error}
                    </div>
                )}

                {/* Method Tabs */}
                {step === 1 && (
                    <div className="flex border-b mb-6">
                        <button
                            className={`flex-1 py-2 text-center font-medium ${method === 'email' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                            onClick={() => setMethod('email')}
                        >
                            Email
                        </button>
                        <button
                            className={`flex-1 py-2 text-center font-medium ${method === 'phone' ? 'text-primary border-b-2 border-primary' : 'text-gray-500 hover:text-gray-700'}`}
                            onClick={() => setMethod('phone')}
                        >
                            Phone
                        </button>
                    </div>
                )}

                {step === 1 ? (
                    <form onSubmit={handleSendOtp} className="space-y-4">
                        {method === 'email' ? (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                                <div className="relative">
                                    <Mail className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                    <input
                                        type="email"
                                        required
                                        className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                                        placeholder="you@example.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </div>
                        ) : (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                                <div className="relative">
                                    <Phone className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                    <input
                                        type="tel"
                                        required
                                        className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                                        placeholder="+91 98765 43210"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                    />
                                </div>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-primary text-white py-2 rounded-lg font-bold hover:bg-opacity-90 transition-colors flex items-center justify-center"
                        >
                            {loading ? 'Sending OTP...' : 'Send OTP'}
                            {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
                        </button>

                        <div className="relative my-6">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-300"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-2 bg-white text-gray-500">Or continue with</span>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={handleGoogleLogin}
                            className="w-full border border-gray-300 bg-white text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center"
                        >
                            <img src="https://www.google.com/favicon.ico" alt="Google" className="w-4 h-4 mr-2" />
                            Google
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} className="space-y-6">
                        <div className="text-center text-sm text-gray-600 mb-4">
                            Enter the OTP sent to {method === 'email' ? email : phone}
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="ml-2 text-primary hover:underline"
                            >
                                Change
                            </button>
                        </div>

                        <div>
                            <input
                                type="text"
                                required
                                maxLength="6"
                                className="w-full px-3 py-2 border rounded-lg text-center tracking-widest text-xl font-mono focus:ring-2 focus:ring-primary"
                                placeholder="000000"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                            />
                        </div>

                        <div className="flex items-center">
                            <input
                                id="remember_me"
                                type="checkbox"
                                className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                                checked={rememberMe}
                                onChange={(e) => setRememberMe(e.target.checked)}
                            />
                            <label htmlFor="remember_me" className="ml-2 block text-sm text-gray-900">
                                Remember me
                            </label>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-green-600 text-white py-2 rounded-lg font-bold hover:bg-green-700 transition-colors flex items-center justify-center"
                        >
                            {loading ? 'Verifying...' : 'Login'}
                            {!loading && <CheckCircle className="w-4 h-4 ml-2" />}
                        </button>
                    </form>
                )}

                <div className="mt-6 text-center text-sm">
                    <p className="text-gray-600">
                        Don't have an account?{' '}
                        <Link to="/signup" className="text-primary hover:underline font-semibold">
                            Create Free Account
                        </Link>
                    </p>
                    <div className="mt-2">
                        <Link to="/forgot-password" className="text-gray-500 hover:text-gray-700">
                            Forgot Password?
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
