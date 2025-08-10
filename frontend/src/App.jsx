import { useState, useEffect } from "react";
import "./App.css";

export default function App() {
  const [machines, setMachines] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [osFilter, setOsFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  useEffect(() => {
    fetchMachines();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [osFilter, statusFilter, machines]);

  const fetchMachines = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/machines");
      const data = await res.json();
      setMachines(data);
      setFiltered(data);
    } catch (err) {
      console.error("Error fetching machines:", err);
    }
  };

  const applyFilters = () => {
    let data = [...machines];

    if (osFilter !== "All") {
      data = data.filter((m) => m.os_name === osFilter);
    }

    if (statusFilter !== "All") {
      data = data.filter((m) => {
        const checks = m.latest_payload?.checks || {};
        const hasIssue =
          !checks.disk_encrypted?.value ||
          !checks.os_up_to_date?.value ||
          !checks.antivirus?.present ||
          (checks.inactivity_sleep_minutes?.value || 0) > 10;
        return statusFilter === "Issues" ? hasIssue : !hasIssue;
      });
    }

    setFiltered(data);
  };

  const getBadge = (condition, okText, badText) => (
    <span className={`badge ${condition ? "ok" : "bad"}`}>
      {condition ? okText : badText}
    </span>
  );

  const formatTime = (isoTime) => {
    if (!isoTime) return "—";
    return new Date(isoTime).toLocaleString();
  };

  const exportCSV = () => {
    if (!filtered.length) return;

    const headers = [
      "Machine ID",
      "Hostname",
      "OS",
      "Disk Encryption",
      "OS Update",
      "Antivirus",
      "Sleep Timer",
      "Last Seen"
    ];

    const rows = filtered.map((m) => {
      const checks = m.latest_payload?.checks || {};
      return [
        m.machine_id,
        m.hostname || "",
        `${m.os_name || ""} ${m.os_version || ""}`,
        checks.disk_encrypted?.value ? "Encrypted" : "Not Encrypted",
        checks.os_up_to_date?.value ? "Up-to-date" : "Outdated",
        checks.antivirus?.present ? "Present" : "Missing",
        (checks.inactivity_sleep_minutes?.value || 0) <= 10 ? "≤ 10 min" : "> 10 min",
        formatTime(m.last_seen)
      ];
    });

    const csvContent =
      [headers, ...rows].map((row) => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "machines_report.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const osOptions = ["All", ...new Set(machines.map((m) => m.os_name).filter(Boolean))];

  return (
    <div className="dashboard-container">
      <h1>Admin Dashboard</h1>

      {/* Filter Controls */}
      <div style={{ marginBottom: "20px", display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
        <select value={osFilter} onChange={(e) => setOsFilter(e.target.value)}>
          {osOptions.map((os) => (
            <option key={os} value={os}>
              {os}
            </option>
          ))}
        </select>

        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="All">All</option>
          <option value="Healthy">Healthy</option>
          <option value="Issues">Issues</option>
        </select>

        <button className="export-btn" onClick={exportCSV}>
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Machine ID</th>
              <th>Hostname</th>
              <th>OS</th>
              <th>Disk Encryption</th>
              <th>OS Update</th>
              <th>Antivirus</th>
              <th>Sleep Timer</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((m) => {
              const checks = m.latest_payload?.checks || {};
              return (
                <tr key={m.machine_id}>
                  <td>{m.machine_id}</td>
                  <td>{m.hostname || "—"}</td>
                  <td>{`${m.os_name || ""} ${m.os_version || ""}`}</td>
                  <td>{getBadge(checks.disk_encrypted?.value, "Encrypted", "Not Encrypted")}</td>
                  <td>{getBadge(checks.os_up_to_date?.value, "Up-to-date", "Outdated")}</td>
                  <td>{getBadge(checks.antivirus?.present, "Present", "Missing")}</td>
                  <td>{getBadge((checks.inactivity_sleep_minutes?.value || 0) <= 10, "≤ 10 min", "> 10 min")}</td>
                  <td>{formatTime(m.last_seen)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
