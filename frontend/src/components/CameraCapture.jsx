import { useRef, useState } from "react";

export default function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [camOn, setCamOn] = useState(false);
  const [error, setError] = useState("");

  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      setCamOn(true);
      setError("");
    } catch (err) {
      setError("Camera access denied or not available on this device.");
      console.log(err);
      
    }
  };

  const capture = () => {
    if (!camOn) return;

    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      const file = new File([blob], "camera.jpg", { type: "image/jpeg" });
      onCapture(file);
    });

    streamRef.current?.getTracks().forEach((t) => t.stop());
    setCamOn(false);
  };

  return (
    <div className="bg-white border border-indigo-100 shadow-lg rounded-2xl p-5 flex flex-col items-center space-y-4">
      <div className="relative">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className={`w-60 h-44 rounded-xl object-cover border ${
            camOn ? "border-indigo-500" : "border-slate-300"
          } transition`}
        />
        {!camOn && (
          <div className="absolute inset-0 rounded-xl bg-slate-900/40 flex items-center justify-center text-xs text-white">
            Camera Off
          </div>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 px-3 py-1 rounded-lg">
          {error}
        </p>
      )}

      <div className="flex gap-3">
        <button
          onClick={openCamera}
          disabled={camOn}
          className={`px-5 py-2 rounded-xl text-sm font-semibold shadow 
            ${
              camOn
                ? "bg-purple-300 cursor-not-allowed"
                : "bg-purple-600 hover:bg-purple-700 text-white"
            }`}
        >
          Open Camera
        </button>

        <button
          onClick={capture}
          disabled={!camOn}
          className={`px-5 py-2 rounded-xl text-sm font-semibold shadow 
            ${
              camOn
                ? "bg-green-600 hover:bg-green-700 text-white"
                : "bg-green-300 cursor-not-allowed"
            }`}
        >
          Capture
        </button>
      </div>

      <p className="text-[10px] text-slate-500 text-center leading-4 max-w-xs">
        Make sure your ear is visible in the camera frame for accurate diagnosis. 
        Good lighting improves AI analysis.
      </p>
    </div>
  );
}