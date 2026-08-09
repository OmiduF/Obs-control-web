import { useEffect, useRef, useState } from "react";
import { useObs } from "@/obs/ObsProvider";
import { Plus, Trash2, ArrowRight, Power, ShieldCheck, Film, Monitor } from "lucide-react";

const LS_KEY = "obs_autoswitch_rules_v1";
const load = () => {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY)) || null;
  } catch {
    return null;
  }
};

export default function AutoSwitchTab() {
  const { status, scenes, mediaInputs, switchScene, onMediaEnded, log } = useObs();
  const connected = status === "connected";

  const [rules, setRules] = useState(
    load() || [{ id: Date.now(), source: "", target: "" }]
  );
  const [armed, setArmed] = useState(false);

  const ref = useRef({});
  ref.current = { rules, armed };

  useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify(rules));
  }, [rules]);

  useEffect(() => {
    const unsub = onMediaEnded((ended) => {
      const { rules: rs, armed: a } = ref.current;
      if (!a) return;
      const rule = rs.find((r) => r.target && (!r.source || r.source === ended));
      if (rule) {
        log(`[Auto Switch] "${ended}" terminat -> "${rule.target}".`, "event");
        switchScene(rule.target);
      }
    });
    return unsub;
  }, [onMediaEnded, switchScene, log]);

  const addRule = () => setRules((r) => [...r, { id: Date.now() + Math.random(), source: "", target: "" }]);
  const removeRule = (id) => setRules((r) => r.filter((x) => x.id !== id));
  const update = (id, key, val) =>
    setRules((r) => r.map((x) => (x.id === id ? { ...x, [key]: val } : x)));

  const canArm = connected && rules.some((r) => r.target);

  return (
    <div data-testid="autoswitch-tab">
      <p className="tab-desc">
        Cand o sursa media se termina, comut pe scena aleasa. Poti adauga mai multe reguli
        (ex. <b>Play → Main</b>).
      </p>

      <div className="rules">
        {rules.map((r, i) => (
          <div className="rule" key={r.id} data-testid={`rule-${i}`}>
            <label className="mini-field">
              <span>
                <Film size={12} /> Sursa media
              </span>
              <select
                data-testid={`rule-source-${i}`}
                value={r.source}
                disabled={!connected}
                onChange={(e) => update(r.id, "source", e.target.value)}
              >
                <option value="">orice sursa media</option>
                {mediaInputs.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <ArrowRight size={18} className="rule-arrow" />

            <label className="mini-field">
              <span>
                <Monitor size={12} /> Scena destinatie
              </span>
              <select
                data-testid={`rule-target-${i}`}
                value={r.target}
                disabled={!connected}
                onChange={(e) => update(r.id, "target", e.target.value)}
              >
                <option value="">— alege scena —</option>
                {scenes.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>

            <button
              className="icon-btn del"
              data-testid={`rule-remove-${i}`}
              onClick={() => removeRule(r.id)}
              disabled={rules.length === 1}
              title="Sterge regula"
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}
      </div>

      <div className="tab-actions">
        <button className="btn-mini btn-arm" data-testid="add-rule-btn" onClick={addRule} disabled={!connected}>
          <Plus size={16} /> Adauga regula
        </button>
        <button
          className={`btn ${armed ? "btn-armed" : "btn-arm"}`}
          data-testid="autoswitch-arm-btn"
          disabled={!canArm}
          onClick={() => {
            const next = !armed;
            setArmed(next);
            log(next ? "[Auto Switch] PORNIT." : "[Auto Switch] oprit.", next ? "success" : "info");
          }}
        >
          {armed ? <ShieldCheck size={18} /> : <Power size={18} />}
          {armed ? "Activ — ascult finalul media" : "Porneste automatizarea"}
        </button>
      </div>
    </div>
  );
}
