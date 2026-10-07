import { Helmet } from "react-helmet";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import UploadBox from "../components/UploadBox";
import HistoryStateWrapper from "../components/HistoryStateWrapper";
import api from "../services/api";
import SymptomInput from "../components/SymptomInput";
import SystemNotice from "../components/SystemNotice";
import { mapApiError } from "../services/apiErrorMap";

const features = [
  {
    icon: "01",
    title: "Upload clearly",
    text: "Use a sharp JPEG or PNG otoscopic image.",
  },
  {
    icon: "02",
    title: "AI analysis",
    text: "EfficientNet-B0 analyzes five supported classes.",
  },
  {
    icon: "03",
    title: "Explainable result",
    text: "Review confidence, guidance and Grad-CAM.",
  },
];

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
      setNotice({
        type: "warning",
        message: "Please upload an otoscopic image before starting the analysis.",
      });
      return;
    }

    try {
      setLoading(true);
      setNotice(null);

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

  const onNewFile = (selectedFile) => {
    if (!selectedFile) return;

    if (preview) URL.revokeObjectURL(preview);

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setNotice(null);
  };

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  return (
    <>
      <Helmet>
        <title>AI Ear Diagnosis</title>
        <meta
          name="description"
          content="Upload an otoscopic image for AI-assisted ear disease analysis."
        />
      </Helmet>

      <div className="min-h-screen bg-slate-50">
        <SystemNotice notice={notice} onClose={() => setNotice(null)} />

        <section className="relative overflow-hidden bg-gradient-to-br from-indigo-950 via-indigo-900 to-slate-900 text-white">
          <div className="absolute -top-24 -right-24 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl" />
          <div className="absolute -bottom-28 -left-20 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />

          <div className="relative max-w-6xl mx-auto px-5 pt-12 pb-16 md:pt-16 md:pb-20">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-medium text-indigo-100 backdrop-blur">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                AI-assisted otoscopic analysis
              </div>

              <h1 className="mt-5 text-4xl md:text-6xl font-black tracking-tight">
                Understand your ear image
                <span className="block text-indigo-300">with AI assistance.</span>
              </h1>

              <p className="mt-5 max-w-2xl text-base md:text-lg leading-7 text-indigo-100/80">
                Upload a clear otoscopic image and receive a five-class prediction,
                confidence information, visual explanation and AI-generated guidance.
              </p>
            </div>

            <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-3">
              {features.map((feature) => (
                <div
                  key={feature.icon}
                  className="rounded-2xl border border-white/10 bg-white/8 p-4 backdrop-blur"
                >
                  <div className="text-xs font-bold tracking-widest text-indigo-300">
                    {feature.icon}
                  </div>
                  <h3 className="mt-2 font-semibold">{feature.title}</h3>
                  <p className="mt-1 text-sm leading-5 text-indigo-100/65">
                    {feature.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <main className="max-w-6xl mx-auto px-5 -mt-7 pb-16 relative">
          <div className="grid lg:grid-cols-[1.35fr_0.65fr] gap-6 items-start">
            <section className="rounded-3xl bg-white border border-slate-200 shadow-xl shadow-slate-900/5 p-5 md:p-7">
              <div className="flex items-start justify-between gap-4 mb-6">
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                    Step 1
                  </p>
                  <h2 className="mt-1 text-2xl font-bold text-slate-900">
                    Upload otoscopic image
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Clear, well-lit images give the system the best chance of reliable analysis.
                  </p>
                </div>

                <div className="hidden sm:flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                  ↑
                </div>
              </div>

              <UploadBox onUpload={onNewFile} />

              {preview && (
                <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">Selected image</p>
                      <p className="text-xs text-slate-500 truncate max-w-[280px]">
                        {file?.name || "Uploaded image"}
                      </p>
                    </div>
                    <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                      Ready
                    </span>
                  </div>
                  <div className="p-3">
                    <img
                      src={preview}
                      alt="Selected otoscopic image preview"
                      className="w-full max-h-[420px] object-contain rounded-xl bg-slate-950"
                    />
                  </div>
                </div>
              )}

              <div className="mt-6">
                <SymptomInput value={symptoms} onChange={setSymptoms} />
              </div>

              <div className="mt-6 rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3">
                <p className="text-xs leading-5 text-amber-800">
                  <strong>For best results:</strong> use a clear otoscopic image similar
                  to the images used to train and evaluate the model.
                </p>
              </div>

              <button
                onClick={handlePredict}
                disabled={loading}
                className="mt-6 w-full rounded-2xl bg-indigo-600 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-700 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
              >
                {loading ? (
                  <span className="inline-flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Analyzing image...
                  </span>
                ) : (
                  "Analyze Image"
                )}
              </button>
            </section>

            <aside className="space-y-5">
              <div className="rounded-3xl bg-white border border-slate-200 shadow-lg shadow-slate-900/5 p-6">
                <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                  Supported classes
                </p>
                <div className="mt-4 space-y-3">
                  {[
                    "Acute Otitis Media",
                    "Cerumen Impaction",
                    "Chronic Otitis Media",
                    "Myringosclerosis",
                    "Normal",
                  ].map((name) => (
                    <div key={name} className="flex items-center gap-3 text-sm text-slate-700">
                      <span className="h-2 w-2 rounded-full bg-indigo-500" />
                      {name}
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl bg-slate-900 p-6 text-white shadow-lg">
                <p className="text-xs font-bold uppercase tracking-widest text-indigo-300">
                  Important
                </p>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  This system provides AI-assisted analysis for academic/research use.
                  It is not a clinical diagnosis and should not replace a qualified
                  healthcare professional.
                </p>
              </div>
            </aside>
          </div>

          <section className="mt-10 rounded-3xl bg-white border border-slate-200 shadow-lg shadow-slate-900/5 p-5 md:p-7">
            <HistoryStateWrapper
              loading={historyLoading}
              error={historyError}
              history={history}
              backendURL={import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000"}
            />
          </section>
        </main>
      </div>
    </>
  );
}
