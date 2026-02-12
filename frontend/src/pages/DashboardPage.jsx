import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Clock, AlertTriangle, Plus, LogOut, Download } from 'lucide-react'

export default function DashboardPage() {
    const navigate = useNavigate()
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchStats = async () => {
            const token = localStorage.getItem('token')
            if (!token) {
                navigate('/login')
                return
            }

            try {
                const response = await fetch('/api/auth/dashboard/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })

                if (!response.ok) {
                    if (response.status === 401) {
                        localStorage.removeItem('token')
                        navigate('/login')
                        return
                    }
                    throw new Error('Failed to fetch dashboard')
                }

                const data = await response.json()
                setStats(data)
            } catch (err) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }

        fetchStats()
    }, [navigate])

    const handleLogout = () => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        navigate('/login')
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 text-red-600">
                Error: {error}
            </div>
        )
    }

    if (!stats) return null

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navbar */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        <LayoutDashboard className="w-6 h-6 text-primary" />
                        <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="text-right hidden sm:block">
                            <p className="text-sm font-semibold text-gray-900">{stats.user.name}</p>
                            <p className="text-xs text-gray-500">{stats.plan.type.replace('_', ' ').toUpperCase()}</p>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-500 hover:text-red-500 rounded-full hover:bg-gray-100"
                        >
                            <LogOut className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {/* Plan Usage */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-gray-500 text-sm font-medium mb-2">Plan Usage</h3>
                        <div className="flex items-end space-x-2">
                            <span className="text-3xl font-bold text-gray-900">{stats.plan.documents_remaining}</span>
                            <span className="text-gray-500 mb-1">/ {stats.plan.documents_limit} docs left</span>
                        </div>
                        <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                            <div
                                className="bg-primary h-2 rounded-full transition-all duration-500"
                                style={{ width: `${(stats.plan.documents_used / stats.plan.documents_limit) * 100}%` }}
                            ></div>
                        </div>
                        {stats.plan.next_reset && (
                            <p className="text-xs text-gray-400 mt-2">
                                Resets on {new Date(stats.plan.next_reset).toLocaleDateString()}
                            </p>
                        )}
                        {stats.plan.rollover_docs > 0 && (
                            <p className="text-xs text-green-600 mt-1">
                                +{stats.plan.rollover_docs} docs rolled over from last week
                            </p>
                        )}
                    </div>

                    {/* Total Value */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-gray-500 text-sm font-medium mb-2">Total Value Saved</h3>
                        <div className="flex items-end space-x-2">
                            <span className="text-3xl font-bold text-green-600">₹{stats.stats.total_saved}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            vs. traditional legal fees
                        </p>
                    </div>

                    {/* Quick Action */}
                    <div className="bg-gradient-to-br from-primary to-orange-600 p-6 rounded-xl shadow-lg text-white">
                        <h3 className="font-bold text-lg mb-2">New Analysis</h3>
                        <p className="text-white text-opacity-80 text-sm mb-4">
                            Upload a new legal document for summary and red flag detection.
                        </p>
                        <button
                            onClick={() => navigate('/')}
                            className="w-full bg-white text-primary py-2 rounded-lg font-bold hover:bg-opacity-90 flex items-center justify-center transition-colors shadow-sm"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Upload Document
                        </button>
                    </div>
                </div>

                {/* Recent Documents */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                        <h3 className="font-bold text-gray-900">Recent Documents</h3>
                        <button className="text-sm text-primary hover:underline">View All</button>
                    </div>

                    {stats.recent_documents.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            No documents processed yet. Start by uploading one!
                        </div>
                    ) : (
                        <div className="divide-y divide-gray-100">
                            {stats.recent_documents.map((doc) => (
                                <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                                            <FileText className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-gray-900">{doc.doc_type || 'Unknown Document'}</p>
                                            <div className="flex items-center text-xs text-gray-500 space-x-2">
                                                <span className="flex items-center">
                                                    <Clock className="w-3 h-3 mr-1" />
                                                    {new Date(doc.processed_at).toLocaleDateString()}
                                                </span>
                                                {doc.red_flags_count > 0 && (
                                                    <span className="flex items-center text-red-500">
                                                        <AlertTriangle className="w-3 h-3 mr-1" />
                                                        {doc.red_flags_count} Issues Found
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <button
                                            onClick={() => navigate(`/summary/${doc.id}`)}
                                            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                                        >
                                            View
                                        </button>
                                        <button className="p-1 text-gray-400 hover:text-gray-600">
                                            <Download className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>
        </div>
    )
}
