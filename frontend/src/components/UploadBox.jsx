import { useState } from "react";

export default function UploadBox({ onUpload }) {
  const [preview, setPreview] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setPreview(URL.createObjectURL(file));
    onUpload(file);
  };

  return (
    <div className="border p-4 rounded-xl text-center">
      <input type="file" onChange={handleFileChange} />

      {preview && (
        <img src={preview} className="w-40 mx-auto mt-4" />
      )}
    </div>
  );
}