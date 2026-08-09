import { useObs } from "@/obs/ObsProvider";
import { Radio, Trash2 } from "lucide-react";

export default function LogPanel() {
  const { logs, clearLogs } = useObs();
  return (
    <section className="card card-wide log-card" data-testid="log-card">
      <div className="card-head">
        <Radio size={18} />
        <h2>Activitate</h2>
        <button className="icon-btn" data-testid="clear-log-btn" onClick={clearLogs} title="Sterge log">
          <Trash2 size={15} />
        </button>
      </div>
      <div className="log" data-testid="log-list">
        {logs.length === 0 ? (
          <p className="log-empty">Niciun eveniment inca. Conecteaza-te si porneste o automatizare.</p>
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
  );
}
