import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Profile from "./pages/Profile";
import Connections from "./pages/Connections";

export default function App(){
 return <BrowserRouter><div className="min-h-screen bg-slate-50"><Navbar/><main className="max-w-6xl mx-auto p-4"><Routes><Route path="/" element={<Navigate to="/dashboard" replace />} /><Route path="/login" element={<Login/>}/><Route path="/signup" element={<Register/>}/><Route path="/forgot-password" element={<ForgotPassword/>}/><Route path="/reset-password" element={<ResetPassword/>}/><Route path="/dashboard" element={<ProtectedRoute><Dashboard/></ProtectedRoute>}/><Route path="/history" element={<ProtectedRoute><History/></ProtectedRoute>}/><Route path="/profile" element={<ProtectedRoute><Profile/></ProtectedRoute>}/><Route path="/connections" element={<ProtectedRoute><Connections/></ProtectedRoute>}/></Routes></main></div></BrowserRouter>
}
