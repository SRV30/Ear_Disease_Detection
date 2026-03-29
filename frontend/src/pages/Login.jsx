import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!email || !password) return alert("Fill all fields");

    try {
      setLoading(true);

      const res = await api.post("/login", { email, password });

      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("refresh_token", res.data.refresh_token);

      navigate("/diagnose");
      window.location.reload();
    } catch {
      alert("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-blue-100 via-white to-purple-100 px-4">
      <div className="w-full max-w-md backdrop-blur-xl bg-white/60 border border-white/30 shadow-2xl rounded-3xl p-8 space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">Welcome Back 👋</h2>
          <p className="text-sm text-gray-500">
            Login to continue your diagnosis
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
                placeholder="Enter password"
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

          <div className="flex justify-between text-xs text-gray-500">
            <span
              onClick={() => alert("Forgot password feature coming soon")}
              className="cursor-pointer hover:text-indigo-600"
            >
              Forgot password?
            </span>

            <span
              onClick={() => navigate("/register")}
              className="cursor-pointer hover:text-indigo-600 font-medium"
            >
              Sign up
            </span>
          </div>
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full py-3 rounded-xl bg-linear-to-r from-blue-500 to-purple-500 text-white font-semibold shadow-md hover:opacity-90 transition"
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="text-[11px] text-center text-gray-400">
          Secure login powered by JWT authentication
        </p>
      </div>
    </div>
  );
}
