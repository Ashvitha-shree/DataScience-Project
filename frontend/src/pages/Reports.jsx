import React, { useState } from "react";
import { FileText, Download } from "lucide-react";

const REPORT_TYPES = [
  { value: "daily", label: "Daily Report", desc: "Summary of the last 24 hours" },
  { value: "weekly", label: "Weekly Report", desc: "Summary of the last 7 days" },
  { value: "monthly", label: "Monthly Report", desc: "Summary of the last 30 days" },
];

export default function Reports() {
  const [downloading, setDownloading] = useState("");

  const handleDownload = async (type) => {
    setDownloading(type);
    try {
      const { downloadReport } = await import("../api/client.js");
      const res = await downloadReport(type);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}_report.pdf`;
      a.click();
    } catch (e) {
      alert("Failed to generate report. Make sure the backend is running and you are logged in.");
    } finally {
      setDownloading("");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Reports</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          Generate and download PDF reports summarizing traffic data, incidents, alerts, and agent decisions.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {REPORT_TYPES.map((r) => (
          <div key={r.value} className="card flex flex-col items-start gap-3">
            <div className="p-3 rounded-xl bg-primary-50 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400">
              <FileText size={22} />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800 dark:text-slate-100">{r.label}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{r.desc}</p>
            </div>
            <button
              className="btn-primary flex items-center gap-2 mt-2"
              onClick={() => handleDownload(r.value)}
              disabled={downloading === r.value}
            >
              <Download size={16} />
              {downloading === r.value ? "Generating..." : "Download PDF"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
