import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import ResultCard from "../components/ResultCard";
import { isValidResultPayload } from "../utils/responseValidators";
import api from "../services/api";

export default function Result() {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  if (!result || !isValidResultPayload(result)) {
    return <div className="min-h-screen bg-slate-50 flex items-center justify-center px-5"><div className="max-w-md w-full rounded-3xl bg-white border border-slate-200 shadow-xl p-8 text-center"><h2 className="text-2xl font-bold text-slate-900">No diagnosis result</h2><p className="mt-2 text-sm text-slate-500">Start a new analysis by uploading an otoscopic image.</p><button onClick={() => navigate("/diagnose")} className="mt-6 w-full rounded-xl bg-indigo-600 px-5 py-3 text-sm font-bold text-white hover:bg-indigo-700">Start New Analysis</button></div></div>;
  }

  const downloadReport = async () => {
    if (!result.id) { setError("Report ID is unavailable for this diagnosis."); return; }
    try {
      setDownloading(true); setError("");
      const response = await api.get(`/report/${result.id}`, { responseType: "blob" });
      const blobUrl = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = blobUrl; link.download = `ear_disease_report_${result.id}.pdf`;
      document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(blobUrl);
    } catch { setError("Unable to generate the PDF report. Please try again."); }
    finally { setDownloading(false); }
  };

  return <div className="min-h-screen bg-slate-50">
    <header className="bg-gradient-to-br from-indigo-950 via-indigo-900 to-slate-900 text-white">
      <div className="max-w-6xl mx-auto px-5 py-10 md:py-14">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
          <div><span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-indigo-100"><span className="h-2 w-2 rounded-full bg-emerald-400" />Analysis complete</span><h1 className="mt-4 text-3xl md:text-5xl font-black tracking-tight">Your analysis result</h1><p className="mt-3 max-w-2xl text-sm md:text-base leading-6 text-indigo-100/75">Review the prediction, confidence, visual explanation and guidance below. This result is for research and decision support and is not a clinical diagnosis.</p></div>
          <div className="flex flex-wrap gap-3"><button onClick={() => navigate("/diagnose")} className="rounded-xl border border-white/15 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/15">New Analysis</button><button onClick={downloadReport} disabled={downloading} className="rounded-xl bg-white px-4 py-2.5 text-sm font-bold text-indigo-900 shadow-lg hover:bg-indigo-50 disabled:opacity-60">{downloading ? "Generating PDF..." : "Download PDF Report"}</button></div>
        </div>
        {error && <p className="mt-4 rounded-xl border border-red-300/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">{error}</p>}
      </div>
    </header>
    <main className="max-w-6xl mx-auto px-5 py-8 md:py-10"><ResultCard result={result} /></main>
  </div>;
}