import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { FileText, Download, Share2, AlertTriangle, CheckCircle } from 'lucide-react'

export default function SummaryPage() {
    const { uploadId } = useParams()
    const [loading, setLoading] = useState(true)
    const [summary, setSummary] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        // TODO: Fetch summary from backend
        // For now, showing placeholder
        setTimeout(() => {
            setLoading(false)
            setSummary({
                doc_type: 'sale_deed',
                health_score: 88,
                summary_text: 'Summary will be generated here...',
                red_flags: [
                    {
                        severity: 'high',
                        explanation_tamil: 'நீதிமன்ற வழக்கு குறிப்பிடப்பட்டுள்ளது',
                        explanation_english: 'Court case reference found',
                        context: 'வழக்கு எண் 123/2022...',
                        action: 'Verify if case is resolved'
                    }
                ]
            })
        }, 2000)
    }, [uploadId])

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-lg font-semibold">Generating your summary...</p>
                    <p className="text-sm text-gray-500 tamil-text">உங்கள் சுருக்கத்தை உருவாக்குகிறோம்...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <p className="text-lg font-semibold text-red-600">{error}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-5xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <h1 className="text-2xl font-bold text-gray-900">
                            ✅ Analysis Complete
                        </h1>
                        <div className="flex space-x-3">
                            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                                <Download className="w-4 h-4" />
                                <span>Download PDF</span>
                            </button>
                            <button className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                                <Share2 className="w-4 h-4" />
                                <span>Share via WhatsApp</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
                {/* Document Overview */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4">📄 Document Overview</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-gray-600">Type</p>
                            <p className="font-semibold">விற்பனை பத்திரம்</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Health Score</p>
                            <p className="font-semibold text-green-600">{summary.health_score}/100 🟢</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Red Flags</p>
                            <p className="font-semibold text-yellow-600">{summary.red_flags.length} issues</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Status</p>
                            <p className="font-semibold">Review Needed</p>
                        </div>
                    </div>
                </div>

                {/* Red Flags */}
                {summary.red_flags.length > 0 && (
                    <div className="card border-2 border-yellow-200 bg-yellow-50">
                        <h2 className="text-xl font-bold mb-4 flex items-center">
                            <AlertTriangle className="w-6 h-6 text-yellow-600 mr-2" />
                            🚨 Red Flags ({summary.red_flags.length})
                        </h2>
                        <div className="space-y-4">
                            {summary.red_flags.map((flag, index) => (
                                <div key={index} className="bg-white rounded-lg p-4 border border-yellow-300">
                                    <div className="flex items-start justify-between mb-2">
                                        <div>
                                            <p className="font-semibold text-gray-900">
                                                {flag.explanation_tamil}
                                            </p>
                                            <p className="text-sm text-gray-600">{flag.explanation_english}</p>
                                        </div>
                                        <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-bold rounded">
                                            {flag.severity.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 mb-2">
                                        "{flag.context}"
                                    </div>
                                    <p className="text-sm text-blue-600">
                                        📌 Action: {flag.action}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Full Summary */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4">📋 Detailed Summary</h2>
                    <div className="prose max-w-none">
                        <p className="whitespace-pre-wrap">{summary.summary_text}</p>
                    </div>
                </div>

                {/* Disclaimer */}
                <div className="card bg-gray-100 border border-gray-300">
                    <p className="text-sm text-gray-700">
                        ⚖️ <strong>Disclaimer:</strong> This is an automated summary, not legal advice.
                        இது தானியங்கி சுருக்கம், சட்ட ஆலோசனை அல்ல.
                        Consult a lawyer for important decisions.
                    </p>
                    <p className="text-xs text-gray-600 mt-2">
                        🔒 Your document was deleted after processing. Only this summary remains.
                    </p>
                </div>
            </main>
        </div>
    )
}
