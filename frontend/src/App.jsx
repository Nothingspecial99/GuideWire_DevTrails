import React, { useEffect, useRef, useState } from "react";
import { api } from "./api";

const defaultWorker = {
  name: "",
  phone: "",
  city: "Pune",
  zone: "pune-central",
  payout_handle: "",
  device_attested: true,
};

export default function App() {
  const [workerForm, setWorkerForm] = useState(defaultWorker);
  const [workers, setWorkers] = useState([]);
  const [activeWorkerId, setActiveWorkerId] = useState("");
  const [quote, setQuote] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState("standard");
  const [workerDash, setWorkerDash] = useState(null);
  const [adminDash, setAdminDash] = useState(null);
  const [eventZone, setEventZone] = useState("pune-central");
  const [eventType, setEventType] = useState("heavy_rain");
  const [eventResult, setEventResult] = useState(null);
  const [error, setError] = useState("");
  const [successToast, setSuccessToast] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const toastTimeoutRef = useRef(null);

  useEffect(() => {
    bootstrap();
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const activeWorker = workers.find((worker) => worker.id === activeWorkerId) || null;

  function showSuccess(message) {
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    setSuccessToast(message);
    toastTimeoutRef.current = setTimeout(() => setSuccessToast(""), 1400);
  }

  async function runAction(actionKey, action, successMessage) {
    setBusyAction(actionKey);
    setError("");
    try {
      await action();
      showSuccess(successMessage);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyAction("");
    }
  }

  async function bootstrap() {
    try {
      const list = await api.listWorkers();
      setWorkers(list);
      await refreshAdmin();
      if (list.length) {
        await switchWorker(list[0].id, list);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshAdmin() {
    const data = await api.adminDashboard();
    setAdminDash(data);
  }

  async function refreshWorkers() {
    const list = await api.listWorkers();
    setWorkers(list);
    return list;
  }

  async function switchWorker(workerId, existingList = null) {
    const list = existingList || workers;
    setActiveWorkerId(workerId);
    const q = await api.quote(workerId);
    setQuote(q);
    setSelectedPlan(q.recommended_plan);
    const dash = await api.workerDashboard(workerId);
    setWorkerDash(dash);
    const selected = list.find((worker) => worker.id === workerId);
    if (selected) {
      setEventZone(selected.zone);
    }
  }

  async function registerWorker(e) {
    e.preventDefault();
    await runAction("register", async () => {
      const worker = await api.register(workerForm);
      setWorkerForm(defaultWorker);
      const list = await refreshWorkers();
      await switchWorker(worker.id, list);
      await refreshAdmin();
    }, "Worker registered successfully");
  }

  async function useSeed() {
    await runAction("seed", async () => {
      const seeded = await api.seed();
      const list = await refreshWorkers();
      const target = seeded.worker_id || list[0]?.id;
      if (target) {
        await switchWorker(target, list);
      }
      await refreshAdmin();
    }, "Demo worker loaded");
  }

  async function buyPolicy() {
    if (!activeWorkerId) return;
    await runAction("buy", async () => {
      await api.buyPolicy({ worker_id: activeWorkerId, plan: selectedPlan });
      await switchWorker(activeWorkerId);
      await refreshAdmin();
    }, "Weekly policy activated");
  }

  async function triggerEvent() {
    const payload = {
      zone: eventZone,
      event_type: eventType,
      rain_mm_3h: eventType === "heavy_rain" ? 48 : null,
      temp_c_4h: eventType === "extreme_heat" ? 44 : null,
      aqi_6h: eventType === "air_pollution" ? 380 : null,
      flood_alert_active: eventType === "flood_alert",
      civic_restriction_active: eventType === "curfew_or_strike",
    };

    await runAction("trigger", async () => {
      const res = await api.trigger(payload);
      setEventResult(res);
      if (activeWorkerId) {
        const dash = await api.workerDashboard(activeWorkerId);
        setWorkerDash(dash);
      }
      await refreshAdmin();
    }, "Event processed");
  }

  return (
    <div className="page">
      <div className="geo geo-a" />
      <div className="geo geo-b" />

      <main className="container">
        <header className="hero card">
          <div>
            <p className="eyebrow">ONE-WEEK INCOME PROTECTION</p>
            <h1>GigSwift Control Center</h1>
            <p className="subtitle">
              Onboard delivery partners, switch active worker profiles, activate weekly plans,
              trigger disruption events, and monitor payouts from one continuous command page.
            </p>
          </div>
          {adminDash ? (
            <div className="chips">
              <span className="chip">Workers {adminDash.workers}</span>
              <span className="chip">Policies {adminDash.active_policies}</span>
              <span className="chip">Claims {adminDash.total_claims}</span>
              <span className="chip">Loss ratio {adminDash.loss_ratio}</span>
            </div>
          ) : null}
        </header>

        {error ? <p className="error">{error}</p> : null}
        {successToast ? <div className="success-toast">✓ {successToast}</div> : null}

        <section className="card">
          <h2>1. Worker Onboarding & Active Profile Switch</h2>
          <div className="split">
            <div>
              <h3>Add New Worker</h3>
              <form onSubmit={registerWorker} className="grid">
                <input placeholder="Name" value={workerForm.name} onChange={(e) => setWorkerForm({ ...workerForm, name: e.target.value })} required />
                <input placeholder="Phone" value={workerForm.phone} onChange={(e) => setWorkerForm({ ...workerForm, phone: e.target.value })} required />
                <input placeholder="Payout Handle (UPI)" value={workerForm.payout_handle} onChange={(e) => setWorkerForm({ ...workerForm, payout_handle: e.target.value })} required />
                <select value={workerForm.city} onChange={(e) => setWorkerForm({ ...workerForm, city: e.target.value })}>
                  <option>Pune</option>
                  <option>Mumbai</option>
                  <option>Delhi</option>
                  <option>Bangalore</option>
                </select>
                <select value={workerForm.zone} onChange={(e) => setWorkerForm({ ...workerForm, zone: e.target.value })}>
                  <option value="pune-central">pune-central</option>
                  <option value="mumbai-west">mumbai-west</option>
                  <option value="delhi-ncr">delhi-ncr</option>
                  <option value="bangalore-east">bangalore-east</option>
                </select>
                <label className="check">
                  <input
                    type="checkbox"
                    checked={workerForm.device_attested}
                    onChange={(e) => setWorkerForm({ ...workerForm, device_attested: e.target.checked })}
                  />
                  Device integrity attested
                </label>
                <button type="submit" disabled={!!busyAction}>{busyAction === "register" ? "Registering..." : "Register Worker"}</button>
                <button type="button" onClick={useSeed} disabled={!!busyAction}>{busyAction === "seed" ? "Loading..." : "Load Demo Worker"}</button>
              </form>
            </div>

            <div>
              <h3>Registered Workers</h3>
              {workers.length ? (
                <div className="worker-list">
                  {workers.map((worker) => (
                    <div key={worker.id} className={`worker-item ${activeWorkerId === worker.id ? "active" : ""}`}>
                      <div>
                        <b>{worker.name}</b>
                        <p>{worker.city} • {worker.zone}</p>
                        <p>{worker.phone} • {worker.payout_handle}</p>
                      </div>
                      <button
                        type="button"
                        className="secondary"
                        onClick={() => runAction("switch", () => switchWorker(worker.id), `Switched to ${worker.name}`)}
                        disabled={!!busyAction}
                      >
                        {activeWorkerId === worker.id ? "Active" : "Switch"}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No workers yet. Add one or load demo worker.</p>
              )}
            </div>
          </div>
        </section>

        <section className="card">
          <h2>2. AI Weekly Pricing & Policy Activation</h2>
          {quote && activeWorker ? (
            <div>
              <p>
                Selected worker <b>{activeWorker.name}</b> ({activeWorker.id}) • Zone <b>{activeWorker.zone}</b>
              </p>
              <p>Risk score <b>{quote.risk_score}</b> • Recommended plan <b>{quote.recommended_plan}</b></p>
              <div className="plans">
                {Object.entries(quote.plans).map(([plan, info]) => (
                  <label key={plan} className={`plan ${selectedPlan === plan ? "plan-selected" : ""}`}>
                    <input type="radio" name="plan" value={plan} checked={selectedPlan === plan} onChange={(e) => setSelectedPlan(e.target.value)} />
                    <span>{plan.toUpperCase()}</span>
                    <small>₹{info.weekly_premium}/week • max payout ₹{info.max_payout}</small>
                  </label>
                ))}
              </div>
              <button onClick={buyPolicy} disabled={!activeWorkerId || !!busyAction}>{busyAction === "buy" ? "Activating..." : "Activate Weekly Policy"}</button>
            </div>
          ) : (
            <p>Select a worker to generate AI-based quote and activate policy.</p>
          )}
        </section>

        <section className="card">
          <h2>3. Parametric Trigger Simulation</h2>
          <div className="grid">
            <select value={eventZone} onChange={(e) => setEventZone(e.target.value)}>
              <option value="pune-central">pune-central</option>
              <option value="mumbai-west">mumbai-west</option>
              <option value="delhi-ncr">delhi-ncr</option>
              <option value="bangalore-east">bangalore-east</option>
            </select>
            <select value={eventType} onChange={(e) => setEventType(e.target.value)}>
              <option value="heavy_rain">heavy_rain</option>
              <option value="extreme_heat">extreme_heat</option>
              <option value="flood_alert">flood_alert</option>
              <option value="air_pollution">air_pollution</option>
              <option value="curfew_or_strike">curfew_or_strike</option>
            </select>
            <button onClick={triggerEvent} disabled={!!busyAction}>{busyAction === "trigger" ? "Triggering..." : "Trigger Event"}</button>
          </div>
          {activeWorker ? <p>Tip: choose zone <b>{activeWorker.zone}</b> to impact the active worker instantly.</p> : null}
          {eventResult ? (
            <p>
              Triggered {String(eventResult.event.triggered)} • Claims {eventResult.claims_processed} •
              Approved {eventResult.approved ?? 0} • Review {eventResult.review ?? 0} • Blocked {eventResult.blocked ?? 0}
            </p>
          ) : null}
        </section>

        <section className="split">
          <div className="card">
            <h2>4. Worker Dashboard</h2>
            {workerDash && activeWorker ? (
              <div>
                <p>Worker <b>{activeWorker.name}</b> ({activeWorker.id})</p>
                <p>Active coverage <b>{String(workerDash.metrics.active_coverage)}</b></p>
                <p>Earnings protected <b>₹{workerDash.metrics.earnings_protected}</b></p>
                <p>Total claims <b>{workerDash.metrics.claims_count}</b></p>
                <ul>
                  {workerDash.claims.slice().reverse().map((claim) => (
                    <li key={claim.id}>{claim.event_type} • {claim.status} • ₹{claim.payout_amount}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <p>Select a worker to view dashboard.</p>
            )}
          </div>

          <div className="card">
            <h2>5. Admin Analytics</h2>
            {adminDash ? (
              <div>
                <p>Workers {adminDash.workers} • Active policies {adminDash.active_policies}</p>
                <p>Premiums ₹{adminDash.total_premiums_collected} • Payouts ₹{adminDash.total_payouts}</p>
                <p>Claims: Approved {adminDash.claims_by_status.approved}, Review {adminDash.claims_by_status.review}, Blocked {adminDash.claims_by_status.blocked}</p>
              </div>
            ) : (
              <p>Loading admin metrics...</p>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
