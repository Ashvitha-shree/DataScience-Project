import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar.jsx";
import Navbar from "./Navbar.jsx";

export default function Layout() {
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100 dark:bg-slate-900">
      <Sidebar open={sidebarOpen} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar
          dark={dark}
          onToggleDark={() => setDark((d) => !d)}
          onToggleSidebar={() => setSidebarOpen((s) => !s)}
        />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
