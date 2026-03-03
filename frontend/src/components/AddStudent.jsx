// frontend/src/components/AddStudent.jsx
// ─────────────────────────────────────────────────────
// Add new student with live camera capture
// Captures 20 photos, sends to backend, auto trains
// ─────────────────────────────────────────────────────

import { useRef, useState } from "react"

export default function AddStudent({ setPage }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [name, setName] = useState("")
  const [enrollment, setEnrollment] = useState("")
  const [step, setStep] = useState("form") // form → capturing → training → done
  const [capturedImages, setCapturedImages] = useState([])
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const totalPhotos = 20

  // Start webcam
  const startCamera = async () => {
    if (!name || !enrollment) {
      setError("Please fill in name and enrollment number")
      return
    }
    setError("")
    setStep("capturing")
    setCapturedImages([])
    setProgress(0)

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      videoRef.current.srcObject = stream
    } catch {
      setError("Cannot access camera!")
      setStep("form")
    }
  }

  // Capture photos automatically
  const startCapturing = () => {
    const images = []
    let count = 0

    const interval = setInterval(() => {
      if (count >= totalPhotos) {
        clearInterval(interval)

        // Stop camera
        const stream = videoRef.current.srcObject
        stream.getTracks().forEach(t => t.stop())

        setCapturedImages(images)
        setStep("preview")
        return
      }

      // Capture frame
      const canvas = canvasRef.current
      const video = videoRef.current
      const ctx = canvas.getContext("2d")
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      ctx.drawImage(video, 0, 0)

      const base64 = canvas.toDataURL("image/jpeg", 0.8).split(",")[1]
      images.push(base64)
      count++
      setProgress(count)

    }, 500) // capture every 0.5 seconds
  }

  // Submit to backend
  const submitStudent = async () => {
    setStep("training")
    setMessage("Saving photos and training model...")

    try {
      const res = await fetch("https://harshasankranth-smartattendance.hf.space  /students/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          enrollment,
          images: capturedImages
        })
      })

      const data = await res.json()

      if (res.ok && data.success) {
        setMessage(data.message)
        setStep("done")
      } else {
        setError(data.detail || "Failed to add student")
        setStep("preview")
      }
    } catch {
      setError("Cannot connect to backend!")
      setStep("preview")
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => setPage("students")}
          className="text-gray-400 hover:text-white transition-colors"
        >
          ← Back
        </button>
        <h2 className="text-2xl font-bold text-white">Add New Student</h2>
      </div>

      <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8">

        {/* STEP 1 — Form */}
        {step === "form" && (
          <div>
            <p className="text-gray-400 mb-6">Enter student details then capture their face photos.</p>

            <div className="mb-4">
              <label className="text-gray-400 text-sm mb-2 block">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="e.g. Harsha Sankranth"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="mb-6">
              <label className="text-gray-400 text-sm mb-2 block">Enrollment Number</label>
              <input
                type="text"
                value={enrollment}
                onChange={e => setEnrollment(e.target.value)}
                placeholder="e.g. 22BCE1234"
                className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {error && (
              <div className="bg-red-900 border border-red-700 rounded-xl px-4 py-3 mb-4">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={startCamera}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-colors"
            >
              📷 Open Camera & Capture Photos
            </button>
          </div>
        )}

        {/* STEP 2 — Capturing */}
        {step === "capturing" && (
          <div>
            <p className="text-gray-400 mb-4">
              Look at the camera. Click Start when ready — system will auto capture 20 photos.
            </p>

            <div className="relative rounded-xl overflow-hidden bg-gray-800 aspect-video mb-4">
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className="w-full h-full object-cover"
              />
              <canvas ref={canvasRef} className="hidden" />

              {/* Progress overlay */}
              {progress > 0 && (
                <div className="absolute top-4 left-4 bg-black bg-opacity-70 rounded-xl px-4 py-2">
                  <p className="text-white font-bold">{progress}/{totalPhotos} captured</p>
                </div>
              )}
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-800 rounded-full h-3 mb-4">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${(progress / totalPhotos) * 100}%` }}
              />
            </div>

            <button
              onClick={startCapturing}
              disabled={progress > 0}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white font-bold py-3 rounded-xl transition-colors"
            >
              {progress === 0 ? "▶ Start Capturing" : `Capturing... ${progress}/${totalPhotos}`}
            </button>
          </div>
        )}

        {/* STEP 3 — Preview */}
        {step === "preview" && (
          <div>
            <div className="text-center mb-6">
              <p className="text-4xl mb-2">✅</p>
              <p className="text-white font-bold text-xl">{capturedImages.length} photos captured!</p>
              <p className="text-gray-400 mt-1">for {name} ({enrollment})</p>
            </div>

            {error && (
              <div className="bg-red-900 border border-red-700 rounded-xl px-4 py-3 mb-4">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep("form")}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-xl transition-colors"
              >
                Retake
              </button>
              <button
                onClick={submitStudent}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-colors"
              >
                🧠 Save & Train Model
              </button>
            </div>
          </div>
        )}

        {/* STEP 4 — Training */}
        {step === "training" && (
          <div className="text-center py-8">
            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-white font-bold text-xl">Training AI Model...</p>
            <p className="text-gray-400 mt-2">{message}</p>
            <p className="text-gray-600 text-sm mt-4">This takes 2-3 minutes. Please wait.</p>
          </div>
        )}

        {/* STEP 5 — Done */}
        {step === "done" && (
          <div className="text-center py-8">
            <p className="text-6xl mb-4">🎉</p>
            <p className="text-white font-bold text-2xl">Student Added!</p>
            <p className="text-gray-400 mt-2">{message}</p>
            <p className="text-green-400 mt-2">Model retrained successfully ✓</p>

            <div className="flex gap-3 mt-8">
              <button
                onClick={() => { setStep("form"); setName(""); setEnrollment("") }}
                className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-xl"
              >
                Add Another
              </button>
              <button
                onClick={() => setPage("home")}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}