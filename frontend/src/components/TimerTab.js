import { useEffect, useRef, useState } from "react";
import { useObs } from "@/obs/ObsProvider";
import { Play, Square, RotateCcw, Clapperboard, Monitor, Type, Film } from "lucide-react";

const LS_KEY = "obs_timer_v1";
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || {};
  } catch {
    return {};
  }
};
const fmt = (s) => {
  s = Math.max(0, s);
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
};

export default function TimerTab() {
  const { status, scenes, mediaInputs, textInputs, switchScene, onMediaEnded, call, log } = useObs();
  const connected = status === "connected";
  const cfg = load();

  const [min, setMin] = useState(cfg.min ?? 5);
  const [sec, setSec] = useState(cfg.sec ?? 0);
  const [introScene, setIntroScene] = useState(cfg.introScene || "");
  const [mainScene, setMainScene] = useState(cfg.mainScene || "");
  const [introMedia, setIntroMedia] = useState(cfg.introMedia || "");
  const [textSource, setTextSource] = useState(cfg.textSource || "");

  const [remaining, setRemaining] = useState(0);
  const [running, setRunning] = useState(false);

  const intervalRef = useRef(null);
  const waitingRef = useRef(false);
  const cfgRef = useRef({});
  cfgRef.current = { introScene, mainScene, introMedia, textSource };

  useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify({ min, sec, introScene, mainScene, introMedia, textSource }));
  }, [min, sec, introScene, mainScene, introMedia, textSource]);

  // when intro media ends -> go to MAIN
  useEffect(() => {
    const unsub = onMediaEnded((ended) => {
      if (!waitingRef.current) return;
      const { introMedia: im, mainScene: ms } = cfgRef.current;
      if (im && ended !== im) return;
      waitingRef.current = false;
      log("[Timer] Intro terminat -> comut pe Main.", "event");
      switchScene(ms);
    });
    return unsub;
  }, [onMediaEnded, switchScene, log]);

  const pushText = async (t) => {
    const { textSource: ts } = cfgRef.current;
    if (!ts) return;
    try {
      await call("SetInputSettings", { inputName: ts, inputSettings: { text: t } });
    } catch {
      /* ignore */
    }
  };

  const stop = () => {
    clearInterval(intervalRef.current);
    intervalRef.current = null;
    setRunning(false);
    waitingRef.current = false;
  };

  const reset = () => {
    stop();
    setRemaining(0);
  };

  const start = () => {
    const total = Number(min) * 60 + Number(sec);
    if (total <= 0) return;
    clearInterval(intervalRef.current);
    setRemaining(total);
    setRunning(true);
    waitingRef.current = false;
    pushText(fmt(total));
    log(`[Timer] Pornit ${fmt(total)}.`, "info");

    intervalRef.current = setInterval(() => {
      setRemaining((prev) => {
        const next = prev - 1;
        pushText(fmt(Math.max(next, 0)));
        if (next <= 0) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          setRunning(false);
          const { introScene: is } = cfgRef.current;
          log("[Timer] Gata -> comut pe INTRO.", "event");
          switchScene(is);
          waitingRef.current = true;
          return 0;
        }
        return next;
      });
    }, 1000);
  };

  useEffect(() => () => clearInterval(intervalRef.current), []);

  const display = running || remaining > 0 ? remaining : Number(min) * 60 + Number(sec);
  const canStart = connected && introScene && mainScene && Number(min) * 60 + Number(sec) > 0;

  return (
    <div data-testid="timer-tab">
      <p className="tab-desc">
        Numaratoare inversa. La final comut pe <b>INTRO</b>; cand se termina materialul din INTRO,
        trec pe <b>MAIN</b>.
      </p>

      <div className="timer-display" data-testid="timer-display">
        {fmt(display)}
      </div>

      <div className="timer-inputs">
        <label className="mini-field">
          <span>Minute</span>
          <input
            data-testid="timer-min"
            type="number"
            min="0"
            value={min}
            disabled={running}
            onChange={(e) => setMin(e.target.value)}
          />
        </label>
        <label className="mini-field">
          <span>Secunde</span>
          <input
            data-testid="timer-sec"
            type="number"
            min="0"
            max="59"
            value={sec}
            disabled={running}
            onChange={(e) => setSec(e.target.value)}
          />
        </label>
      </div>

      <div className="grid2">
        <label className="mini-field">
          <span>
            <Clapperboard size={12} /> Scena INTRO
          </span>
          <select
            data-testid="timer-intro-scene"
            value={introScene}
            disabled={!connected}
            onChange={(e) => setIntroScene(e.target.value)}
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
            data-testid="timer-main-scene"
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
            <Film size={12} /> Media din INTRO (optional)
          </span>
          <select
            data-testid="timer-intro-media"
            value={introMedia}
            disabled={!connected}
            onChange={(e) => setIntroMedia(e.target.value)}
          >
            <option value="">orice media</option>
            {mediaInputs.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="mini-field">
          <span>
            <Type size={12} /> Text OBS pt. countdown (optional)
          </span>
          <select
            data-testid="timer-text-source"
            value={textSource}
            disabled={!connected}
            onChange={(e) => setTextSource(e.target.value)}
          >
            <option value="">nu afisa in OBS</option>
            {textInputs.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="tab-actions">
        {!running ? (
          <button className="btn btn-primary" data-testid="timer-start-btn" disabled={!canStart} onClick={start}>
            <Play size={18} /> Start countdown
          </button>
        ) : (
          <button className="btn btn-ghost" data-testid="timer-stop-btn" onClick={stop}>
            <Square size={18} /> Stop
          </button>
        )}
        <button className="btn-mini btn-arm" data-testid="timer-reset-btn" onClick={reset}>
          <RotateCcw size={16} /> Reset
        </button>
      </div>
    </div>
  );
}
