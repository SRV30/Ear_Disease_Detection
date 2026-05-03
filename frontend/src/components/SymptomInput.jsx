export default function SymptomInput({ value, onChange }) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700">Symptoms (optional)</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        placeholder="e.g., ear pain, discharge, hearing loss"
        className="w-full mt-1 p-3 rounded-xl bg-white/70 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-300"
      />
    </div>
  );
}
