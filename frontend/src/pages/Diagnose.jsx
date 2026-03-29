import { Helmet } from "react-helmet";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import UploadBox from "../components/UploadBox";
import CameraCapture from "../components/CameraCapture";
import HistoryCard from "../components/HistoryCard";
import api from "../services/api";

export default function Diagnose() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await api.get("/history");
      setHistory(res.data);
    } catch {
      console.log("History fetch failed");
    }
  };

  const handlePredict = async () => {
    if (!file) return alert("Upload image first");

    try {
      setLoading(true);

      const fd = new FormData();
      fd.append("file", file);

      const res = await api.post("/predict", fd);
      const result = res.data;

      navigate("/result", { state: { result } });
      fetchHistory();
    } catch {
      alert("Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const onNewFile = (f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  return (
    <>
      <Helmet>
        <title>Diagnose</title>
      </Helmet>

      <div className="max-w-5xl mx-auto px-4 py-10 space-y-10">
        <h2 className="text-3xl font-bold text-center">AI Ear Diagnosis</h2>

        <div className="grid md:grid-cols-2 gap-10">
          <UploadBox onUpload={onNewFile} />
          <CameraCapture onCapture={onNewFile} />
        </div>

        {preview && (
          <img src={preview} className="w-44 h-44 mx-auto rounded-xl shadow" />
        )}

        <div className="text-center">
          <button
            onClick={handlePredict}
            className="bg-indigo-600 text-white px-6 py-2 rounded-xl"
          >
            {loading ? "Analyzing..." : "Predict"}
          </button>
        </div>

        <HistoryCard history={history} backendURL="http://127.0.0.1:5000" />
      </div>
    </>
  );
}
