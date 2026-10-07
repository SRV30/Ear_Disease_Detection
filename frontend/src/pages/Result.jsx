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
    return (
      <div className="text-center mt-10">
        <h2>No Result</h2>
        <button onClick={() => navigate("/diagnose")}>Go Back</button>
      </div>
    );
  }

  const downloadReport = async () => {
    if (!result.id) {
      setError("Report ID is unavailable for this prediction.");
      return;
    }

    try {
      setDownloading(true);
      setError("");

      const response = await api.get(`/report/${result.id}`, {
        responseType: "blob",
      });

      const blobUrl = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `ear_disease_report_${result.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch {
      setError("Unable to generate the PDF report. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto mt-10 px-4">
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={downloadReport}
          disabled={downloading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white px-6 py-2.5 rounded-xl font-semibold shadow"
        >
          {downloading ? "Generating Report..." : "Download PDF Report"}
        </button>

        {error && (
          <p className="text-sm text-red-600 text-center">{error}</p>
        )}
      </div>

      <ResultCard result={result} />
    </div>
  );
}
