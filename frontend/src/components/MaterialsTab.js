import { useEffect, useRef, useState } from "react";
import { useObs } from "@/obs/ObsProvider";
import { Play, Power, ShieldCheck, Film, Monitor, Layers } from "lucide-react";

const LS_KEY = "obs_materials_v1";
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || {};
  } catch {
    return {};
  }
};

export default function MaterialsTab() {
  const { status, scenes, mediaInputs, switchScene, getCurrentScene, onMediaEnded, call, log } = useObs();
  const connected = status === "connected";
  const cfg = load();

  const [matScene, setMatScene] = useState(cfg.matScene || "");
  const [mediaSource, setMediaSource] = useState(cfg.mediaSource || "");
  const [mainScene, setMainScene] = useState(cfg.mainScene || "");
  const [onlyWhenMatLive, setOnlyWhenMatLive] = useState(cfg.onlyWhenMatLive !== undefined ? cfg.onlyWhenMatLive : true);
  const [armed, setArmed] = useState(false);

  const ref = useRef({});
  ref.current = { matScene, mediaSource, mainScene, onlyWhenMatLive, armed };

  useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify({ matScene, mediaSource, mainScene, onlyWhenMatLive }));
  }, [matScene, mediaSource, mainScene, onlyWhenMatLive]);

  useEffect(() => {
    const unsub = onMediaEnded(async (ended) => {
      const s = ref.current;
      if (!s.armed) return;
      if (s.mediaSource && ended !== s.mediaSource) return;
      if (s.onlyWhenMatLive && s.matScene) {
        const cur = await getCurrentScene();
        if (cur !== s.matScene) {
          log(`[Materiale] Scena live e "${cur}", nu "${s.matScene}" -> nu comut.`, "info");
          return;
        }
      }
      log(`[Materiale] "${ended}" terminat -> comut pe "${s.mainScene}".`, "event");
      switchScene(s.mainScene);
    });
    return unsub;
  }, [onMediaEnded, switchScene, getCurrentScene, log]);

  const startMaterial = async () => {
    if (matScene) await switchScene(matScene);
    if (mediaSource) {
      try {
        await call("TriggerMediaInputAction", {
          inputName: mediaSource,
          mediaAction: "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART",
        });
        log(`[Materiale] Pornesc materialul "${mediaSource}".`, "info");
      } catch (e) {
        log("Nu am putut porni materialul: " + e.message, "error");
      }
    }
  };

  const canArm = connected && mainScene;

  return (
    <div data-testid="materials-tab">
      <p className="tab-desc">
        Cand materialul din scena <b>MATERIALE</b> se termina, trec pe <b>MAIN</b>. Butonul de start
        comuta pe scena materiale si reporneste materialul de la inceput.
      </p>

      <div className="grid2">
        <label className="mini-field">
          <span>
            <Layers size={12} /> Scena MATERIALE
          </span>
          <select
            data-testid="mat-scene"
            value={matScene}
            disabled={!connected}
            onChange={(e) => setMatScene(e.target.value)}
          >
            <option value="">— alege scena —</option>
            {scenes.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="mini-field">
          <span>
            <Monitor size={12} /> Scena MAIN
          </span>
          <select
            data-testid="mat-main-scene"
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
        <label className="mini-field">
          <span>
            <Film size={12} /> Sursa media (optional)
          </span>
          <select
            data-testid="mat-media-source"
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
        <label className="toggle mat-toggle" data-testid="mat-only-live">
          <input type="checkbox" checked={onlyWhenMatLive} onChange={(e) => setOnlyWhenMatLive(e.target.checked)} />
          <span className="track">
            <span className="thumb" />
          </span>
          <span className="toggle-label">Doar cand MATERIALE e live</span>
        </label>
      </div>

      <div className="tab-actions">
        <button className="btn-mini btn-primary" data-testid="mat-start-btn" disabled={!connected || !matScene} onClick={startMaterial}>
          <Play size={16} /> Start material
        </button>
        <button
          className={`btn ${armed ? "btn-armed" : "btn-arm"}`}
          data-testid="materials-arm-btn"
          disabled={!canArm}
          onClick={() => {
            const next = !armed;
            setArmed(next);
            log(next ? "[Materiale] PORNIT." : "[Materiale] oprit.", next ? "success" : "info");
          }}
        >
          {armed ? <ShieldCheck size={18} /> : <Power size={18} />}
          {armed ? "Activ — ascult finalul materialului" : "Porneste automatizarea"}
        </button>
      </div>
    </div>
  );
}
