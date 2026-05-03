export default function HeatmapPanel({ backendURL, imageUrl, heatmapUrl }) {
  if (!heatmapUrl) return null;

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-1">Original</p>
        <img src={`${backendURL}${imageUrl}`} alt="Original ear" className="w-full rounded-xl border" />
      </div>
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-1">Grad-CAM Heatmap</p>
        <img src={`${backendURL}${heatmapUrl}`} alt="Grad-CAM heatmap" className="w-full rounded-xl border" />
      </div>
    </div>
  );
}
