export default function PDFReportBtn({ downloadPDF }) {
  return (
    <button onClick={downloadPDF} className="bg-green-600 hover:bg-green-700 text-white font-semibold px-5 py-2 rounded-xl shadow">
      Download PDF Report
    </button>
  );
}