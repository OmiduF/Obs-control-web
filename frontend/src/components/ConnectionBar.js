import { useEffect, useState } from "react";
import { useObs } from "@/obs/ObsProvider";
import { Plug, PlugZap, Power, CircleDot, RefreshCw } from "lucide-react";

const LS_KEY = "obs_conn_v1";
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || {};
  } catch {
    return {};
  }
};

export default function ConnectionBar() {
  const { status, connError, connect, disconnect, refreshSources } = useObs();
  const cfg = load();
  const [host, setHost] = useState(cfg.host || "localhost");
  const [port, setPort] = useState(cfg.port || "4455");
  const [password, setPassword] = useState(cfg.password || "");

  useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify({ host, port, password }));
  }, [host, port, password]);

  const connected = status === "connected";
  const meta = {
    disconnected: { label: "Deconectat", cls: "st-off" },
    connecting: { label: "Se conecteaza...", cls: "st-wait" },
    connected: { label: "Conectat", cls: "st-on" },
  }[status];

  return (
    <section className="conn-bar" data-testid="connection-card">
      <div className="conn-left">
        <Plug size={18} className="conn-ico" />
        <div className="conn-fields">
          <input
            data-testid="input-host"
            className="conn-input"
            value={host}
            disabled={connected}
            onChange={(e) => setHost(e.target.value)}
            placeholder="localhost sau IP (ex. 192.168.1.20)"
          />
          <input
            data-testid="input-port"
            className="conn-input conn-port"
            value={port}
            disabled={connected}
            onChange={(e) => setPort(e.target.value)}
            placeholder="4455"
          />
          <input
            data-testid="input-password"
            className="conn-input"
            type="password"
            value={password}
            disabled={connected}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="parola WebSocket"
          />
        </div>
      </div>

      <div className="conn-right">
        <span className={`status-pill ${meta.cls}`} data-testid="status-pill">
          <CircleDot size={12} /> {meta.label}
        </span>
        {connected ? (
          <>
            <button className="icon-btn" data-testid="refresh-btn" title="Reincarca scenele" onClick={refreshSources}>
              <RefreshCw size={16} />
            </button>
            <button className="btn-mini btn-ghost" data-testid="disconnect-btn" onClick={disconnect}>
              <Power size={16} /> Deconecteaza
            </button>
          </>
        ) : (
          <button
            className="btn-mini btn-primary"
            data-testid="connect-btn"
            disabled={status === "connecting"}
            onClick={() => connect(host, port, password)}
          >
            <PlugZap size={16} />
            {status === "connecting" ? "..." : "Conecteaza"}
          </button>
        )}
      </div>

      {connError ? (
        <p className="err-text conn-err" data-testid="conn-error">
          {connError}
        </p>
      ) : null}
    </section>
  );
}
