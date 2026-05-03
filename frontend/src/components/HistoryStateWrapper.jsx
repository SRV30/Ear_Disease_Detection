import HistoryCard from './HistoryCard';

export default function HistoryStateWrapper({ loading, error, history, backendURL }) {
  if (loading) return <p className="text-sm text-gray-500">Loading history...</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!history?.length) return <p className="text-sm text-gray-500">No diagnosis history yet.</p>;
  return <HistoryCard history={history} backendURL={backendURL} />;
}
