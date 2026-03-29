import { useNavigate } from "react-router-dom";

export default function HistoryCard({ history, backendURL }) {
  const navigate = useNavigate();

  return (
    <div>
      <h2 className="text-xl font-bold mb-3">History</h2>

      {history.map((item, idx) => {
        const label = (item.prediction || "unknown").toLowerCase();

        const color = label.includes("normal")
          ? "bg-green-600"
          : label.includes("wax")
            ? "bg-yellow-500"
            : "bg-red-600";

        return (
          <div
            key={idx}
            className="flex items-center gap-4 border p-3 rounded-lg mb-2"
          >
            <img
              src={`${backendURL}${item.image_url}`}
              className="w-14 h-14 rounded"
            />

            <div className="flex-1">
              <p>
                {item.prediction}
                <span className={`ml-2 px-2 text-white ${color}`}>
                  {item.confidence}%
                </span>
              </p>
            </div>

            <button
              onClick={() => navigate("/result", { state: { result: item } })}
            >
              View →
            </button>
          </div>
        );
      })}
    </div>
  );
}
