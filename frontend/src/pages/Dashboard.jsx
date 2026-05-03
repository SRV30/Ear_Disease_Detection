import { useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

export default function Dashboard(){
  const [file,setFile]=useState(null); const [result,setResult]=useState(null); const [loading,setLoading]=useState(false);
  const predict=async()=>{ if(!file) return toast.error('Upload image'); const fd=new FormData(); fd.append('file',file); try{setLoading(true); const {data}=await api.post('/predict',fd); setResult(data); toast.success('Prediction complete');}catch{toast.error('Prediction failed')}finally{setLoading(false)}};
  return <div className="grid gap-6 lg:grid-cols-2"><div className="bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">AI Diagnosis</h1><input type="file" accept="image/*" onChange={(e)=>setFile(e.target.files?.[0])} /><button onClick={predict} className="bg-indigo-600 text-white px-5 py-2 rounded-xl">{loading?'Analyzing...':'Predict'}</button></div><div className="bg-white p-6 rounded-2xl shadow">{result? <div className="space-y-2"><p><b>Disease:</b> {result.prediction}</p><p><b>Confidence:</b> {result.confidence}%</p>{result.image_url && <img src={`${api.defaults.baseURL}${result.image_url}`} className="rounded-xl"/>}{result.heatmap_url && <img src={`${api.defaults.baseURL}${result.heatmap_url}`} className="rounded-xl"/>}</div>:<p className="text-slate-500">Result will appear here.</p>}</div></div>
}
