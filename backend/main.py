from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models import (
    Claim,
    ClaimStatus,
    LocationPing,
    Policy,
    PolicyPurchaseRequest,
    Payout,
    TriggerEvent,
    TriggerEventRequest,
    Worker,
    WorkerCreate,
)
from app.services import (
    PLAN_MAX_PAYOUT,
    event_triggered,
    fraud_check,
    haversine_km,
    payout_factor,
    premium_for,
    risk_score,
)
from app.store import store

app = FastAPI(title="GigSwift API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/workers/register", response_model=Worker)
def register_worker(payload: WorkerCreate) -> Worker:
    worker = Worker(
        id=store.new_worker_id(),
        name=payload.name,
        phone=payload.phone,
        city=payload.city,
        zone=payload.zone,
        payout_handle=payload.payout_handle,
        device_attested=payload.device_attested,
        created_at=store.now(),
    )
    store.workers[worker.id] = worker
    store.locations[worker.id] = []
    return worker


@app.get("/workers", response_model=list[Worker])
def list_workers() -> list[Worker]:
    return list(store.workers.values())


@app.post("/workers/location")
def push_location(payload: LocationPing) -> dict:
    worker = store.workers.get(payload.worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    store.locations[payload.worker_id].append(payload)
    return {"status": "recorded"}


@app.get("/risk/quote/{worker_id}")
def quote(worker_id: str) -> dict:
    worker = store.workers.get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    score = risk_score(worker.zone)
    plans = {
        "basic": {"weekly_premium": premium_for(worker.zone, "basic"), "max_payout": PLAN_MAX_PAYOUT["basic"]},
        "standard": {"weekly_premium": premium_for(worker.zone, "standard"), "max_payout": PLAN_MAX_PAYOUT["standard"]},
        "pro": {"weekly_premium": premium_for(worker.zone, "pro"), "max_payout": PLAN_MAX_PAYOUT["pro"]},
    }
    recommendation = "basic" if score < 40 else "standard" if score < 70 else "pro"
    return {"worker_id": worker_id, "risk_score": score, "recommended_plan": recommendation, "plans": plans}


@app.post("/policies/purchase", response_model=Policy)
def purchase_policy(payload: PolicyPurchaseRequest) -> Policy:
    worker = store.workers.get(payload.worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    for p in store.policies.values():
        if p.worker_id == worker.id and p.active:
            p.active = False

    policy = Policy(
        id=store.new_policy_id(),
        worker_id=worker.id,
        plan=payload.plan,
        zone=worker.zone,
        weekly_premium=premium_for(worker.zone, payload.plan),
        max_payout=PLAN_MAX_PAYOUT[payload.plan],
        active=True,
        created_at=store.now(),
    )
    store.policies[policy.id] = policy
    return policy


@app.post("/events/trigger")
def trigger_event(payload: TriggerEventRequest) -> dict:
    is_triggered = event_triggered(payload)
    event = TriggerEvent(
        id=store.new_event_id(),
        zone=payload.zone,
        event_type=payload.event_type,
        triggered=is_triggered,
        created_at=store.now(),
    )
    store.events[event.id] = event
    store.zone_event_counter[payload.zone] = store.zone_event_counter.get(payload.zone, 0) + 1

    if not is_triggered:
        return {"event": event, "claims_processed": 0, "message": "Threshold not met"}

    claims_processed = 0
    approved = 0
    reviewed = 0
    blocked = 0

    for policy in store.policies.values():
        if not policy.active or policy.zone != payload.zone:
            continue

        worker = store.workers.get(policy.worker_id)
        if not worker:
            continue

        duplicate_exists = any(
            c.worker_id == worker.id and c.event_id == event.id for c in store.claims.values()
        )
        speed_kmph = None
        pings = store.locations.get(worker.id, [])
        if len(pings) >= 2:
            last, current = pings[-2], pings[-1]
            distance = haversine_km(last.latitude, last.longitude, current.latitude, current.longitude)
            elapsed = max((current.captured_at - last.captured_at).total_seconds() / 3600, 1 / 3600)
            speed_kmph = distance / elapsed

        status, reason = fraud_check(duplicate_exists, worker.device_attested, speed_kmph)
        payout_amount = round(policy.max_payout * payout_factor(payload.event_type), 2)
        if status != ClaimStatus.approved:
            payout_amount = 0.0

        claim = Claim(
            id=store.new_claim_id(),
            worker_id=worker.id,
            policy_id=policy.id,
            event_id=event.id,
            event_type=payload.event_type,
            status=status,
            payout_amount=payout_amount,
            reason=reason,
            created_at=store.now(),
        )
        store.claims[claim.id] = claim
        claims_processed += 1

        if claim.status == ClaimStatus.approved:
            approved += 1
            payout = Payout(
                id=store.new_payout_id(),
                claim_id=claim.id,
                worker_id=worker.id,
                amount=claim.payout_amount,
                created_at=store.now(),
            )
            store.payouts[payout.id] = payout
        elif claim.status == ClaimStatus.review:
            reviewed += 1
        else:
            blocked += 1

    return {
        "event": event,
        "claims_processed": claims_processed,
        "approved": approved,
        "review": reviewed,
        "blocked": blocked,
    }


@app.get("/workers/{worker_id}/dashboard")
def worker_dashboard(worker_id: str) -> dict:
    worker = store.workers.get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    active_policy = next((p for p in store.policies.values() if p.worker_id == worker_id and p.active), None)
    claims = [c for c in store.claims.values() if c.worker_id == worker_id]
    payouts = [p for p in store.payouts.values() if p.worker_id == worker_id]
    earnings_protected = round(sum(p.amount for p in payouts), 2)

    return {
        "worker": worker,
        "active_policy": active_policy,
        "claims": claims,
        "payouts": payouts,
        "metrics": {
            "earnings_protected": earnings_protected,
            "claims_count": len(claims),
            "active_coverage": bool(active_policy),
            "coverage_renews_in_days": 7,
        },
    }


@app.get("/admin/dashboard")
def admin_dashboard() -> dict:
    total_premium = sum(p.weekly_premium for p in store.policies.values())
    total_payout = sum(p.amount for p in store.payouts.values())
    loss_ratio = round((total_payout / total_premium), 3) if total_premium else 0

    claims = list(store.claims.values())
    by_status = {
        "approved": len([c for c in claims if c.status == ClaimStatus.approved]),
        "review": len([c for c in claims if c.status == ClaimStatus.review]),
        "blocked": len([c for c in claims if c.status == ClaimStatus.blocked]),
    }

    upcoming_risk = []
    for zone, event_count in store.zone_event_counter.items():
        score = risk_score(zone)
        projected = "high" if score >= 70 or event_count >= 3 else "moderate" if score >= 40 else "low"
        upcoming_risk.append({"zone": zone, "risk_score": score, "next_week_disruption_risk": projected})

    return {
        "workers": len(store.workers),
        "active_policies": len([p for p in store.policies.values() if p.active]),
        "total_claims": len(claims),
        "total_premiums_collected": round(total_premium, 2),
        "total_payouts": round(total_payout, 2),
        "loss_ratio": loss_ratio,
        "claims_by_status": by_status,
        "zone_analytics": upcoming_risk,
    }


@app.get("/seed")
def seed_demo() -> dict:
    if store.workers:
        return {"message": "Seed already exists"}

    worker = register_worker(
        WorkerCreate(
            name="Rajan",
            phone="9999999999",
            city="Pune",
            zone="pune-central",
            payout_handle="rajan@upi",
            device_attested=True,
        )
    )
    purchase_policy(PolicyPurchaseRequest(worker_id=worker.id, plan="standard"))
    push_location(
        LocationPing(worker_id=worker.id, latitude=18.5204, longitude=73.8567, captured_at=store.now() - timedelta(minutes=20))
    )
    push_location(LocationPing(worker_id=worker.id, latitude=18.5209, longitude=73.8571, captured_at=store.now()))

    return {"message": "Seeded", "worker_id": worker.id}


# Serve Vite-built frontend as single-service deployment.
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.get("/{path_name:path}")
async def serve_spa(path_name: str):
    """Serve SPA index.html for client-side routing. Only called if path doesn't match /api or /assets."""
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not found")
