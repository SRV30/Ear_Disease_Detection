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
        if (active) setObjectUrl(createdUrl);
        else URL.revokeObjectURL(createdUrl);
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
      <div className="w-16 h-16 rounded bg-gray-100 border flex items-center justify-center text-[10px] text-gray-400">
        Image
      </div>
    );
  }

  return <img src={objectUrl} alt="Diagnosis" className="w-16 h-16 rounded-lg object-cover" />;
}

export default function HistoryCard({ history, onDelete }) {
  const navigate = useNavigate();
  const [deletingId, setDeletingId] = useState("");

  const deleteItem = async (id) => {
    if (!id || !window.confirm("Delete this diagnosis from history?")) return;

    try {
      setDeletingId(id);
      await api.delete(`/history/${id}`);
      onDelete?.(id);
    } catch {
      window.alert("Unable to delete this history item.");
    } finally {
      setDeletingId("");
    }
  };

  const formatDate = (value) => {
    if (!value) return "Date unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? "Date unavailable" : date.toLocaleString();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-bold">History</h2>
        <span className="text-sm text-gray-500">{history.length} record{history.length === 1 ? "" : "s"}</span>
      </div>

      <div className="space-y-3">
        {history.map((item, idx) => {
          const label = (item.prediction || "unknown").toLowerCase();
          const color = label.includes("normal")
            ? "bg-green-600"
            : label.includes("cerumen")
              ? "bg-yellow-500"
              : "bg-red-600";

          return (
            <div
              key={item.id || String(item.image_url) + "-" + String(item.prediction) + "-" + idx}
              className="border rounded-xl p-3 flex flex-wrap items-center gap-4 bg-white/60"
            >
              <ProtectedThumbnail url={item.image_url} />

              <div className="flex-1 min-w-[180px]">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-semibold">{item.prediction}</p>
                  <span className={"px-2 py-0.5 rounded text-white text-xs " + color}>
                    {Number(item.confidence).toFixed(4)}%
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{formatDate(item.created_at)}</p>
                <p className="text-xs text-gray-500">Risk: {item.risk || "N/A"}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => navigate("/result", { state: { result: item } })}
                  className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-sm"
                >
                  View
                </button>
                <button
                  onClick={() => deleteItem(item.id)}
                  disabled={deletingId === item.id}
                  className="px-3 py-1.5 rounded-lg bg-red-600 text-white text-sm disabled:opacity-60"
                >
                  {deletingId === item.id ? "Deleting..." : "Delete"}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
