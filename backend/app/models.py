from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PlanType(str, Enum):
    basic = "basic"
    standard = "standard"
    pro = "pro"


class EventType(str, Enum):
    heavy_rain = "heavy_rain"
    extreme_heat = "extreme_heat"
    flood_alert = "flood_alert"
    air_pollution = "air_pollution"
    curfew_or_strike = "curfew_or_strike"


class ClaimStatus(str, Enum):
    approved = "approved"
    review = "review"
    blocked = "blocked"


class WorkerCreate(BaseModel):
    name: str
    phone: str
    city: str
    zone: str
    payout_handle: str
    device_attested: bool = True


class Worker(BaseModel):
    id: str
    name: str
    phone: str
    city: str
    zone: str
    payout_handle: str
    device_attested: bool
    created_at: datetime


class LocationPing(BaseModel):
    worker_id: str
    latitude: float
    longitude: float
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class PolicyPurchaseRequest(BaseModel):
    worker_id: str
    plan: PlanType


class Policy(BaseModel):
    id: str
    worker_id: str
    plan: PlanType
    zone: str
    weekly_premium: float
    max_payout: float
    active: bool = True
    created_at: datetime


class TriggerEventRequest(BaseModel):
    zone: str
    event_type: EventType
    rain_mm_3h: Optional[float] = None
    temp_c_4h: Optional[float] = None
    aqi_6h: Optional[float] = None
    flood_alert_active: Optional[bool] = None
    civic_restriction_active: Optional[bool] = None


class TriggerEvent(BaseModel):
    id: str
    zone: str
    event_type: EventType
    triggered: bool
    created_at: datetime


class Claim(BaseModel):
    id: str
    worker_id: str
    policy_id: str
    event_id: str
    event_type: EventType
    status: ClaimStatus
    payout_amount: float
    reason: str
    created_at: datetime


class Payout(BaseModel):
    id: str
    claim_id: str
    worker_id: str
    amount: float
    channel: str = "razorpay_sandbox"
    status: str = "simulated_success"
    created_at: datetime
