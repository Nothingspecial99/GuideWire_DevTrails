from math import radians, sin, cos, atan2, sqrt

from .models import ClaimStatus, EventType, PlanType, TriggerEventRequest

BASE_PREMIUM = 59.0
PLAN_MULTIPLIER = {
    PlanType.basic: 1.0,
    PlanType.standard: 99.0 / 59.0,
    PlanType.pro: 149.0 / 59.0,
}
PLAN_MAX_PAYOUT = {
    PlanType.basic: 500.0,
    PlanType.standard: 800.0,
    PlanType.pro: 1200.0,
}
ZONE_RISK = {
    "pune-central": {"mult": 1.0, "rain": 0.7, "heat": 0.5, "flood": 0.3, "aqi": 0.5, "civic": 0.2},
    "mumbai-west": {"mult": 1.2, "rain": 0.9, "heat": 0.4, "flood": 0.6, "aqi": 0.4, "civic": 0.3},
    "delhi-ncr": {"mult": 1.15, "rain": 0.4, "heat": 0.8, "flood": 0.2, "aqi": 0.9, "civic": 0.3},
    "bangalore-east": {"mult": 0.95, "rain": 0.5, "heat": 0.4, "flood": 0.2, "aqi": 0.3, "civic": 0.2},
}


def zone_features(zone: str) -> dict:
    return ZONE_RISK.get(zone, {"mult": 1.0, "rain": 0.5, "heat": 0.5, "flood": 0.3, "aqi": 0.4, "civic": 0.2})


def risk_score(zone: str) -> int:
    features = zone_features(zone)
    weighted = (
        0.30 * features["rain"]
        + 0.20 * features["heat"]
        + 0.20 * features["flood"]
        + 0.20 * features["aqi"]
        + 0.10 * features["civic"]
    )
    return max(0, min(100, int(round(weighted * 100))))


def premium_for(zone: str, plan: PlanType) -> float:
    multiplier = zone_features(zone)["mult"]
    return round(BASE_PREMIUM * PLAN_MULTIPLIER[plan] * multiplier, 2)


def event_triggered(event: TriggerEventRequest) -> bool:
    if event.event_type == EventType.heavy_rain:
        return (event.rain_mm_3h or 0) > 35
    if event.event_type == EventType.extreme_heat:
        return (event.temp_c_4h or 0) > 42
    if event.event_type == EventType.flood_alert:
        return bool(event.flood_alert_active)
    if event.event_type == EventType.air_pollution:
        return (event.aqi_6h or 0) > 350
    if event.event_type == EventType.curfew_or_strike:
        return bool(event.civic_restriction_active)
    return False


def payout_factor(event_type: EventType) -> float:
    if event_type in {EventType.flood_alert, EventType.curfew_or_strike}:
        return 1.0
    if event_type == EventType.heavy_rain:
        return 0.8
    return 0.6


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius * c


def fraud_check(
    duplicate_claim_exists: bool,
    device_attested: bool,
    speed_kmph: float | None,
) -> tuple[ClaimStatus, str]:
    if duplicate_claim_exists:
        return ClaimStatus.blocked, "Duplicate claim for same event"
    if not device_attested:
        return ClaimStatus.blocked, "Device attestation failed"
    if speed_kmph is not None and speed_kmph > 120:
        return ClaimStatus.review, "Impossible travel pattern flagged"
    return ClaimStatus.approved, "Passed automated checks"
