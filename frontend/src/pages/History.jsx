import { useEffect, useState } from "react";
import api from "../services/api";

export default function History(){
 const [items,setItems]=useState([]); const [page,setPage]=useState(1); const [total,setTotal]=useState(0); const limit=10;
 useEffect(()=>{(async()=>{const {data}=await api.get(`/history?page=${page}&limit=${limit}`); setItems(data.items||[]); setTotal(data.total||0);})();},[page]);
 const pages=Math.max(1,Math.ceil(total/limit));
 return <div className="bg-white p-6 rounded-2xl shadow"><h1 className="text-2xl font-bold mb-4">Prediction History</h1><div className="space-y-3">{items.map((h,i)=><div key={i} className="border p-3 rounded-xl"><p className="font-semibold">{h.prediction}</p><p className="text-sm">Confidence: {Number(h.confidence).toFixed(2)}%</p></div>)}</div><div className="flex gap-2 mt-4"><button disabled={page===1} onClick={()=>setPage((p)=>p-1)} className="px-3 py-1 border rounded">Prev</button><span>Page {page}/{pages}</span><button disabled={page===pages} onClick={()=>setPage((p)=>p+1)} className="px-3 py-1 border rounded">Next</button></div></div>
}
