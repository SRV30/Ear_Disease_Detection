import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ResultCard({ result, pdfRef }) {

  const getRiskColor = (risk) => {
    if (risk === "High") return "bg-red-500";
    if (risk === "Medium") return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div
      ref={pdfRef}
      className="mt-10 backdrop-blur-lg bg-white/40 border border-white/20 shadow-2xl rounded-3xl p-8 space-y-8 animate-fadeIn"
    >
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Diagnosis Result
        </h2>
        <p className="text-sm text-gray-500">
          AI-powered ear disease analysis
        </p>
      </div>

      {/* Prediction Badge */}
      <div className="text-center">
        <span className="px-4 py-1.5 rounded-xl text-white font-bold text-lg shadow bg-indigo-600">
          {result.prediction}
        </span>

        <p className="mt-2 text-gray-700 font-medium">
          Confidence:{" "}
          <span className="text-indigo-700">{result.confidence}%</span>
        </p>
      </div>

      {/* Risk */}
      <div className="text-center">
        <span
          className={`px-3 py-1 rounded-lg text-white text-sm font-semibold ${getRiskColor(result.risk)}`}
        >
          Risk: {result.risk}
        </span>
      </div>

      {/* Divider */}
      <div className="h-0.5 w-full bg-linear-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50 rounded-full" />

      {/* Chart (if probabilities exist) */}
      {result.probabilities && (
        <Bar
          className="max-w-xl mx-auto"
          data={{
            labels: ["Normal", "Wax", "Infection"],
            datasets: [
              {
                data: result.probabilities,
                backgroundColor: ["#4F46E5", "#F59E0B", "#EF4444"],
                borderRadius: 8
              }
            ]
          }}
          options={{
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100 } },
            responsive: true
          }}
        />
      )}

      {/* Explanation */}
      <div>
        <h3 className="font-semibold text-gray-800 mb-1">Explanation</h3>
        <p className="text-sm text-gray-600">{result.explanation}</p>
      </div>

      {/* Advice */}
      <div>
        <h3 className="font-semibold text-gray-800 mb-1">Advice</h3>
        <p className="text-sm text-gray-600">{result.advice}</p>
      </div>

      {/* Extra */}
      {result.extra && (
        <div>
          <h3 className="font-semibold text-gray-800 mb-1">Extra Info</h3>
          <p className="text-sm text-gray-600">{result.extra}</p>
        </div>
      )}

      {/* Footer badges */}
      <div className="flex flex-wrap justify-center gap-4 pt-2">
        <span className="text-xs bg-gray-100 px-3 py-1 rounded-lg shadow">
          ⚡ Deep Learning Model
        </span>
        <span className="text-xs bg-gray-100 px-3 py-1 rounded-lg shadow">
          🧠 AI Diagnosis
        </span>
        <span className="text-xs bg-gray-100 px-3 py-1 rounded-lg shadow">
          🔒 Privacy Safe
        </span>
      </div>

      {/* Animation */}
      <style>
        {`
          .animate-fadeIn {
            animation: fadeIn 0.4s ease-in-out;
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}
      </style>
    </div>
  );
}