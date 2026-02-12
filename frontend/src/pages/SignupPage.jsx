import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UserPlus, Mail, Phone, MapPin, Briefcase, CheckCircle, ArrowRight } from 'lucide-react'

export default function SignupPage() {
    const navigate = useNavigate()
    const [step, setStep] = useState(1) // 1: Details, 2: Verification
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    // Form State
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        phone: '',
        city: '',
        profession: ''
    })

    // OTP State
    const [otpData, setOtpData] = useState({
        email_otp: '',
        phone_otp: '',
        user_id: null
    })

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value })
    }

    const handleSignup = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            // Get device fingerprint (placeholder for now)
            const deviceFingerprint = "browser-" + Date.now()

            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...formData,
                    device_fingerprint: deviceFingerprint
                })
            })

            const data = await response.json()

            if (!response.ok) throw new Error(data.detail || 'Signup failed')

            setOtpData({ ...otpData, user_id: data.user_id })
            setStep(2) // Move to OTP step
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleVerifyParams = (e) => {
        setOtpData({ ...otpData, [e.target.name]: e.target.value })
    }

    const handleVerify = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: otpData.user_id,
                    email_otp: otpData.email_otp,
                    phone_otp: otpData.phone_otp
                })
            })

            const data = await response.json()

            if (!response.ok) throw new Error(data.detail || 'Verification failed')

            // Success! Store token and redirect
            localStorage.setItem('token', data.session_token)
            localStorage.setItem('user', JSON.stringify(data.user))

            navigate('/dashboard')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-orange-50 to-blue-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <UserPlus className="w-12 h-12 text-primary mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900">Create Account</h2>
                    <p className="text-gray-600">
                        {step === 1 ? 'Start your free trial today' : 'Verify your contact details'}
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-center">
                        {error}
                    </div>
                )}

                {step === 1 ? (
                    <form onSubmit={handleSignup} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                            <input
                                type="text"
                                name="full_name"
                                required
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                                placeholder="Your Name"
                                value={formData.full_name}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                            <div className="relative">
                                <Mail className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                <input
                                    type="email"
                                    name="email"
                                    required
                                    className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                                    placeholder="you@example.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                            <div className="relative">
                                <Phone className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                <input
                                    type="tel"
                                    name="phone"
                                    required
                                    className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                                    placeholder="+91 98765 43210"
                                    value={formData.phone}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">City (Optional)</label>
                                <div className="relative">
                                    <MapPin className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                    <input
                                        type="text"
                                        name="city"
                                        className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                                        placeholder="Chennai"
                                        value={formData.city}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Profession</label>
                                <div className="relative">
                                    <Briefcase className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                                    <input
                                        type="text"
                                        name="profession"
                                        className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary"
                                        placeholder="Lawyer"
                                        value={formData.profession}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-primary text-white py-2 rounded-lg font-bold hover:bg-opacity-90 transition-colors flex items-center justify-center"
                        >
                            {loading ? 'Sending OTPs...' : 'Continue'}
                            {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerify} className="space-y-6">
                        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                            <div className="flex">
                                <div className="ml-3">
                                    <p className="text-sm text-yellow-700">
                                        We sent OTPs to both <strong>{formData.email}</strong> and <strong>{formData.phone}</strong>.
                                        Please enter both to verify.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Email OTP</label>
                            <input
                                type="text"
                                name="email_otp"
                                required
                                maxLength="6"
                                className="w-full px-3 py-2 border rounded-lg text-center tracking-widest text-xl font-mono focus:ring-2 focus:ring-primary"
                                placeholder="000000"
                                value={otpData.email_otp}
                                onChange={handleVerifyParams}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Phone OTP</label>
                            <input
                                type="text"
                                name="phone_otp"
                                required
                                maxLength="6"
                                className="w-full px-3 py-2 border rounded-lg text-center tracking-widest text-xl font-mono focus:ring-2 focus:ring-primary"
                                placeholder="000000"
                                value={otpData.phone_otp}
                                onChange={handleVerifyParams}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-green-600 text-white py-2 rounded-lg font-bold hover:bg-green-700 transition-colors flex items-center justify-center"
                        >
                            {loading ? 'Verifying...' : 'Verify & Launch'}
                            {!loading && <CheckCircle className="w-4 h-4 ml-2" />}
                        </button>
                    </form>
                )}

                <div className="mt-6 text-center text-sm">
                    <p className="text-gray-600">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary hover:underline font-semibold">
                            Login here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}
