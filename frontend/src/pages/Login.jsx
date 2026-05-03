import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    if (!emailRe.test(email)) return toast.error("Enter valid email");
    if (!password) return toast.error("Password required");
    try {
      setLoading(true);
      const { data } = await api.post("/login", { email, password });
      login(data);
      toast.success("Logged in");
      navigate("/dashboard");
    } catch {
      toast.error("Invalid credentials");
    } finally { setLoading(false); }
  };

  return <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Login</h1><input className="w-full border p-3 rounded-xl" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} /><input type="password" className="w-full border p-3 rounded-xl" placeholder="Password" value={password} onChange={(e)=>setPassword(e.target.value)} /><button disabled={loading} className="w-full bg-indigo-600 text-white py-3 rounded-xl">{loading?"Signing in...":"Login"}</button><div className="flex justify-between text-sm"><Link to="/forgot-password" className="text-indigo-600">Forgot password?</Link><Link to="/signup" className="text-indigo-600">Create account</Link></div></form>;
}
