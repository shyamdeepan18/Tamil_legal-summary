import { useState } from 'react'
import { X, CheckCircle, AlertTriangle, FileText, Clock } from 'lucide-react'
import PaymentButton from './PaymentButton'

export default function PreviewModal({ data, onClose, onPaymentSuccess }) {
    const { upload_id, preview, pricing } = data

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900">
                        ✅ Document Ready for Analysis
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Document Overview */}
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <FileText className="w-5 h-5 text-primary" />
                                <span className="font-semibold">Document Type:</span>
                            </div>
                            <span className="font-bold text-primary">
                                {preview.doc_type_tamil} ({preview.doc_type})
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-gray-600">Quality:</span>
                                <span className="ml-2 font-semibold">
                                    {Math.round(preview.quality_score * 100)}% readable
                                </span>
                            </div>
                            <div>
                                <span className="text-gray-600">Pages:</span>
                                <span className="ml-2 font-semibold">{preview.page_count}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">Language:</span>
                                <span className="ml-2 font-semibold">{preview.language}</span>
                            </div>
                            <div className="flex items-center">
                                <Clock className="w-4 h-4 text-gray-600 mr-1" />
                                <span className="text-gray-600">Processing:</span>
                                <span className="ml-2 font-semibold">~{preview.estimated_time}s</span>
                            </div>
                        </div>
                    </div>

                    {/* Quick Analysis (FREE) */}
                    <div className="border-2 border-green-200 bg-green-50 rounded-lg p-4">
                        <h3 className="font-bold text-green-800 mb-3 flex items-center">
                            <CheckCircle className="w-5 h-5 mr-2" />
                            💡 Quick Analysis (FREE)
                        </h3>

                        <div className="space-y-2 text-sm">
                            {preview.detected_elements.property_details && (
                                <div className="flex items-center text-green-700">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Property details detected
                                </div>
                            )}
                            {preview.detected_elements.party_information && (
                                <div className="flex items-center text-green-700">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Seller/buyer information found
                                </div>
                            )}
                            {preview.detected_elements.financial_terms && (
                                <div className="flex items-center text-green-700">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Financial terms present (₹ amount visible)
                                </div>
                            )}
                            {preview.detected_elements.signatures && (
                                <div className="flex items-center text-green-700">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    Signature sections identified
                                </div>
                            )}

                            {/* Potential Flags */}
                            {preview.potential_flags.court_references && (
                                <div className="flex items-center text-yellow-700 bg-yellow-100 p-2 rounded">
                                    <AlertTriangle className="w-4 h-4 mr-2" />
                                    ⚠️ Possible court reference found (needs review)
                                </div>
                            )}
                            {preview.potential_flags.encumbrance_mentions && (
                                <div className="flex items-center text-yellow-700 bg-yellow-100 p-2 rounded">
                                    <AlertTriangle className="w-4 h-4 mr-2" />
                                    ⚠️ Encumbrance/mortgage mention detected
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Full Summary Includes */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h3 className="font-bold text-blue-800 mb-3">🎁 Full Summary Includes:</h3>
                        <ul className="space-y-2 text-sm text-blue-900">
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Complete Tamil + English summary</span>
                            </li>
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Key details extraction (parties, property, amounts)</span>
                            </li>
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Red flags detection (5 categories)</span>
                            </li>
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Missing information analysis</span>
                            </li>
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Document health score</span>
                            </li>
                            <li className="flex items-start">
                                <span className="mr-2">✓</span>
                                <span>Verification checklist</span>
                            </li>
                        </ul>
                    </div>

                    {/* Pricing Options */}
                    <div>
                        <h3 className="font-bold text-gray-900 mb-4 text-center">💰 Unlock Full Summary</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Quick Check */}
                            <div className="border-2 border-primary rounded-lg p-4 relative bg-blue-50">
                                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary text-white px-3 py-1 rounded-full text-xs font-bold">
                                    ONE TIME
                                </div>
                                <div className="text-center mb-4">
                                    <p className="text-sm text-gray-600 mb-1">⚡ Quick Check</p>
                                    <p className="text-3xl font-bold text-primary">₹49</p>
                                    <p className="text-xs text-gray-500">Unlock this document</p>
                                </div>
                                <ul className="text-sm space-y-2 mb-4">
                                    <li className="flex items-center"><span className="text-green-600 mr-2">✓</span> Full legal summary</li>
                                    <li className="flex items-center"><span className="text-green-600 mr-2">✓</span> Red flags detection</li>
                                    <li className="flex items-center"><span className="text-green-600 mr-2">✓</span> One-time payment</li>
                                </ul>
                                <PaymentButton
                                    amount={4900} // in paise
                                    uploadId={upload_id}
                                    plan="quick_check"
                                    onSuccess={onPaymentSuccess}
                                />
                            </div>

                            {/* Monthly Pack */}
                            <div className="border-2 border-secondary rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
                                <div className="text-center mb-4">
                                    <p className="text-sm text-gray-600 mb-1">📅 Monthly Pack</p>
                                    <p className="text-3xl font-bold text-secondary">₹499</p>
                                    <p className="text-xs text-gray-500">15 Documents / Month</p>
                                </div>
                                <ul className="text-sm space-y-2 mb-4">
                                    <li className="flex items-center"><span className="text-secondary mr-2">✦</span> Best Value (Save 33%)</li>
                                    <li className="flex items-center"><span className="text-secondary mr-2">✦</span> Includes this doc</li>
                                    <li className="flex items-center"><span className="text-secondary mr-2">✦</span> Priority support</li>
                                </ul>
                                <PaymentButton
                                    amount={49900} // in paise
                                    uploadId={upload_id}
                                    plan="monthly_pack"
                                    onSuccess={onPaymentSuccess}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Trust Signals */}
                    <div className="text-center space-y-2">
                        <p className="text-sm text-gray-600">
                            💬 "Found a court case I didn't know about!" - Ramesh K., Chennai
                        </p>
                        <p className="text-xs text-gray-500">
                            🔒 Document will be auto-deleted after analysis
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
