import { useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

export default function ForgotPassword(){
  const [email,setEmail]=useState(""); const [loading,setLoading]=useState(false);
  const submit=async(e)=>{e.preventDefault(); try{setLoading(true); await api.post('/forgot-password',{email}); toast.success('If account exists, reset link sent');}catch{toast.error('Request failed')}finally{setLoading(false)}};
  return <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Forgot password</h1><input className="w-full border p-3 rounded-xl" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} /><button className="w-full bg-indigo-600 text-white py-3 rounded-xl">{loading?"Submitting...":"Send reset link"}</button></form>
}
