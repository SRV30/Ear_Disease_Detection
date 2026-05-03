export default function SystemNotice({ notice, onClose }) {
  if (!notice?.message) return null;

  const tone = notice.type === 'warning'
    ? 'bg-yellow-50 text-yellow-800 border-yellow-200'
    : 'bg-red-50 text-red-800 border-red-200';

  return (
    <div className={`border rounded-lg px-3 py-2 text-sm ${tone}`} role="status" aria-live="polite">
      <div className="flex items-center justify-between gap-2">
        <span>{notice.message}</span>
        <button onClick={onClose} className="text-xs underline">Dismiss</button>
      </div>
    </div>
  );
}
