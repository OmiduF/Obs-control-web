import { createContext, useContext, useRef, useState, useCallback, useEffect } from "react";
import OBSWebSocket from "obs-websocket-js";

const MEDIA_KINDS = ["ffmpeg_source", "vlc_source"];
const isTextKind = (k) => typeof k === "string" && k.includes("text");

const ObsCtx = createContext(null);
export const useObs = () => useContext(ObsCtx);

export function ObsProvider({ children }) {
  const obsRef = useRef(null);
  const [status, setStatus] = useState("disconnected");
  const [connError, setConnError] = useState("");
  const [scenes, setScenes] = useState([]);
  const [mediaInputs, setMediaInputs] = useState([]);
  const [textInputs, setTextInputs] = useState([]);
  const [logs, setLogs] = useState([]);
  const subsRef = useRef([]);

  const log = useCallback((msg, type = "info") => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [{ id: Date.now() + Math.random(), time, msg, type }, ...prev].slice(0, 150));
  }, []);
  const clearLogs = useCallback(() => setLogs([]), []);

  const onMediaEnded = useCallback((cb) => {
    subsRef.current.push(cb);
    return () => {
      subsRef.current = subsRef.current.filter((f) => f !== cb);
    };
  }, []);

  const call = useCallback(async (req, data) => {
    if (!obsRef.current) throw new Error("Neconectat");
    return obsRef.current.call(req, data);
  }, []);

  const refreshSources = useCallback(async () => {
    const obs = obsRef.current;
    if (!obs) return;
    try {
      const sl = await obs.call("GetSceneList");
      setScenes((sl.scenes || []).map((s) => s.sceneName));
      const il = await obs.call("GetInputList");
      const inputs = il.inputs || [];
      setMediaInputs(inputs.filter((i) => MEDIA_KINDS.includes(i.inputKind)).map((i) => i.inputName));
      setTextInputs(inputs.filter((i) => isTextKind(i.inputKind)).map((i) => i.inputName));
    } catch (e) {
      log("Nu am putut citi scenele/sursele: " + e.message, "error");
    }
  }, [log]);

  const switchScene = useCallback(
    async (name) => {
      if (!name) return;
      try {
        await obsRef.current.call("SetCurrentProgramScene", { sceneName: name });
        log(`Comutat pe scena "${name}".`, "success");
      } catch (e) {
        log("Eroare la comutare: " + e.message, "error");
      }
    },
    [log]
  );

  const getCurrentScene = useCallback(async () => {
    try {
      const r = await obsRef.current.call("GetCurrentProgramScene");
      return r.currentProgramSceneName || r.sceneName;
    } catch {
      return null;
    }
  }, []);

  const connect = useCallback(
    async (host, port, password) => {
      if (status === "connected") return;
      const obs = new OBSWebSocket();
      obsRef.current = obs;
      setStatus("connecting");
      setConnError("");
      log(`Ma conectez la ws://${host}:${port} ...`);

      obs.on("ConnectionClosed", () => {
        setStatus("disconnected");
        log("Conexiune inchisa.", "error");
      });
      obs.on("MediaInputPlaybackEnded", (data) => {
        log(`Media terminata: "${data.inputName}".`, "event");
        subsRef.current.forEach((cb) => {
          try {
            cb(data.inputName);
          } catch {
            /* ignore subscriber errors */
          }
        });
      });
      obs.on("SceneListChanged", () => refreshSources());
      obs.on("InputCreated", () => refreshSources());
      obs.on("InputRemoved", () => refreshSources());

      try {
        await obs.connect(`ws://${host}:${port}`, password || undefined);
        setStatus("connected");
        log("Conectat la OBS.", "success");
        await refreshSources();
      } catch (e) {
        setStatus("disconnected");
        const m = e && e.message ? e.message : String(e);
        setConnError(m);
        log("Conectare esuata: " + m, "error");
        obsRef.current = null;
      }
    },
    [status, log, refreshSources]
  );

  const disconnect = useCallback(async () => {
    if (obsRef.current) {
      try {
        await obsRef.current.disconnect();
      } catch {
        /* ignore */
      }
    }
    obsRef.current = null;
    setStatus("disconnected");
    log("Deconectat.");
  }, [log]);

  useEffect(
    () => () => {
      if (obsRef.current) obsRef.current.disconnect().catch(() => {});
    },
    []
  );

  const value = {
    status,
    connError,
    scenes,
    mediaInputs,
    textInputs,
    logs,
    log,
    clearLogs,
    connect,
    disconnect,
    refreshSources,
    onMediaEnded,
    switchScene,
    getCurrentScene,
    call,
  };
  return <ObsCtx.Provider value={value}>{children}</ObsCtx.Provider>;
}
