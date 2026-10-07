function DeleteHistory() {
  const [deleting, setDeleting] = useState(false);
  const [message, setMessage] = useState("");

  const handleDeleteHistory = async () => {
    if (!window.confirm("Delete all of your diagnosis history and uploaded images?")) {
      return;
    }

    try {
      setDeleting(true);
      setMessage("");
      const response = await api.delete("/history");
      setMessage(
        String(response.data.deleted_count || 0) +
          " history item(s) deleted successfully."
      );
    } catch (error) {
      setMessage(
        error.response?.data?.error ||
          "Could not delete your history. Please try again."
      );
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-5">
      <h3 className="text-lg font-semibold text-red-800">
        Delete Your Diagnosis History
      </h3>
      <p className="mt-1 text-sm text-red-700">
        This permanently deletes your saved diagnosis history and associated
        uploaded images from the application.
      </p>
      <button
        onClick={handleDeleteHistory}
        disabled={deleting}
        className="mt-4 rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
      >
        {deleting ? "Deleting..." : "Delete All History"}
      </button>
      {message && <p className="mt-3 text-sm text-red-700">{message}</p>}
    </div>
  );
}

// src/pages/Privacy.jsx
import { useState } from "react";
import { Helmet } from "react-helmet";
import api from "../services/api";

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
        {localStorage.getItem("access_token") && (
          <DeleteHistory />
        )}

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