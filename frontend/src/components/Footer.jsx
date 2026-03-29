// src/components/Footer.jsx
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-200 mt-10">
      <div className="max-w-6xl mx-auto px-4 py-8 grid md:grid-cols-3 gap-8">
        <div>
          <h3 className="text-lg font-semibold mb-2">EarCare AI Clinic</h3>
          <p className="text-sm text-slate-400">
            Early detection of ear infections and wax blockage using
            deep-learning powered image analysis.
          </p>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-2">Contact</h4>
          <p className="text-sm text-slate-400">
            Hall 1<br />
            IIITDMJ
          </p>
          <p className="text-sm text-slate-400 mt-1">
            Phone: +91-9182637455<br />
            Email: care@earcare-ai.com
          </p>
        </div>

        <div>
          <h4 className="text-sm font-semibold mb-2">Links</h4>
          <ul className="space-y-1 text-sm text-slate-400">
            <li>
              <Link to="/about" className="hover:text-white">
                About Us
              </Link>
            </li>
            <li>
              <Link to="/contact" className="hover:text-white">
                Contact
              </Link>
            </li>
            <li>
              <Link to="/privacy" className="hover:text-white">
                Privacy Policy
              </Link>
            </li>
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-700 text-xs text-center py-3 text-slate-500">
        © {new Date().getFullYear()} EarCare AI Clinic. All rights reserved.
      </div>
    </footer>
  );
}