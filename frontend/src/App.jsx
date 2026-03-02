import { useState } from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import Login from "./components/Login"
import Header from "./components/Header"
import Camera from "./components/Camera"
import Dashboard from "./components/Dashboard"
import Students from "./components/Students"
import AddStudent from "./components/AddStudent"

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [attendance, setAttendance] = useState([])
  const [presentCount, setPresentCount] = useState(0)
  const [page, setPage] = useState("home")

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Header
        presentCount={presentCount}
        total={6}
        page={page}
        setPage={setPage}
        onLogout={() => setIsLoggedIn(false)}
      />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {page === "home" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Camera
              setAttendance={setAttendance}
              setPresentCount={setPresentCount}
            />
            <Dashboard attendance={attendance} />
          </div>
        )}
        {page === "students" && <Students setPage={setPage} />}
        {page === "add" && <AddStudent setPage={setPage} />}
      </main>
    </div>
  )
}