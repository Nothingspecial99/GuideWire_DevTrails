const API_BASE = "";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path.startsWith('/') ? path : '/' + path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  seed: () => request("/seed"),
  listWorkers: () => request("/workers"),
  register: (payload) => request("/workers/register", { method: "POST", body: JSON.stringify(payload) }),
  quote: (workerId) => request(`/risk/quote/${workerId}`),
  buyPolicy: (payload) => request("/policies/purchase", { method: "POST", body: JSON.stringify(payload) }),
  trigger: (payload) => request("/events/trigger", { method: "POST", body: JSON.stringify(payload) }),
  workerDashboard: (workerId) => request(`/workers/${workerId}/dashboard`),
  adminDashboard: () => request("/admin/dashboard"),
};
