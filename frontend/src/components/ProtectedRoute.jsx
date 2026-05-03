import { Navigate } from "react-router-dom";
import { isTokenExpired } from "../services/authSession";

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  if (!token || isTokenExpired(token)) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    return <Navigate to="/login" replace />;
  }

  return children;
}
