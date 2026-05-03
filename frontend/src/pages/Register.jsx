import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../services/api";

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passRe = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,64}$/;

export default function Register() {
  const [form, setForm] = useState({ email: "", password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const submit = async (e) => {
    e.preventDefault();
    if (!emailRe.test(form.email)) return toast.error("Invalid email");
    if (!passRe.test(form.password)) return toast.error("Password must be strong");
    if (form.password !== form.confirm) return toast.error("Passwords do not match");
    try { setLoading(true); await api.post("/signup", { email: form.email, password: form.password }); toast.success("Account created"); navigate("/login"); }
    catch { toast.error("Signup failed"); } finally { setLoading(false); }
  };
  return <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Sign up</h1><input className="w-full border p-3 rounded-xl" placeholder="Email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})}/><input type="password" className="w-full border p-3 rounded-xl" placeholder="Password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})}/><input type="password" className="w-full border p-3 rounded-xl" placeholder="Confirm password" value={form.confirm} onChange={(e)=>setForm({...form,confirm:e.target.value})}/><button disabled={loading} className="w-full bg-indigo-600 text-white py-3 rounded-xl">{loading?"Creating...":"Create account"}</button><Link to="/login" className="text-indigo-600 text-sm">Back to login</Link></form>;
}
