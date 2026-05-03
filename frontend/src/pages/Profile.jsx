import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import api from "../services/api";

export default function Profile(){
 const [profile,setProfile]=useState(null); const [name,setName]=useState(''); const [avatar,setAvatar]=useState('');
 useEffect(()=>{(async()=>{const {data}=await api.get('/profile'); setProfile(data); setName(data.name||''); setAvatar(data.avatar||'');})();},[]);
 const save=async()=>{try{await api.patch('/profile',{name,avatar}); toast.success('Profile updated');}catch{toast.error('Update failed')}};
 if(!profile) return <div>Loading...</div>;
 return <div className="bg-white p-6 rounded-2xl shadow space-y-4"><h1 className="text-2xl font-bold">Profile</h1><p><b>Email:</b> {profile.email}</p><input className="w-full border p-3 rounded-xl" value={name} onChange={(e)=>setName(e.target.value)} placeholder="Name"/><input className="w-full border p-3 rounded-xl" value={avatar} onChange={(e)=>setAvatar(e.target.value)} placeholder="Avatar URL"/>{avatar && <img src={avatar} className="w-20 h-20 rounded-full"/>}<button onClick={save} className="bg-indigo-600 text-white px-4 py-2 rounded-xl">Save</button></div>
}
