import { Helmet } from "react-helmet";
import { useNavigate } from "react-router-dom";
import img from "../assets/norm.jpg";

export default function Home() {
  const navigate = useNavigate();

  return (
    <>
      <Helmet>
        <title>EarCare AI Clinic | AI Ear Infection Detection</title>
        <meta
          name="description"
          content="EarCare AI Clinic uses deep learning to detect ear infections and wax blockage from ear images within seconds."
        />
      </Helmet>

      <section className="max-w-6xl mx-auto px-4 py-10 md:py-16">
        {/* Hero */}
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div>
            <p className="text-xs font-semibold tracking-[0.25em] text-indigo-500 uppercase mb-3">
              AI-POWERED EAR HEALTH
            </p>
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-slate-900 mb-4 leading-tight">
              Early detection of{" "}
              <span className="text-indigo-600">
                Ear Infections & Wax
              </span>{" "}
              in seconds.
            </h1>
            <p className="text-sm md:text-base text-slate-600 mb-6 max-w-xl">
              Upload an otoscopic ear image and our AI model instantly
              analyzes for signs of infection or wax blockage, helping
              ENT specialists make faster, data-driven decisions.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => navigate("/diagnose")}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3 rounded-xl shadow-md text-sm md:text-base"
              >
                Start Diagnosis
              </button>
              <button
                onClick={() => navigate("/about")}
                className="border border-indigo-200 text-indigo-700 hover:bg-indigo-50 font-medium px-5 py-3 rounded-xl text-sm md:text-base"
              >
                Learn more
              </button>
            </div>

            <div className="mt-8 grid grid-cols-3 gap-4 text-center text-xs md:text-sm">
              <div className="bg-white rounded-2xl shadow-sm p-3 border border-slate-100">
                <p className="font-bold text-indigo-600 text-lg md:text-xl">
                  &lt; 5s
                </p>
                <p className="text-slate-500">Average analysis time</p>
              </div>
              <div className="bg-white rounded-2xl shadow-sm p-3 border border-slate-100">
                <p className="font-bold text-indigo-600 text-lg md:text-xl">
                  3+
                </p>
                <p className="text-slate-500">Conditions screened</p>
              </div>
              <div className="bg-white rounded-2xl shadow-sm p-3 border border-slate-100">
                <p className="font-bold text-indigo-600 text-lg md:text-xl">
                  24/7
                </p>
                <p className="text-slate-500">Online access</p>
              </div>
            </div>
          </div>

          {/* Hero illustration (simple gradient card) */}
          <div className="relative">
            <div className="rounded-3xl bg-linear-to-br from-indigo-500 via-sky-500 to-cyan-400 h-64 md:h-80 shadow-2xl flex items-center justify-center">
              <div className="bg-white/90 rounded-2xl p-4 w-60 md:w-72 shadow-lg">
                <p className="text-xs font-semibold text-slate-500 mb-2">
                  AI Diagnosis Preview
                </p>
                <div className="h-32 bg-slate-100 rounded-xl mb-3 flex items-center justify-center text-slate-400 text-xs">
                  <img src={img} alt="AI Diagnosis Preview" className="w-full h-full object-fit rounded-xl" />
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  Likely Condition:{" "}
                  <span className="text-indigo-600">Normal</span>
                </p>
                <p className="text-xs text-slate-500">
                  Confidence: 98.4%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <section className="mt-16 grid md:grid-cols-3 gap-6">
          {[
            {
              title: "Clinician friendly",
              text: "Designed to support ENT specialists with clear visualizations and probability scores.",
            },
            {
              title: "AI + Human expertise",
              text: "AI never replaces doctors – it augments them with fast triage & second opinions.",
            },
            {
              title: "Secure & Private",
              text: "Images are processed securely on our servers and never shared with third parties.",
            },
          ].map((f) => (
            <div
              key={f.title}
              className="bg-white border border-slate-100 rounded-2xl shadow-sm p-5"
            >
              <h3 className="text-sm font-semibold text-slate-900 mb-2">
                {f.title}
              </h3>
              <p className="text-xs md:text-sm text-slate-600">
                {f.text}
              </p>
            </div>
          ))}
        </section>
      </section>
    </>
  );
}