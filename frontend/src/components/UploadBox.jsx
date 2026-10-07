import { useRef, useState } from "react";

const MAX_SIZE = 50 * 1024 * 1024;

export default function UploadBox({ onUpload }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  const selectFile = (file) => {
    if (!file) return;

    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setError("Please select a JPEG or PNG image.");
      return;
    }

    if (file.size > MAX_SIZE) {
      setError("Image must be smaller than 50 MB.");
      return;
    }

    setError("");
    onUpload(file);
  };

  const handleChange = (event) => {
    selectFile(event.target.files?.[0]);
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    selectFile(event.dataTransfer.files?.[0]);
  };

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={
          "group w-full rounded-2xl border-2 border-dashed p-8 md:p-10 text-center transition " +
          (dragging
            ? "border-indigo-500 bg-indigo-50"
            : "border-slate-300 bg-slate-50 hover:border-indigo-400 hover:bg-indigo-50/50")
        }
      >
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-100 text-indigo-600 transition group-hover:scale-105">
          <svg
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 16V4" />
            <path d="m7 9 5-5 5 5" />
            <path d="M5 20h14" />
          </svg>
        </div>

        <h3 className="mt-5 text-base font-bold text-slate-800">
          {dragging ? "Drop your image here" : "Choose an otoscopic image"}
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Drag & drop here or <span className="font-semibold text-indigo-600">browse files</span>
        </p>

        <div className="mt-4 flex flex-wrap justify-center gap-2">
          <span className="rounded-full bg-white border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500">
            JPG / JPEG
          </span>
          <span className="rounded-full bg-white border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500">
            PNG
          </span>
          <span className="rounded-full bg-white border border-slate-200 px-3 py-1 text-xs font-medium text-slate-500">
            Max 50 MB
          </span>
        </div>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleChange}
        className="hidden"
      />

      {error && (
        <p className="mt-3 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
