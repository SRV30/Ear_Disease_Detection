import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function ProtectedThumbnail({ url }) {
  const [objectUrl, setObjectUrl] = useState("");

  useEffect(() => {
    let active = true;
    let createdUrl = "";

    const load = async () => {
      try {
        const response = await api.get(url, { responseType: "blob" });
        createdUrl = URL.createObjectURL(response.data);
        if (active) {
          setObjectUrl(createdUrl);
        } else {
          URL.revokeObjectURL(createdUrl);
        }
      } catch {
        if (active) setObjectUrl("");
      }
    };

    load();

    return () => {
      active = false;
      if (createdUrl) URL.revokeObjectURL(createdUrl);
    };
  }, [url]);

  if (!objectUrl) {
    return (
      <div className="w-14 h-14 rounded bg-gray-100 border flex items-center justify-center text-[10px] text-gray-400">
        Image
      </div>
    );
  }

  return (
    <img
      src={objectUrl}
      alt="Diagnosis"
      className="w-14 h-14 rounded object-cover"
    />
  );
}

export default function HistoryCard({ history }) {
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
            key={item.id || String(item.image_url) + "-" + String(item.prediction) + "-" + idx}
            className="flex items-center gap-4 border p-3 rounded-lg mb-2"
          >
            <ProtectedThumbnail url={item.image_url} />

            <div className="flex-1">
              <p>
                {item.prediction}
                <span className={"ml-2 px-2 text-white " + color}>
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
