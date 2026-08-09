import { useEffect, useRef, useState, useCallback } from "react";
import "@/App.css";
import OBSWebSocket from "obs-websocket-js";
import {
  Plug,
  PlugZap,
  Radio,
  Play,
  Monitor,
  Film,
  Power,
  Trash2,
  CircleDot,
  Timer,
  ShieldCheck,
} from "lucide-react";

const LS_KEY = "obs_autoswitch_cfg_v1";

const loadCfg = () => {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || {};
  } catch {
    return {};
  }
};

function App() {
  const cfg = loadCfg();
  const obsRef = useRef(null);

  const [host, setHost] = useState(cfg.host || "localhost");
  const [port, setPort] = useState(cfg.port || "4455");
  const [password, setPassword] = useState(cfg.password || "");

  const [status, setStatus] = useState("disconnected"); // disconnected | connecting | connected
  const [connError, setConnError] = useState("");

  const [scenes, setScenes] = useState([]);
  const [mediaInputs, setMediaInputs] = useState([]);

  const [playScene, setPlayScene] = useState(cfg.playScene || "");
  const [mainScene, setMainScene] = useState(cfg.mainScene || "");
  const [mediaSource, setMediaSource] = useState(cfg.mediaSource || "");
  const [onlyWhenPlayActive, setOnlyWhenPlayActive] = useState(
    cfg.onlyWhenPlayActive !== undefined ? cfg.onlyWhenPlayActive : true
  );
  const [delaySec, setDelaySec] = useState(cfg.delaySec || 0);
  const [armed, setArmed] = useState(false);

  const [logs, setLogs] = useState([]);
  const [switchCount, setSwitchCount] = useState(0);

  // refs so the event handler always reads fresh config
  const stateRef = useRef({});
  stateRef.current = {
    playScene,
    mainScene,
    mediaSource,
    onlyWhenPlayActive,
    delaySec,
    armed,
  };

  const addLog = useCallback((msg, type = "info") => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [{ time, msg, type, id: Date.now() + Math.random() }, ...prev].slice(0, 120));
  }, []);

  // persist config
  useEffect(() => {
    localStorage.setItem(
      LS_KEY,
      JSON.stringify({
        host,
        port,
        password,
        playScene,
        mainScene,
        mediaSource,
        onlyWhenPlayActive,
        delaySec,
      })
    );
  }, [host, port, password, playScene, mainScene, mediaSource, onlyWhenPlayActive, delaySec]);

  const refreshSources = useCallback(async () => {
    const obs = obsRef.current;
    if (!obs) return;
    try {
      const sceneList = await obs.call("GetSceneList");
      setScenes((sceneList.scenes || []).map((s) => s.sceneName));
      const inputList = await obs.call("GetInputList");
      const media = (inputList.inputs || []).filter((i) =>
        ["ffmpeg_source", "vlc_source"].includes(i.inputKind)
      );
      setMediaInputs(media.map((i) => i.inputName));
    } catch (e) {
      addLog("Nu am putut citi scenele/sursele: " + e.message, "error");
    }
  }, [addLog]);

  const doSwitch = useCallback(async () => {
    const obs = obsRef.current;
    const { mainScene: main } = stateRef.current;
    if (!obs || !main) return;
    try {
      await obs.call("SetCurrentProgramScene", { sceneName: main });
      setSwitchCount((c) => c + 1);
      addLog(`Am comutat pe scena "${main}".`, "success");
    } catch (e) {
      addLog("Eroare la comutare: " + e.message, "error");
    }
  }, [addLog]);

  const handleMediaEnded = useCallback(
    async (data) => {
      const s = stateRef.current;
      const ended = data.inputName;
      addLog(`Media terminata: "${ended}".`, "event");

      if (!s.armed) return;
      if (s.mediaSource && ended !== s.mediaSource) return;

      if (s.onlyWhenPlayActive) {
        try {
          const cur = await obsRef.current.call("GetCurrentProgramScene");
          const curName = cur.currentProgramSceneName || cur.sceneName;
          if (curName !== s.playScene) {
            addLog(`Scena live este "${curName}", nu "${s.playScene}" -> nu comut.`, "info");
            return;
          }
        } catch {
          /* ignore, continue to switch */
        }
      }

      const delay = Number(s.delaySec) || 0;
      if (delay > 0) {
        addLog(`Astept ${delay}s inainte de comutare...`, "info");
        setTimeout(doSwitch, delay * 1000);
      } else {
        doSwitch();
      }
    },
    [addLog, doSwitch]
  );

  const connect = useCallback(async () => {
    if (status === "connected") return;
    const obs = new OBSWebSocket();
    obsRef.current = obs;
    setStatus("connecting");
    setConnError("");
    addLog(`Ma conectez la ws://${host}:${port} ...`, "info");

    obs.on("ConnectionClosed", () => {
      setStatus("disconnected");
      setArmed(false);
      addLog("Conexiune inchisa.", "error");
    });
    obs.on("MediaInputPlaybackEnded", handleMediaEnded);

    try {
      await obs.connect(`ws://${host}:${port}`, password || undefined);
      setStatus("connected");
      addLog("Conectat la OBS.", "success");
      await refreshSources();
    } catch (e) {
      setStatus("disconnected");
      const msg = e && e.message ? e.message : String(e);
      setConnError(msg);
      addLog("Conectare esuata: " + msg, "error");
      obsRef.current = null;
    }
  }, [host, port, password, status, addLog, handleMediaEnded, refreshSources]);

  const disconnect = useCallback(async () => {
    const obs = obsRef.current;
    setArmed(false);
    if (obs) {
      try {
        await obs.disconnect();
      } catch {
        /* ignore */
      }
    }
    obsRef.current = null;
    setStatus("disconnected");
    addLog("Deconectat.", "info");
  }, [addLog]);

  useEffect(() => {
    return () => {
      if (obsRef.current) obsRef.current.disconnect().catch(() => {});
    };
  }, []);

  const connected = status === "connected";
  const canArm = connected && mainScene && (mediaSource || mediaInputs.length === 0);

  const statusMeta = {
    disconnected: { label: "Deconectat", cls: "st-off" },
    connecting: { label: "Se conecteaza...", cls: "st-wait" },
    connected: { label: "Conectat", cls: "st-on" },
  }[status];

  return (
    <div className="obs-app" data-testid="app-root">
      <div className="grain" />
      <div className="shell">
        <header className="hero">
          <div className="hero-badge">
            <Radio size={16} /> OBS AUTO&nbsp;SWITCH
          </div>
          <h1 className="hero-title">
            Play <span className="arrow">→</span> Main
          </h1>
          <p className="hero-sub">
            Cand materialul media din scena Play se termina, comut automat pe Main.
            Conectare directa la OBS prin WebSocket.
          </p>
        </header>

        <div className="grid">
          {/* CONNECTION */}
          <section className="card" data-testid="connection-card">
            <div className="card-head">
              <Plug size={18} />
              <h2>Conexiune</h2>
              <span className={`status-pill ${statusMeta.cls}`} data-testid="status-pill">
                <CircleDot size={12} /> {statusMeta.label}
              </span>
            </div>

            <div className="field-row">
              <label className="field">
                <span>Host</span>
                <input
                  data-testid="input-host"
                  value={host}
                  disabled={connected}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="localhost"
                />
              </label>
              <label className="field field-sm">
                <span>Port</span>
                <input
                  data-testid="input-port"
                  value={port}
                  disabled={connected}
                  onChange={(e) => setPort(e.target.value)}
                  placeholder="4455"
                />
              </label>
            </div>

            <label className="field">
              <span>Parola WebSocket</span>
              <input
                data-testid="input-password"
                type="password"
                value={password}
                disabled={connected}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="din OBS → Tools → WebSocket Server Settings"
              />
            </label>

            {connError ? (
              <p className="err-text" data-testid="conn-error">
                {connError}
              </p>
            ) : null}

            {!connected ? (
              <button
                className="btn btn-primary"
                data-testid="connect-btn"
                onClick={connect}
                disabled={status === "connecting"}
              >
                <PlugZap size={18} />
                {status === "connecting" ? "Se conecteaza..." : "Conecteaza"}
              </button>
            ) : (
              <button className="btn btn-ghost" data-testid="disconnect-btn" onClick={disconnect}>
                <Power size={18} /> Deconecteaza
              </button>
            )}

            <p className="hint">
              Ai OBS deschis pe acest calculator? Bifeaza „Enable WebSocket server” in OBS.
            </p>
          </section>

          {/* CONFIG */}
          <section className="card" data-testid="config-card">
            <div className="card-head">
              <Monitor size={18} />
              <h2>Reguli de comutare</h2>
            </div>

            <label className="field">
              <span>
                <Play size={13} /> Scena Play (sursa)
              </span>
              <select
                data-testid="select-play-scene"
                value={playScene}
                disabled={!connected}
                onChange={(e) => setPlayScene(e.target.value)}
              >
                <option value="">— alege scena —</option>
                {scenes.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>
                <Monitor size={13} /> Scena Main (destinatie)
              </span>
              <select
                data-testid="select-main-scene"
                value={mainScene}
                disabled={!connected}
                onChange={(e) => setMainScene(e.target.value)}
              >
                <option value="">— alege scena —</option>
                {scenes.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>
                <Film size={13} /> Sursa media (optional)
              </span>
              <select
                data-testid="select-media-source"
                value={mediaSource}
                disabled={!connected}
                onChange={(e) => setMediaSource(e.target.value)}
              >
                <option value="">orice sursa media</option>
                {mediaInputs.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <div className="field-row">
              <label className="field field-sm">
                <span>
                  <Timer size={13} /> Delay (sec)
                </span>
                <input
                  data-testid="input-delay"
                  type="number"
                  min="0"
                  value={delaySec}
                  onChange={(e) => setDelaySec(e.target.value)}
                />
              </label>
              <label className="toggle" data-testid="toggle-only-active">
                <input
                  type="checkbox"
                  checked={onlyWhenPlayActive}
                  onChange={(e) => setOnlyWhenPlayActive(e.target.checked)}
                />
                <span className="track">
                  <span className="thumb" />
                </span>
                <span className="toggle-label">Doar cand Play e live</span>
              </label>
            </div>

            <button
              className={`btn ${armed ? "btn-armed" : "btn-arm"}`}
              data-testid="arm-btn"
              disabled={!canArm}
              onClick={() => {
                const next = !armed;
                setArmed(next);
                addLog(next ? "Automatizare PORNITA." : "Automatizare oprita.", next ? "success" : "info");
              }}
            >
              {armed ? <ShieldCheck size={18} /> : <Power size={18} />}
              {armed ? "Activa — asculta finalul media" : "Porneste automatizarea"}
            </button>
          </section>

          {/* LOG */}
          <section className="card card-wide" data-testid="log-card">
            <div className="card-head">
              <Radio size={18} />
              <h2>Activitate</h2>
              <span className="counter" data-testid="switch-count">
                {switchCount} comutari
              </span>
              <button className="icon-btn" data-testid="clear-log-btn" onClick={() => setLogs([])} title="Sterge log">
                <Trash2 size={15} />
              </button>
            </div>
            <div className="log" data-testid="log-list">
              {logs.length === 0 ? (
                <p className="log-empty">Niciun eveniment inca. Conecteaza-te si porneste automatizarea.</p>
              ) : (
                logs.map((l) => (
                  <div key={l.id} className={`log-row lr-${l.type}`}>
                    <span className="log-time">{l.time}</span>
                    <span className="log-msg">{l.msg}</span>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        <footer className="foot">OBS WebSocket • ruleaza in browser • datele raman pe acest calculator</footer>
      </div>
    </div>
  );
}

export default App;
