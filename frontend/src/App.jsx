import { useState, useEffect } from "react";
import "./Button.css";
import CanvasComponent from "./threejs/Canvas";
import { io } from "socket.io-client";

export default function App() {
  // — sniffing button state —
  const [status, setStatus] = useState("idle");

  // — prediction button state —
  const [predStatus, setPredStatus] = useState("idle");
  const [fileStatus, setFileStatus] = useState("idle");
  const [predictions, setPredictions] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [didCapture, setDidCapture] = useState(false);
  const [fileMetrics, setFileMetrics] = useState(null);
  const [predFileKey, setPredFileKey] = useState(null);
  const [fileFileKey, setFileFileKey] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const pageSize = 50;

  const [malStatus, setMalStatus] = useState("idle");
  const [malPredictions, setMalPredictions] = useState([]);
  const [malFileKey, setMalFileKey] = useState(null);
  const [malPage, setMalPage] = useState(0);
  const malPageSize = 50;

  // — which view to show: "sniff" or "predict" —
  const [viewMode, setViewMode] = useState("intro");

  // live packets
  const [packets, setPackets] = useState([]);

  useEffect(() => {
    const sock = io("http://localhost:5000/packets", {
      transports: ["websocket", "polling"],
    });
    sock.on("connect", () => console.log("🔥 WS connected"));
    sock.on("packet", (pkt) =>
      setPackets((prev) => {
        const next = [...prev, pkt];
        return next.length > 1000 ? next.slice(-1000) : next;
      })
    );
    return () => sock.disconnect();
  }, []);

  // — Start/Stop Sniffing —
  const handleClick = async () => {
    setViewMode("sniff");
    if (status === "idle") {
      setDidCapture(false);
      setStatus("running");
      await fetch("/api/start-sniffing");
    } else if (status === "running") {
      setStatus("stopping");
      await fetch("/api/stop-sniffing");
      setStatus("stopped");
      setDidCapture(true);
      setTimeout(() => setStatus("idle"), 1500);
    }
  };
  const sniffLabel = {
    idle: "Start Sniffing",
    running: "Running…",
    stopping: "Stopping…",
    stopped: "Stopped",
  }[status];

  // — Run Predictions —
  const handlePredict = async () => {
    setPredStatus("reasoning");
    setViewMode("predict");
    try {
      const resp = await fetch("/api/run-predictions");
      if (!resp.ok) {
        console.error("Prediction API error", resp.status, resp.statusText);
        setPredStatus("idle");
        return;
      }
      const data = await resp.json();
      if (data.predictions) {
        setPredFileKey(data.file_key);
        setPredictions(data.predictions);
        setModelInfo(data.model_info);
        setPredStatus("done");
        // reset button after a bit if you like
        setTimeout(() => setPredStatus("idle"), 1500);
      } else {
        console.error("No predictions field in response", data);
        setPredStatus("idle");
      }
    } catch (e) {
      console.error("Fetch failed", e);
      setPredStatus("idle");
    }
  };

  const handleFilePredict = async () => {
    setFileStatus("reasoning");
    setViewMode("file");
    try {
      const resp = await fetch("/api/run-file-predictions");
      const data = await resp.json();
      if (resp.ok) {
        setFileFileKey(data.file_key);
        setFileMetrics(data);
        setFileStatus("done");
      } else {
        console.error(data.error);
        setFileStatus("idle");
      }
      setTimeout(() => setFileStatus("idle"), 1500);
    } catch (e) {
      console.error(e);
      setFileStatus("idle");
    }
  };

  const handleMalPredict = async () => {
    setMalStatus("reasoning");
    setViewMode("malicious");
    try {
      const resp = await fetch("/api/run-malicious-predictions");
      const data = await resp.json();
      if (resp.ok && data.predictions) {
        setMalFileKey(data.file_key);
        setMalPredictions(data.predictions);
        setMalPage(0);
        setMalStatus("done");
        setTimeout(() => setMalStatus("idle"), 1500);
      } else {
        console.error(data.error || "No predictions");
        setMalStatus("idle");
      }
    } catch (e) {
      console.error(e);
      setMalStatus("idle");
    }
  };

  const predLabel = {
    idle: "Run Predictions",
    reasoning: "Reasoning…",
    done: "Done",
  }[predStatus];

  const fileLabel = {
    idle: "Run File",
    reasoning: "Reasoning…",
    done: "Done",
  }[fileStatus];

  const malLabel = {
    idle: "Run Malicious",
    reasoning: "Reasoning…",
    done: "Done",
  }[malStatus];

  const total = predictions.length;
  const pageCount = Math.ceil(total / pageSize);
  const startIndex = currentPage * pageSize;
  const pageResults = predictions.slice(startIndex, startIndex + pageSize);
  const dangerousCount = predictions.filter((p) => p === 1).length;

  // total malicious predictions loaded
  const malTotal = malPredictions.length;
  // how many pages we’ll have
  const malPageCount = Math.ceil(malTotal / malPageSize);
  // slice out just the current page
  const malStart = malPage * malPageSize;
  const malPageResults = malPredictions.slice(malStart, malStart + malPageSize);

  return (
    <div className="container">
      <CanvasComponent />

      <div className="interactive">
        <h1>Threat HunterAI</h1>

        <div className="button-grid">
          {/* Sniffing */}
          <button
            className={`btn-3 ${status === "running" ? "clicked" : ""}`}
            onClick={handleClick}
            disabled={status === "stopping" || status === "stopped"}
          >
            <span className="typewriter">{sniffLabel}</span>
          </button>

          {/* Per‐packet Predictions */}
          <button
            className={`btn-3 ${predStatus === "reasoning" ? "clicked" : ""}`}
            onClick={handlePredict}
            disabled={predStatus !== "idle"}
          >
            <span className="typewriter">{predLabel}</span>
          </button>

          {/* Malicious‐data Predictions */}
          <button
            className={`btn-3 ${malStatus === "reasoning" ? "clicked" : ""}`}
            onClick={handleMalPredict}
            disabled={malStatus !== "idle"}
          >
            <span className="typewriter">{malLabel}</span>
          </button>
        </div>
      </div>

      <div className="packets">
        {viewMode === "intro" && (
          <div className="intro-container">
            <h2 className="intro-title">Begin Sniffing…</h2>
          </div>
        )}
        {viewMode === "sniff" && (
          <>
            <h2>Network Packet Flow</h2>
            <ul>
              {packets.map((pkt, i) => (
                <li key={i} className="packet-item">
                  {Object.entries(pkt)
                    .filter(([key]) => key !== "bad_packet")
                    .map(([key, val]) => (
                      <div className="packet-field" key={key}>
                        <div className="packet-key">{key}</div>
                        <div className="packet-val">{val ?? "—"}</div>
                      </div>
                    ))}
                </li>
              ))}
            </ul>
            {didCapture && (
              <div className="capture-message">
                Network Packets Successfully Captured and Saved to S3:{" "}
                <a
                  href="https://s3.console.aws.amazon.com/s3/home"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open S3 Console
                </a>
              </div>
            )}
          </>
        )}

        {viewMode === "predict" && predictions.length > 0 && (
          <>
            <h2>Prediction Results</h2>

            {predFileKey && (
              <p className="file-key">
                File: <code>{predFileKey}</code>
              </p>
            )}

            {/* Summary */}
            <div className="summary-card">
              Showing <strong>{pageResults.length}</strong> of{" "}
              <strong>{total}</strong> packets (&nbsp;
              <span className="dangerous">{dangerousCount} dangerous</span>)
            </div>

            {/* Table */}
            <table className="results-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {pageResults.map((p, idx) => {
                  const cls = p === 1 ? "dangerous" : "safe";
                  const label = p === 1 ? "🚨 Dangerous!" : "✅ Safe!";
                  return (
                    <tr key={startIndex + idx} className={cls}>
                      <td>Packet: {startIndex + idx + 1}</td>
                      <td>{label}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Pagination controls */}
            <div className="pagination">
              <button
                onClick={() => setCurrentPage((p) => Math.max(p - 1, 0))}
                disabled={currentPage === 0}
              >
                ◀ Prev
              </button>
              <span>
                {" "}
                Page {currentPage + 1} / {pageCount}{" "}
              </span>
              <button
                onClick={() =>
                  setCurrentPage((p) => Math.min(p + 1, pageCount - 1))
                }
                disabled={currentPage >= pageCount - 1}
              >
                Next ▶
              </button>
            </div>
          </>
        )}

        {viewMode === "file" && fileMetrics && (
          <div className="file-results">
            <h2>Capture Analysis</h2>

            {fileFileKey && (
              <p className="file-key">
                File: <code>{fileFileKey}</code>
              </p>
            )}

            <p>
              Total packets: <strong>{fileMetrics.total_packets}</strong>
            </p>
            <p>
              Anomalous:{" "}
              <strong>{fileMetrics.anomalous_packets} packets</strong>
            </p>
            <p>
              Percent Anomalous:{" "}
              <strong>
                ( {(fileMetrics.percent_anomalous * 100).toFixed(1)}% )
              </strong>
            </p>

            <h3>Top Features</h3>
            <ul>
              {fileMetrics.top_features.map((f, i) => (
                <li key={i}>
                  {i + 1}. {f.feature}
                </li>
              ))}
            </ul>
          </div>
        )}

        {viewMode === "malicious" && malPredictions.length > 0 && (
          <>
            <h2>Malicious Predictions</h2>
            {malFileKey && (
              <p className="file-key">
                File: <code>{malFileKey}</code>
              </p>
            )}

            {/* summary banner */}
            <div className="summary-card">
              Showing <strong>{malPageResults.length}</strong> of{" "}
              <strong>{malTotal}</strong> packets
            </div>

            {/* paged table */}
            <table className="results-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {malPageResults.map((p, idx) => (
                  <tr
                    key={malStart + idx}
                    className={p === 1 ? "dangerous" : "safe"}
                  >
                    <td>Packet: {malStart + idx + 1}</td>
                    <td>{p === 1 ? "🚨 Dangerous!" : "✅ Safe!"}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* pagination controls */}
            <div className="pagination">
              <button
                onClick={() => setMalPage((m) => Math.max(m - 1, 0))}
                disabled={malPage === 0}
              >
                ◀ Prev
              </button>
              <span>
                {" "}
                Page {malPage + 1} / {malPageCount}{" "}
              </span>
              <button
                onClick={() =>
                  setMalPage((m) => Math.min(m + 1, malPageCount - 1))
                }
                disabled={malPage >= malPageCount - 1}
              >
                Next ▶
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
