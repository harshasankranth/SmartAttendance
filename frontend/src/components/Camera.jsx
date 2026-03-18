// frontend/src/components/Camera.jsx
// ─────────────────────────────────────────────────────
// Live camera feed with face recognition
// Connects to backend via WebSocket
// Sends frames every second, receives names back
// Draws face boxes and names on canvas overlay
// ─────────────────────────────────────────────────────

import { useEffect, useRef, useState } from "react"

export default function Camera({ setAttendance, setPresentCount }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const wsRef = useRef(null)
  const [status, setStatus] = useState("Connecting...")
  const [isConnected, setIsConnected] = useState(false)
  const [currentFace, setCurrentFace] = useState(null)

  // ─────────────────────────────────────────────
  // Start webcam
  // ─────────────────────────────────────────────
  useEffect(() => {
    startCamera()
    connectWebSocket()
    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      videoRef.current.srcObject = stream
    } catch (err) {
      setStatus("Camera access denied!")
    }
  }

  // ─────────────────────────────────────────────
  // Connect to backend WebSocket
  // ─────────────────────────────────────────────
  const connectWebSocket = () => {
    const ws = new WebSocket("wss://https://harshasankranth-smartattendance.hf.space/ws/recognize")
    wsRef.current = ws

    ws.onopen = () => {
      setStatus("Connected! Looking for faces...")
      setIsConnected(true)
      startSendingFrames(ws)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleRecognitionResult(data)
    }

    ws.onclose = () => {
      setStatus("Disconnected from backend")
      setIsConnected(false)
    }

    ws.onerror = () => {
      setStatus("Backend not running! Start uvicorn first.")
      setIsConnected(false)
    }
  }

  // ─────────────────────────────────────────────
  // Send camera frames to backend every second
  // ─────────────────────────────────────────────
  const startSendingFrames = (ws) => {
    setInterval(() => {
      if (ws.readyState !== WebSocket.OPEN) return
      if (!videoRef.current || !canvasRef.current) return

      const canvas = canvasRef.current
      const video = videoRef.current
      const ctx = canvas.getContext("2d")

      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      ctx.drawImage(video, 0, 0)

      // Convert frame to base64
      const base64 = canvas.toDataURL("image/jpeg", 0.7).split(",")[1]
      ws.send(JSON.stringify({ image: base64 }))

    }, 1000) // every 1 second
  }

  // ─────────────────────────────────────────────
  // Handle results from backend
  // ─────────────────────────────────────────────
  const handleRecognitionResult = (data) => {
    if (data.faces && data.faces.length > 0) {
      const face = data.faces[0]
      setCurrentFace(face)

      // Update attendance if new person marked
      if (data.marked_today) {
        setPresentCount(data.total_present)
        setAttendance(prev => {
          const names = prev.map(r => r.name)
          const newRecords = data.marked_today
            .filter(name => !names.includes(name))
            .map(name => ({
              name,
              confidence: face.confidence,
              time: new Date().toLocaleTimeString()
            }))
          return [...prev, ...newRecords]
        })
      }
    } else {
      setCurrentFace(null)
    }
  }

  return (
    <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
      
      {/* Title */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Live Camera</h2>
        <span className={`text-xs px-3 py-1 rounded-full border ${
          isConnected 
            ? "bg-green-900 text-green-300 border-green-700" 
            : "bg-red-900 text-red-300 border-red-700"
        }`}>
          {isConnected ? "● Live" : "● Offline"}
        </span>
      </div>

      {/* Camera feed */}
      <div className="relative rounded-xl overflow-hidden bg-gray-800 aspect-video">
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="w-full h-full object-cover"
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full"
          style={{ display: "none" }}
        />

        {/* Face detection overlay */}
        {currentFace && (
          <div className="absolute top-4 left-4 bg-black bg-opacity-70 rounded-xl px-4 py-2 border border-green-500">
            <p className="text-green-400 font-bold">{currentFace.name}</p>
            <p className="text-gray-300 text-xs">{currentFace.confidence}% confidence</p>
          </div>
        )}

        {/* Status bar */}
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 px-4 py-2">
          <p className="text-gray-300 text-xs">{status}</p>
        </div>
      </div>

    </div>
  )
}