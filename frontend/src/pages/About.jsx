import { Helmet } from "react-helmet";
import logo from "../assets/favicon.png";

export default function About() {
  return (
    <>
      <Helmet>
        <title>About | EarCare AI Clinic</title>
        <meta
          name="description"
          content="Learn about EarCare AI Clinic, our mission and how we use AI to support ENT specialists."
        />
      </Helmet>

      <section className="max-w-6xl mx-auto px-4 py-12 space-y-12">

        <div className="text-center max-w-3xl mx-auto">

          <img
            src={logo}
            alt="EarCare AI Logo"
            className="w-20 h-20 mx-auto mb-4 drop-shadow-lg"
          />

          <h2 className="text-4xl font-extrabold text-slate-900 mb-4">
            About EarCare AI Clinic
          </h2>

          <p className="text-base md:text-lg text-slate-600 leading-relaxed">
            EarCare AI Clinic blends medical expertise with artificial intelligence
            to detect ear infections and wax blockage from otoscopic images using
            deep learning. Our vision is to make ear care faster, affordable and
            accessible globally.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              title: "Our Mission",
              desc: "Provide AI-powered early screening tools while keeping doctors at the center of clinical decisions.",
            },
            {
              title: "Clinical Support",
              desc: "Grad-CAM visualization and probability insights help ENT specialists make faster, data-driven decisions.",
            },
            {
              title: "Patient Experience",
              desc: "Clear AI-generated reports improve understanding and confidence in diagnosis and treatment.",
            },
          ].map((box) => (
            <div
              key={box.title}
              className="bg-white backdrop-blur-lg border border-indigo-100 p-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all hover:-translate-y-1"
            >
              <h3 className="text-lg font-semibold text-indigo-700 mb-2">
                {box.title}
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {box.desc}
              </p>
            </div>
          ))}
        </div>

        <div className="pt-6">
          <h3 className="text-3xl font-bold text-slate-900 text-center mb-10">
            Technology & Innovation
          </h3>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Deep Learning Model",
                desc: "EfficientNet-based architecture trained on medical datasets for high accuracy classification.",
              },
              {
                title: "Explainable AI",
                desc: "Grad-CAM heatmaps highlight regions influencing predictions, improving trust and transparency.",
              },
              {
                title: "Secure & Scalable",
                desc: "JWT authentication and cloud-ready backend ensure secure, scalable medical AI deployment.",
              },
            ].map((item) => (
              <div
                key={item.title}
                className="bg-white border border-slate-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition"
              >
                <h4 className="font-semibold text-indigo-700 mb-2">
                  {item.title}
                </h4>
                <p className="text-sm text-slate-600 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-linear-to-r from-indigo-600 to-blue-500 text-white rounded-3xl shadow-xl text-center px-6 py-12">
          <h3 className="text-2xl md:text-3xl font-bold mb-3">
            “Human Intelligence + Artificial Intelligence = Future of Healthcare”
          </h3>
          <p className="text-sm md:text-base opacity-90 max-w-3xl mx-auto leading-relaxed">
            EarCare AI Clinic empowers doctors with AI-driven insights to improve
            diagnostic speed, accuracy, and patient outcomes.
          </p>
        </div>

      </section>
    </>
  );
}