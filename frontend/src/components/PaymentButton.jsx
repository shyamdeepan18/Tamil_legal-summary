import { useState } from 'react'
import axios from 'axios'

export default function PaymentButton({ amount, uploadId, plan, onSuccess, className, children }) {
    const [loading, setLoading] = useState(false)

    const handlePayment = async () => {
        // Check authentication
        const userStr = localStorage.getItem('user')
        if (!userStr) {
            alert('Please login to purchase a plan.')
            window.location.href = '/login'
            return
        }

        const user = JSON.parse(userStr)
        setLoading(true)

        try {
            // Step 1: Create order
            const orderResponse = await axios.post('/api/create-order', {
                amount: amount,
                user_id: user.id || user.user_id,
                upload_id: uploadId || "plan_purchase",
                plan: plan
            })

            const { order_id, key_id } = orderResponse.data

            // Step 2: Open Razorpay checkout
            const options = {
                key: key_id,
                amount: amount,
                currency: 'INR',
                name: 'Tamil Document Summarizer',
                description: `Plan Upgrade - ${plan.replace('_', ' ').toUpperCase()}`,
                order_id: order_id,

                handler: async function (response) {
                    try {
                        await axios.post('/api/verify-payment', {
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                            upload_id: uploadId || "plan_purchase"
                        })

                        if (onSuccess) onSuccess(uploadId)
                        else window.location.href = '/dashboard'
                    } catch (error) {
                        console.error(error)
                        alert('Payment verification failed. Please contact support.')
                        setLoading(false)
                    }
                },

                prefill: {
                    name: user.name || user.full_name,
                    email: user.email,
                    contact: user.phone || ''
                },

                theme: {
                    color: '#F37254'
                },

                modal: {
                    ondismiss: function () {
                        setLoading(false)
                        alert('Payment cancelled. You can retry anytime.')
                    }
                }
            }

            const rzp = new window.Razorpay(options)
            rzp.open()
        } catch (error) {
            console.error(error)
            setLoading(false)
            alert('Failed to initiate payment. Please try again.')
        }
    }

    return (
        <button
            onClick={handlePayment}
            disabled={loading}
            className={className || "w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"}
        >
            {loading ? 'Processing...' : (children || `Pay ₹${amount / 100}`)}
        </button>
    )
}
