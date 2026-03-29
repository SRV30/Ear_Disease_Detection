export default function Hospitals({ mapsUrl, locationMsg }) {
  return (
    <div className="mt-14">
      <h2 className="text-2xl font-bold text-slate-900 mb-4">
        Nearby ENT / Ear Hospitals
      </h2>

      {!mapsUrl && (
        <div className="bg-white border border-slate-200 rounded-2xl shadow p-6 text-center">
          <img
            src="https://cdn-icons-png.flaticon.com/512/3916/3916594.png"
            alt="location"
            className="w-16 mx-auto opacity-80 mb-3"
          />
          <p className="text-sm text-slate-600">{locationMsg}</p>
        </div>
      )}

      {mapsUrl && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-lg p-6 space-y-5">
          <div className="space-y-4">
            {[
              {
                name: "➡ Best ENT Specialist Near You",
                desc: "Recommended for diagnosis & ear infection treatment.",
              },
              {
                name: "➡ Ear & Hearing Care Center",
                desc: "Wax removal, ear checkup and emergency care.",
              },
              {
                name: "➡ Multi-Speciality Hospital (ENT Dept.)",
                desc: "Full medical support & ENT consultation.",
              },
            ].map((h, i) => (
              <div
                key={i}
                className="bg-slate-50 p-4 rounded-xl border border-slate-200 hover:bg-slate-100 transition-all shadow-sm"
              >
                <p className="text-sm font-semibold text-slate-900">{h.name}</p>
                <p className="text-xs text-slate-500">{h.desc}</p>
              </div>
            ))}
          </div>

          <a
            href={mapsUrl}
            target="_blank"
            rel="noreferrer"
            className="block text-center w-full bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3 rounded-2xl shadow-md text-sm transition-all"
          >
            🔍 View Exact Nearby Hospitals on Google Maps
          </a>

          <p className="text-[10px] text-slate-500 text-center">
            Location is used only to find hospitals — we do not store or track your data.
          </p>
        </div>
      )}
    </div>
  );
}