import { useState } from 'react'
import { Lock, AlertCircle } from 'lucide-react'

export default function PasswordPrompt({ onSubmit, onCancel, error }) {
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!password.trim()) return

        setLoading(true)
        await onSubmit(password)
        setLoading(false)
    }

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
                {/* Header */}
                <div className="flex items-center space-x-3 mb-4">
                    <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                        <Lock className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">
                            Password Protected PDF
                        </h2>
                        <p className="text-sm text-gray-600 tamil-text">
                            கடவுச்சொல் பாதுகாக்கப்பட்ட PDF
                        </p>
                    </div>
                </div>

                {/* Message */}
                <p className="text-gray-700 mb-4">
                    This document is password protected. Please enter the password to continue.
                </p>
                <p className="text-sm text-gray-600 mb-6 tamil-text">
                    இந்த ஆவணம் கடவுச்சொல் பாதுகாக்கப்பட்டுள்ளது. தொடர கடவுச்சொல்லை உள்ளிடவும்.
                </p>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
                        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-sm font-semibold text-red-800">Incorrect Password</p>
                            <p className="text-sm text-red-600">{error}</p>
                        </div>
                    </div>
                )}

                {/* Password Form */}
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                            Enter Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter PDF password"
                            className="input-field"
                            autoFocus
                            disabled={loading}
                        />
                    </div>

                    {/* Buttons */}
                    <div className="flex space-x-3">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-semibold"
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 btn-primary disabled:opacity-50"
                            disabled={loading || !password.trim()}
                        >
                            {loading ? 'Unlocking...' : 'Unlock PDF'}
                        </button>
                    </div>
                </form>

                {/* Help Text */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-blue-800">
                        💡 <strong>Tip:</strong> The password is set by the person who created or encrypted the PDF.
                        If you don't have the password, contact the document owner.
                    </p>
                </div>
            </div>
        </div>
    )
}
