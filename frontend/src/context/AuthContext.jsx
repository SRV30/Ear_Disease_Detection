import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(localStorage.getItem("access_token") || "");
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem("refresh_token") || "");

  const login = ({ access_token, refresh_token }) => {
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    setAccessToken(access_token);
    setRefreshToken(refresh_token);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setAccessToken("");
    setRefreshToken("");
  };

  const value = useMemo(() => ({ accessToken, refreshToken, isAuthenticated: !!accessToken, login, logout }), [accessToken, refreshToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
