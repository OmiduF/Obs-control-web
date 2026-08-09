import { useState } from "react";
import "@/App.css";
import { ObsProvider } from "@/obs/ObsProvider";
import ConnectionBar from "@/components/ConnectionBar";
import AutoSwitchTab from "@/components/AutoSwitchTab";
import TimerTab from "@/components/TimerTab";
import MaterialsTab from "@/components/MaterialsTab";
import LogPanel from "@/components/LogPanel";
import { Repeat, Timer as TimerIcon, Layers, Radio } from "lucide-react";

const TABS = [
  { id: "switch", label: "Auto Switch", icon: Repeat },
  { id: "timer", label: "Timer", icon: TimerIcon },
  { id: "materials", label: "Materiale", icon: Layers },
];

function App() {
  const [tab, setTab] = useState("switch");

  return (
    <ObsProvider>
      <div className="obs-app" data-testid="app-root">
        <div className="grain" />
        <div className="shell">
          <header className="hero">
            <div className="hero-badge">
              <Radio size={16} /> OBS CONTROL DECK
            </div>
            <h1 className="hero-title">Stream Automations</h1>
            <p className="hero-sub">
              Auto switch, timer si materiale — conectare directa la OBS prin WebSocket, dintr-un
              singur panou.
            </p>
          </header>

          <ConnectionBar />

          <nav className="tabs" data-testid="tabs-nav">
            {TABS.map((t) => {
              const Icon = t.icon;
              return (
                <button
                  key={t.id}
                  className={`tab-btn ${tab === t.id ? "active" : ""}`}
                  data-testid={`tab-${t.id}`}
                  onClick={() => setTab(t.id)}
                >
                  <Icon size={16} /> {t.label}
                </button>
              );
            })}
          </nav>

          <section className="card tab-panel" data-testid="tab-panel">
            {tab === "switch" && <AutoSwitchTab />}
            {tab === "timer" && <TimerTab />}
            {tab === "materials" && <MaterialsTab />}
          </section>

          <LogPanel />

          <footer className="foot">OBS WebSocket • ruleaza in browser • datele raman pe acest calculator</footer>
        </div>
      </div>
    </ObsProvider>
  );
}

export default App;
