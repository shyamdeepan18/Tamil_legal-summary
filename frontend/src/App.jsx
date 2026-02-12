import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import SummaryPage from './pages/SummaryPage'

import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'

import DashboardPage from './pages/DashboardPage'

import AuthCallback from './pages/AuthCallback'

function App() {
    return (
        <Router>
            <div className="min-h-screen">
                <Routes>
                    <Route path="/" element={<UploadPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignupPage />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/auth/callback" element={<AuthCallback />} />
                    <Route path="/summary/:uploadId" element={<SummaryPage />} />
                </Routes>
            </div>
        </Router>
    )
}

export default App
