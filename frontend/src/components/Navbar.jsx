import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar(){
 const {isAuthenticated,logout}=useAuth();
 return <header className="bg-white border-b"><div className="max-w-6xl mx-auto p-4 flex justify-between"><Link to="/dashboard" className="font-bold text-indigo-700">EarCare AI</Link><nav className="flex gap-4 text-sm items-center">{isAuthenticated && <><Link to="/dashboard">Dashboard</Link><Link to="/history">History</Link><Link to="/profile">Profile</Link><Link to="/connections">Connections</Link><button onClick={logout} className="px-3 py-1 bg-red-500 text-white rounded">Logout</button></>}{!isAuthenticated && <><Link to="/login">Login</Link><Link to="/signup">Signup</Link></>}</nav></div></header>
}
