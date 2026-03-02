// frontend/src/components/Header.jsx
export default function Header({ presentCount, total, page, setPage, onLogout }) {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long", year: "numeric", month: "long", day: "numeric"
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

        {/* Nav */}
        <nav className="flex items-center gap-2">
          {[
            { id: "home", label: "Dashboard" },
            { id: "students", label: "Students" },
            { id: "add", label: "+ Add Student" }
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setPage(item.id)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                page === item.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3">
          <div className="bg-green-900 border border-green-700 rounded-xl px-4 py-2 text-center">
            <p className="text-green-400 text-xs">Present Today</p>
            <p className="text-white font-bold text-lg">{presentCount}/{total}</p>
          </div>
          <button
            onClick={onLogout}
            className="text-gray-400 hover:text-white text-sm px-3 py-2 rounded-xl hover:bg-gray-800 transition-colors"
          >
            Logout
          </button>
        </div>

      </div>
    </header>
  )
}