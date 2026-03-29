import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [show, setShow] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleRegister = async () => {
    if (!email || !password || !confirm) {
      return alert("Fill all fields");
    }

    if (password !== confirm) {
      return alert("Passwords do not match");
    }

    if (password.length < 6) {
      return alert("Password must be at least 6 characters");
    }

    try {
      setLoading(true);

      await api.post("/signup", { email, password });

      alert("Account created successfully");
      navigate("/login");
    } catch {
      alert("Signup failed (email may already exist)");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-100 via-white to-purple-100 px-4">
      <div className="w-full max-w-md backdrop-blur-xl bg-white/60 border border-white/30 shadow-2xl rounded-3xl p-8 space-y-6">

        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">
            Create Account 🚀
          </h2>
          <p className="text-sm text-gray-500">
            Start your AI-powered ear diagnosis journey
          </p>
        </div>

        <div className="space-y-4">

          <div>
            <label className="text-xs text-gray-500">Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              className="w-full mt-1 p-3 rounded-xl bg-white/70 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-300"
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="text-xs text-gray-500">Password</label>

            <div className="relative">
              <input
                type={show ? "text" : "password"}
                placeholder="Create password"
                className="w-full mt-1 p-3 rounded-xl bg-white/70 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-300 pr-10"
                onChange={(e) => setPassword(e.target.value)}
              />

              <span
                onClick={() => setShow(!show)}
                className="absolute right-3 top-3 cursor-pointer text-gray-500 text-sm"
              >
                {show ? "🙈" : "👁"}
              </span>
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-500">Confirm Password</label>

            <div className="relative">
              <input
                type={showConfirm ? "text" : "password"}
                placeholder="Confirm password"
                className="w-full mt-1 p-3 rounded-xl bg-white/70 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-300 pr-10"
                onChange={(e) => setConfirm(e.target.value)}
              />

              <span
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-3 top-3 cursor-pointer text-gray-500 text-sm"
              >
                {showConfirm ? "🙈" : "👁"}
              </span>
            </div>
          </div>

          <div className="flex justify-end text-xs">
            <span
              onClick={() => navigate("/login")}
              className="cursor-pointer text-indigo-600 hover:underline font-medium"
            >
              Already have an account?
            </span>
          </div>
        </div>

        <button
          onClick={handleRegister}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-linear-to-r from-blue-500 to-purple-500 text-white font-semibold shadow-md hover:opacity-90 transition"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>

        <p className="text-[11px] text-center text-gray-400">
          Your data is securely stored and protected
        </p>
      </div>
    </div>
  );
}