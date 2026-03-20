# GigSwift
### AI-Powered Parametric Income Protection for Food Delivery Workers in India

> A rainy day should not become a no-income day.

---

## The Problem

India has over fifteen million platform-based delivery partners working for Zomato, Swiggy, and similar platforms. These workers earn only when they ride and complete orders. A single disruption, whether it is a monsoon downpour, a heatwave, or a local curfew, can erase an entire day of income with no recourse.

The numbers are stark. A typical food delivery partner in a city like Pune earns between Rs. 700 and Rs. 900 on a normal working day. On a heavy rain day, that figure can drop to near zero because orders stop coming in, roads become unrideable, or platforms reduce active zones. Missing two or three working days in a week does not just mean less income. It means missed rent, skipped meals, and borrowed money that carries into the next week.

The insurance industry has not addressed this gap. Existing micro-insurance products for gig workers focus on accidents and hospitalisation. None of them protect the thing that actually breaks a delivery worker's week: lost earnings on disrupted days. GigSwift is built to fill exactly that gap.

---

## Our Persona

**Segment:** Food Delivery Partners (Zomato and Swiggy)

We chose this segment deliberately. Weather and civic events have a direct, measurable, and near-immediate effect on delivery volumes. The triggers are objective and verifiable. The income loss is real and quantifiable. And the workers themselves operate week to week, which makes weekly insurance pricing a natural fit rather than an imposed structure.

**Representative User Profile**

- Name: Rajan
- Age: 28, Pune
- Hours: 10 to 11 hours per day, six days a week
- Income dependency: weekly earnings cover rent, groceries, and family expenses
- Insurance awareness: low, but open to something simple and affordable
- Pain point: no system exists to protect him when rain shuts down his earning day

---

## Real Scenarios We Are Solving

**Scenario 1: Heavy Monsoon Rain**

Rainfall crosses 35mm in a three-hour window across Rajan's operating zone. Delivery demand collapses. He either cannot ride safely or sits waiting for orders that do not come. He loses Rs. 600 to Rs. 800 that day. With GigSwift, the rainfall threshold breach is detected automatically, a claim is initiated without him doing anything, and a payout reaches his account the same day.

**Scenario 2: Extreme Heat Advisory**

Temperature stays above 42 degrees Celsius for four consecutive hours. Riding in this heat is dangerous for sustained periods. Rajan cuts his shift short. He earns Rs. 300 instead of Rs. 800. GigSwift detects the heat event, calculates the disruption window, and processes a partial payout.

**Scenario 3: Curfew or Local Strike**

A sudden curfew is announced in his operating zone. Delivery platforms suspend operations in the flagged area. Rajan's full working day is lost. GigSwift cross-references the civic alert with zone-level policy eligibility and triggers a full disruption payout.

---

## How the Parametric Model Works

Parametric insurance means the payout is driven by verified external data, not by the worker submitting a claim form and waiting for an adjuster. The moment a trigger condition is confirmed from a trusted data source, the system initiates the payout process automatically.

| Trigger Event | Threshold Condition | Data Source | Action |
|---|---|---|---|
| Heavy Rain | Rainfall greater than 35mm in 3 hours | IMD and OpenWeatherMap | Auto-claim initiation |
| Extreme Heat | Temperature above 42 degrees C for 4 hours | OpenWeatherMap and NDMA advisories | Heat disruption payout |
| Flood Alert | Area-level flood warning active | Disaster alert APIs | Full disruption payout |
| Air Pollution | AQI above 350 for 6 hours | CPCB and AQI monitoring APIs | Partial disruption payout |
| Curfew or Strike | Verified geo-fenced restriction alert | State government and news feeds | Event-linked payout |

**Core payout workflow:**

Event detected > Zone and policy eligibility check > Fraud and anomaly checks > Payout approved > Worker notified

---

## Weekly Premium Model

The pricing model is structured weekly because that is how delivery workers think about money. Monthly premiums feel abstract. A weekly Rs. 59 to Rs. 149 amount is tangible and fits within how workers budget.

| Plan | Weekly Premium | Max Payout Per Event |
|---|---|---|
| Basic | Rs. 59 | Rs. 500 |
| Standard | Rs. 99 | Rs. 800 |
| Pro | Rs. 149 | Rs. 1,200 |

**Pricing formula:**

```
Weekly Premium = Base Premium x Zone Risk Multiplier x Plan Multiplier
```

The zone risk multiplier is derived from the AI risk engine. A worker operating in a zone with low historical flood and rainfall incidents gets a lower multiplier. A worker in a zone with consistent monsoon disruptions gets a higher one. This makes pricing fair and defensible, not arbitrary.

---

## AI and ML Components

### Risk Prediction Engine

**Goal:** Recommend a fair weekly premium based on a worker's actual disruption exposure, not a flat rate.

**Inputs to the model:**
- Worker's operating zone and city
- Historical weather disruption data for that zone
- Flood risk index for the area
- Pollution trend data
- Delivery activity density in the zone (as a proxy for exposure time)

**Outputs:**
- Risk score from 0 to 100
- Recommended plan and premium band

**Methodology:** Rule-based baseline for the early stage, with a gradient boosting model (XGBoost) as historical claim and trigger data accumulates. The risk model is zone-level, not individual-level, to protect worker privacy while still enabling fair pricing.

### Fraud Detection Engine

Fraud is a genuine operational risk in parametric systems because payouts are automated. Our fraud detection runs in two layers: hard rule checks that block obvious manipulation instantly, and anomaly detection that flags borderline cases for review.

**Fraud patterns the system checks against:**

- Duplicate claims filed for the same event window
- Location data that does not match the declared operating zone
- GPS spoofing signals detected through spatial-temporal physics validation
- Claim timing that is statistically anomalous compared to the worker's historical pattern
- Device-level signals suggesting emulator or phone farm usage

**Methods:**
- Rule-based hard checks (instant rejection layer)
- Isolation Forest anomaly detection on claim behaviour patterns
- Graph-based ring detection for coordinated fraud networks
- Manual review queue for flagged edge cases

---

## Adversarial Defense Architecture

This section addresses the coordinated fraud scenario specifically. Parametric insurance at scale is vulnerable to organised rings attempting to game the trigger system. Our defense operates across four vectors.

### 1. Hardware Attestation and Device Integrity

The system does not rely on API checks alone. Device-level attestation verifies that the app is running on genuine physical hardware. Rooted devices, emulators, and devices running mock location modules are automatically assigned a high-risk flag and excluded from automated payouts. This cuts off phone farm operations at the device layer before any claim logic runs.

### 2. Spatial-Temporal Physics Validation

Every location ping is run through an impossible travel check. If a device reports a position in a disruption zone that would require exceeding a motorcycle's realistic urban speed to reach from its previous reported position, the claim is flagged. Genuine workers who are sheltering show location jitter consistent with stationary or slow-moving behaviour. Spoofed data tends to appear artificially clean or involves instant position jumps that violate physical movement constraints.

### 3. Cross-Sensor Fusion

GPS data alone is not sufficient for location validation. GigSwift cross-references GPS coordinates with on-device motion sensor data, specifically the accelerometer and gyroscope. If a device reports movement at 30 kmph via GPS while the accelerometer records zero vibration and no rotational change, the location is confirmed as a software simulation and the claim is blocked.

### 4. Graph-Based Ring Detection

Individual fraud checks are not enough to catch coordinated networks of fifty or five hundred accounts. GigSwift uses graph analytics to detect ring topology based on three signals:

- **Shared infrastructure:** Multiple accounts sharing the same WiFi SSID, IP address range, or device fingerprint cluster.
- **Behavioural synchronisation:** Near-identical timing patterns for policy purchase and claim activation across a cluster of accounts that otherwise appear unrelated.
- **Payout consolidation:** Multiple independently registered accounts funnelling payouts into a small set of UPI handles or bank accounts, indicating mule account structures.

Accounts flagged by graph analysis are held for SIU review rather than auto-rejected, because some clusters reflect legitimate shared housing or community group signups. The flag triggers human review, not automatic disqualification.

---

## Platform Architecture

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React (web-first, mobile-responsive) | Worker onboarding, plan selection, dashboard, notifications |
| Backend | FastAPI | Policy management, trigger orchestration, claim processing, payout initiation |
| Database | PostgreSQL | Workers, policies, claims, trigger event logs |
| Event APIs | IMD, OpenWeatherMap, CPCB, Civic alert feeds | External disruption signal ingestion |
| AI Layer | Risk scoring engine and fraud detection engine | Premium calculation and claim quality control |
| Payments | Razorpay sandbox | Premium collection and instant payout simulation |
| Analytics | Worker and admin dashboards | Operational monitoring and trust transparency |

### Platform vs Mobile Decision

We are building web-first with a mobile-responsive interface for Phase 1 and 2, with a Flutter mobile app planned for Phase 3. The reasoning is straightforward: delivery workers access services through phones, but onboarding and policy management on a well-designed mobile web interface reduces the distribution barrier compared to requiring an app download. The Flutter app in Phase 3 enables push notifications for trigger alerts, which is a meaningful UX improvement for the worker.

---

## End-to-End Application Workflow

```
Worker registers with phone number and operating city
        |
System captures zone and builds initial profile
        |
AI risk engine calculates zone-level risk score
        |
Weekly premium options are presented with coverage detail
        |
Worker selects plan and pays weekly premium via UPI or card
        |
System begins continuous disruption signal monitoring for worker's zone
        |
Trigger event detected and validated against threshold conditions
        |
Fraud and eligibility checks run automatically
        |
Payout initiated to worker's registered payment method
        |
Worker receives notification with payout confirmation and event summary
```

---

## Development Plan

**Phase 1 (Current): Ideation and Foundation**
- Finalised persona, problem framing, and parametric trigger design
- Defined premium model and pricing logic
- Documented AI model strategy for risk prediction and fraud detection
- Designed adversarial defense architecture
- Prototype wireframes for core worker journey screens

**Phase 2: Automation and Protection**
- Registration and onboarding flow (functional)
- Insurance policy management module
- Dynamic premium calculation with zone risk model
- Claims management with trigger integration (mock APIs)
- Zero-touch claim process implementation

**Phase 3: Scale and Optimise**
- Advanced fraud detection with device attestation and graph analytics
- Razorpay sandbox integration for simulated instant payouts
- Worker dashboard: active coverage, earnings protected, claim history
- Admin dashboard: loss ratios, zone-level disruption analytics, SIU review queue
- Final pitch deck and video submission

---

## Why This Works

The core design principle of GigSwift is that the worker should never have to prove they were disrupted. The system knows. Weather data is objective. Civic alerts are verifiable. The payout should be a consequence of the event, not a result of the worker's ability to navigate a claims process.

For delivery workers who are already managing tight weekly budgets, a missed payout or a delayed claim is as damaging as no insurance at all. GigSwift is designed so that the default outcome is a fast, transparent payout, and the exception path is a flagged review, not the other way around.

---

## References

- India Meteorological Department weather and rainfall datasets
- CPCB air quality monitoring and AQI data
- NITI Aayog and ILO reports on gig worker income and financial vulnerability
- Zomato and Swiggy annual reports for delivery partner volume references
- IRDAI guidelines on micro-insurance product frameworks
- OpenWeatherMap API documentation
- Razorpay developer sandbox documentation

---

*GigSwift is built for the week-to-week reality of delivery workers. The goal is simple: predictable support when disruptions happen, with zero paperwork and no delays.*
