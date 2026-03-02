
import { useState } from "react"
import Header from "./components/Header"
import Camera from "./components/Camera"
import Dashboard from "./components/Dashboard"

export default function App() {
  const [attendance, setAttendance] = useState([])
  const [presentCount, setPresentCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Header presentCount={presentCount} total={6} />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left — Live Camera */}
          <Camera 
            setAttendance={setAttendance}
            setPresentCount={setPresentCount}
          />

          {/* Right — Attendance Dashboard */}
          <Dashboard attendance={attendance} />

        </div>
      </main>
    </div>
  )
}