import { useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

export default function Connections(){
 const [q,setQ]=useState(''); const [users,setUsers]=useState([]); const [requester,setRequester]=useState('');
 const search=async()=>{try{const {data}=await api.get(`/users/search?q=${encodeURIComponent(q)}`); setUsers(data);}catch{toast.error('Search failed')}};
 const sendReq=async(id)=>{try{await api.post('/connections/request',{target_user_id:id}); toast.success('Request sent');}catch{toast.error('Failed')}};
 const accept=async()=>{try{await api.post('/connections/accept',{requester_user_id:requester}); toast.success('Accepted');}catch{toast.error('Failed')}};
 return <div className="bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Connections</h1><div className="flex gap-2"><input className="border p-2 rounded-xl flex-1" value={q} onChange={(e)=>setQ(e.target.value)} placeholder="Search by email"/><button onClick={search} className="px-4 py-2 bg-indigo-600 text-white rounded-xl">Search</button></div>{users.map(u=><div key={u.id} className="border p-3 rounded-xl flex justify-between"><span>{u.email}</span><button onClick={()=>sendReq(u.id)} className="text-indigo-600">Connect</button></div>)}<div className="pt-4 border-t"><h2 className="font-semibold">Accept request</h2><input className="border p-2 rounded-xl w-full" value={requester} onChange={(e)=>setRequester(e.target.value)} placeholder="Requester user id"/><button onClick={accept} className="mt-2 px-4 py-2 bg-emerald-600 text-white rounded-xl">Accept</button></div></div>
}
