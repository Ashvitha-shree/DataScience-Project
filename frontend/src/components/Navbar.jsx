import React from "react";
import { Menu, Sun, Moon, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar({ dark, onToggleDark, onToggleSidebar }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex items-center justify-between px-6 py-3 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
      <button onClick={onToggleSidebar} className="text-slate-600 dark:text-slate-300">
        <Menu size={20} />
      </button>

      <div className="flex items-center gap-4">
        <button
          onClick={onToggleDark}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300"
          title="Toggle dark mode"
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="text-right hidden sm:block">
          <div className="text-sm font-medium text-slate-800 dark:text-slate-100">{user?.name}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 capitalize">{user?.role}</div>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-1 text-sm text-red-600 hover:text-red-700 font-medium"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </header>
  );
}
