// frontend/src/components/Header.jsx
// ─────────────────────────────────────────────────────
// Top navigation bar
// Shows logo, date, and present count
// ─────────────────────────────────────────────────────

export default function Header({ presentCount, total }) {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric"
  })

  return (
    <header className="border-b border-gray-800 bg-gray-900 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-xl">
            👁️
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">SmartAttendance</h1>
            <p className="text-xs text-gray-400">AI Facial Recognition System</p>
          </div>
        </div>

        {/* Date */}
        <p className="text-gray-400 text-sm hidden md:block">{today}</p>

        {/* Present count */}
        <div className="bg-green-900 border border-green-700 rounded-xl px-4 py-2 text-center">
          <p className="text-green-400 text-xs">Present Today</p>
          <p className="text-white font-bold text-lg">{presentCount}/{total}</p>
        </div>

      </div>
    </header>
  )
}