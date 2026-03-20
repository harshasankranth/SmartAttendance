// frontend/src/components/Students.jsx
import { useEffect, useState } from "react"

export default function Students({ setPage }) {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("https://harshasankranth-smartattendance.hf.space/students/all")
      .then(res => res.json())
      .then(data => {
        setStudents(data.students)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* Top bar */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Registered Students</h2>
          <p className="text-gray-400 text-sm mt-1">{students.length} students in system</p>
        </div>
        <button
          onClick={() => setPage("add")}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-3 rounded-xl transition-colors"
        >
          + Add New Student
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-16">
          <p className="text-gray-400">Loading students...</p>
        </div>
      )}

      {/* Empty */}
      {!loading && students.length === 0 && (
        <div className="text-center py-16 bg-gray-900 rounded-2xl border border-gray-800">
          <p className="text-4xl mb-3">👥</p>
          <p className="text-gray-400">No students registered yet</p>
          <button
            onClick={() => setPage("add")}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-xl"
          >
            Add First Student
          </button>
        </div>
      )}

      {/* Students grid */}
      {!loading && students.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {students.map((student, i) => (
            <div key={i} className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl font-bold">
                  {student.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-white font-bold">{student.name}</p>
                  <p className="text-gray-400 text-sm">#{student.enrollment}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-800 flex justify-between text-sm">
                <span className="text-gray-400">{student.photos} photos</span>
                <span className="text-gray-500">{student.added_on}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}