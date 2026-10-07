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
import HeatmapPanel from "./HeatmapPanel";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const CLASS_NAMES = [
  "Acute Otitis Media",
  "Cerumen Impaction",
  "Chronic Otitis Media",
  "Myringosclerosis",
  "Normal"
];

export default function ResultCard({ result, pdfRef }) {

  const getRiskColor = (risk) => {
    if (risk === "High") return "bg-red-500";
    if (risk === "Medium") return "bg-yellow-500";
    return "bg-green-500";
  };

  const confidence = Number(result.confidence);
  const confidenceText = Number.isFinite(confidence)
    ? confidence.toFixed(4)
    : result.confidence;

  const probabilities = Array.isArray(result.probabilities)
    ? result.probabilities
    : [];

  const probabilityValues = CLASS_NAMES.map((_, index) => {
    const value = Number(probabilities[index]);
    return Number.isFinite(value) ? value * 100 : 0;
  });

  const probabilityLabels = CLASS_NAMES.map((name) =>
    name === result.prediction ? `${name} (Predicted)` : name
  );

  const probabilityData = {
    labels: probabilityLabels,
    datasets: [
      {
        label: "Probability (%)",
        data: probabilityValues,
        borderWidth: 1,
        borderRadius: 6
      }
    ]
  };

  const probabilityOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: "y",
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        title: {
          display: true,
          text: "Probability (%)"
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: "Prediction Probabilities"
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.raw.toFixed(4)}%`
        }
      }
    }
  };

  return (
    <div
      ref={pdfRef}
      className="mt-10 backdrop-blur-lg bg-white/40 border border-white/20 shadow-2xl rounded-3xl p-8 space-y-8 animate-fadeIn"
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Diagnosis Result
        </h2>
        <p className="text-sm text-gray-500">
          AI-powered ear disease analysis
        </p>
      </div>

      <div className="text-center">
        <span className="px-4 py-1.5 rounded-xl text-white font-bold text-lg shadow bg-indigo-600">
          {result.prediction}
        </span>

        <p className="mt-2 text-gray-700 font-medium">
          Confidence:{" "}
          <span className="text-indigo-700">{confidenceText}%</span>
        </p>
      </div>

      <div className="text-center">
        <span
          className={"px-3 py-1 rounded-lg text-white text-sm font-semibold " + getRiskColor(result.risk)}
        >
          Risk: {result.risk}
        </span>
      </div>

      <div className="h-0.5 w-full bg-linear-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50 rounded-full" />

      <div>
        <h3 className="font-semibold text-gray-800 mb-1">Explanation</h3>
        <p className="text-sm text-gray-600">{result.explanation}</p>
      </div>

      <div>
        <h3 className="font-semibold text-gray-800 mb-1">Advice</h3>
        <p className="text-sm text-gray-600">{result.advice}</p>
      </div>

      {probabilities.length === CLASS_NAMES.length && (
        <div>
          <h3 className="font-semibold text-gray-800 mb-3">
            Class Probabilities
          </h3>

          <div className="h-64 w-full">
            <Bar data={probabilityData} options={probabilityOptions} />
          </div>

          <div className="mt-4 space-y-2">
            {CLASS_NAMES.map((name, index) => (
              <div
                key={name}
                className="flex items-center justify-between rounded-lg bg-white/60 px-3 py-2 text-sm"
              >
                <span className="font-medium text-gray-700">
                  {name}
                  {name === result.prediction && (
                    <span className="ml-2 text-xs font-semibold text-indigo-600">
                      Predicted
                    </span>
                  )}
                </span>
                <span className="font-semibold text-gray-800">
                  {probabilityValues[index].toFixed(4)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <HeatmapPanel
        imageUrl={result.image_url}
        heatmapUrl={result.heatmap_url}
      />

      {result.extra && (
        <div>
          <h3 className="font-semibold text-gray-800 mb-1">Extra Info</h3>
          <p className="text-sm text-gray-600">{result.extra}</p>
        </div>
      )}

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

      <style>
        {".animate-fadeIn { animation: fadeIn 0.4s ease-in-out; } @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }"}
      </style>
    </div>
  );
}