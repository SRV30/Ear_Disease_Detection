import { Helmet } from "react-helmet";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import UploadBox from "../components/UploadBox";
import CameraCapture from "../components/CameraCapture";
import HistoryStateWrapper from "../components/HistoryStateWrapper";
import api from "../services/api";
import SymptomInput from "../components/SymptomInput";
import SystemNotice from "../components/SystemNotice";
import { mapApiError } from "../services/apiErrorMap";

export default function Diagnose() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [notice, setNotice] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setHistoryLoading(true);
      setHistoryError("");
      const res = await api.get("/history");
      setHistory(res.data);
    } catch (error) {
      setHistoryError(mapApiError(error, "History fetch failed").message);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!file) {
      setNotice({ type: "warning", message: "Upload image first" });
      return;
    }

    try {
      setLoading(true);

      const fd = new FormData();
      fd.append("file", file);
      if (symptoms.trim()) fd.append("symptoms", symptoms.trim());

      const res = await api.post("/predict", fd);
      const result = res.data;

      navigate("/result", { state: { result } });
      fetchHistory();
    } catch (error) {
      setNotice(mapApiError(error, "Prediction failed"));
    } finally {
      setLoading(false);
    }
  };

  const onNewFile = (f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  return (
    <>
      <Helmet>
        <title>Diagnose</title>
      </Helmet>

      <div className="max-w-5xl mx-auto px-4 py-10 space-y-10">
        <SystemNotice notice={notice} onClose={() => setNotice(null)} />
        <h2 className="text-3xl font-bold text-center">AI Ear Diagnosis</h2>

        <div className="grid md:grid-cols-2 gap-10">
          <UploadBox onUpload={onNewFile} />
          <CameraCapture onCapture={onNewFile} />
        </div>

        {preview && (
          <img src={preview} className="w-44 h-44 mx-auto rounded-xl shadow" />
        )}

        <SymptomInput value={symptoms} onChange={setSymptoms} />

        <div className="text-center">
          <button
            onClick={handlePredict}
            className="bg-indigo-600 text-white px-6 py-2 rounded-xl"
          >
            {loading ? "Analyzing..." : "Predict"}
          </button>
        </div>

        <HistoryStateWrapper loading={historyLoading} error={historyError} history={history} backendURL={import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000"} />
      </div>
    </>
  );
}
