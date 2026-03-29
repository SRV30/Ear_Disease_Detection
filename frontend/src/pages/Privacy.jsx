// src/pages/Privacy.jsx
import { Helmet } from "react-helmet";

export default function Privacy() {
  return (
    <>
      <Helmet>
        <title>Privacy Policy | EarCare AI Clinic</title>
        <meta
          name="description"
          content="Read the privacy policy for EarCare AI Clinic and learn how we handle your data and medical images."
        />
      </Helmet>

      <section className="max-w-5xl mx-auto px-4 py-10 space-y-4 text-sm md:text-base text-slate-700">
        <h2 className="text-3xl font-bold text-slate-900 mb-3">
          Privacy Policy
        </h2>
        <p>
          EarCare AI Clinic respects your privacy and is committed to
          protecting your personal data. This policy explains how we
          collect, use, and safeguard information when you use our
          ear-disease detection service.
        </p>
        <h3 className="text-lg font-semibold text-slate-900 mt-4">
          1. Image Processing
        </h3>
        <p>
          Uploaded ear images are used solely for generating predictions
          and may be temporarily stored on our secure server for
          processing. We do not sell or share your images with any third
          parties.
        </p>
        <h3 className="text-lg font-semibold text-slate-900 mt-4">
          2. No Medical Replacement
        </h3>
        <p>
          Our AI tool is decision-support software. It does not replace a
          physical examination by a qualified ENT specialist. Always
          consult your doctor for diagnosis and treatment decisions.
        </p>
        <h3 className="text-lg font-semibold text-slate-900 mt-4">
          3. Contact
        </h3>
        <p>
          If you have any questions about this policy, please contact us
          at <span className="font-mono">care@earcare-ai.com</span>.
        </p>
      </section>
    </>
  );
}