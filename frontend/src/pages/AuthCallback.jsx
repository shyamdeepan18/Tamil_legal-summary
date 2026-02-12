import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'

export default function AuthCallback() {
    const navigate = useNavigate()
    const location = useLocation()

    useEffect(() => {
        const params = new URLSearchParams(location.search)
        const token = params.get('token')

        if (token) {
            // Save token
            localStorage.setItem('token', token)

            // Fetch user details
            fetch('/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
                .then(res => res.json())
                .then(data => {
                    localStorage.setItem('user', JSON.stringify(data.user))
                    navigate('/dashboard')
                })
                .catch(err => {
                    console.error("Failed to fetch user:", err)
                    navigate('/login?error=auth_failed')
                })
        } else {
            navigate('/login?error=no_token')
        }
    }, [navigate, location])

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Completing login...</p>
            </div>
        </div>
    )
}
