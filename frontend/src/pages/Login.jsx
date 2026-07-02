import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { TrafficCone } from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const [email, setEmail] = useState("admin@smarttraffic.local");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-primary-900 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-primary-600 rounded-2xl mb-3">
            <TrafficCone className="text-white" size={28} />
          </div>
          <h1 className="text-2xl font-bold text-white">Smart City Traffic Management</h1>
          <p className="text-slate-300 text-sm mt-1">Admin / Traffic Officer Login</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-3 py-2 rounded-lg border border-red-200">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="input-field" placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Password</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="input-field" placeholder="••••••••"
            />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full justify-center flex">
            {loading ? "Signing in..." : "Sign In"}
          </button>
          <p className="text-xs text-center text-slate-500 dark:text-slate-400 pt-2">
            Default admin: <strong>admin@smarttraffic.local</strong> / <strong>Admin@123</strong>
            <br />(created automatically on first backend startup)
          </p>
        </form>
      </div>
    </div>
  );
}
