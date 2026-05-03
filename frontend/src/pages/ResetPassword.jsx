import { useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

export default function ResetPassword(){
 const [token,setToken]=useState(""); const [password,setPassword]=useState("");
 const submit=async(e)=>{e.preventDefault(); try{await api.post('/reset-password',{token,password}); toast.success('Password reset successful');}catch{toast.error('Reset failed')}};
 return <form onSubmit={submit} className="max-w-md mx-auto bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Reset password</h1><input className="w-full border p-3 rounded-xl" placeholder="Reset token" value={token} onChange={(e)=>setToken(e.target.value)} /><input type="password" className="w-full border p-3 rounded-xl" placeholder="New password" value={password} onChange={(e)=>setPassword(e.target.value)} /><button className="w-full bg-indigo-600 text-white py-3 rounded-xl">Reset password</button></form>
}
