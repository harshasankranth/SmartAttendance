// frontend/src/components/Login.jsx
// ─────────────────────────────────────────────────────
// Admin login page
// Username: admin | Password: smart123
// ─────────────────────────────────────────────────────

import { useState } from "react"

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    setLoading(true)
    setError("")

    try {
      const res = await fetch("https://harshasankranth-smartattendance.hf.space  /auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      })

      const data = await res.json()

      if (res.ok && data.success) {
        onLogin()
      } else {
        setError("Invalid username or password")
      }
    } catch (err) {
      setError("Cannot connect to backend. Is the server running?")
    }

    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">
            👁️
          </div>
          <h1 className="text-3xl font-bold text-white">SmartAttendance</h1>
          <p className="text-gray-400 mt-2">AI Facial Recognition System</p>
        </div>

        {/* Card */}
        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8">
          <h2 className="text-xl font-bold text-white mb-6">Admin Login</h2>

          {/* Username */}
          <div className="mb-4">
            <label className="text-gray-400 text-sm mb-2 block">Username</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Enter username"
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Password */}
          <div className="mb-6">
            <label className="text-gray-400 text-sm mb-2 block">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Enter password"
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-900 border border-red-700 rounded-xl px-4 py-3 mb-4">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Button */}
          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900 text-white font-bold py-3 rounded-xl transition-colors"
          >
            {loading ? "Logging in..." : "Login"}
          </button>

          {/* Hint */}
          <p className="text-gray-600 text-xs text-center mt-4">
            Default: harsha / lucky123
          </p>
        </div>

      </div>
    </div>
  )
}