// frontend/src/components/Dashboard.jsx
export default function Dashboard({ attendance }) {
  const exportAttendance = () => {
    window.open("https://https://harshasankranth-smartattendance.hf.space  /attendance/export", "_blank")
  }

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">

      {/* Title */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-white">Today's Attendance</h2>
        <div className="flex items-center gap-2">
          <span className="bg-blue-900 text-blue-300 text-xs px-3 py-1 rounded-full border border-blue-700">
            {attendance.length} marked
          </span>
          <button
            onClick={exportAttendance}
            className="bg-green-700 hover:bg-green-600 text-white text-xs px-3 py-1 rounded-full transition-colors"
          >
            Export Excel
          </button>
        </div>
      </div>

      {/* Table */}
      {attendance.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">📷</p>
          <p className="text-gray-400">No attendance marked yet</p>
          <p className="text-gray-600 text-sm mt-1">Point camera at students to begin</p>
        </div>
      ) : (
        <div className="space-y-3">
          {attendance.map((record, index) => (
            <div key={index}
              className="flex items-center justify-between bg-gray-800 rounded-xl px-4 py-3 border border-gray-700">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <p className="text-white font-medium">{record.name}</p>
                  <p className="text-gray-400 text-xs">#{record.enrollment} • {record.confidence}%</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-gray-300 text-sm">{record.time}</p>
                <span className="text-green-400 text-xs bg-green-900 px-2 py-0.5 rounded-full">
                  Present ✓
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}