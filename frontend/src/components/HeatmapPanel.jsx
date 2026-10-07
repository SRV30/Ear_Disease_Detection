import { useEffect, useState } from "react";
import api from "../services/api";

function ProtectedImage({ url, alt }) {
  const [objectUrl, setObjectUrl] = useState(null);

  useEffect(() => {
    let active = true;
    let createdUrl = null;

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
        if (active) {
          setObjectUrl(null);
        }
      }
    };

    load();

    return () => {
      active = false;
      if (createdUrl) {
        URL.revokeObjectURL(createdUrl);
      }
    };
  }, [url]);

  if (!objectUrl) {
    return (
      <div className="w-full aspect-video rounded-xl border bg-gray-100 flex items-center justify-center text-sm text-gray-500">
        Loading image...
      </div>
    );
  }

  return (
    <img
      src={objectUrl}
      alt={alt}
      className="w-full rounded-xl border"
    />
  );
}

export default function HeatmapPanel({ imageUrl, heatmapUrl }) {
  if (!heatmapUrl) return null;

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-1">Original</p>
        <ProtectedImage url={imageUrl} alt="Original ear" />
      </div>
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-1">
          Grad-CAM Heatmap
        </p>
        <ProtectedImage url={heatmapUrl} alt="Grad-CAM heatmap" />
      </div>
    </div>
  );
}
