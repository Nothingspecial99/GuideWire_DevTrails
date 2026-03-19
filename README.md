# GigSwift

AI-powered parametric income protection for food delivery workers in India.

Tagline: A rainy day should not become a no-income day.

---


## One-Line Idea

GigSwift provides weekly, low-cost insurance for food delivery partners where payouts are triggered automatically by real-world disruption signals like heavy rain, extreme heat, pollution, and city shutdowns.

---

## Why This Problem Matters

Food delivery workers earn only when they can ride and complete orders. If rain, heat, pollution, or city restrictions reduce deliveries, income drops immediately. Most insurance products help with accidents or medical issues, but almost none protect day-to-day earnings disruption.

This creates a protection gap for a large workforce that is already financially vulnerable.

Human reality:

- A partner may earn around ₹700-₹900 on a normal day.
- In severe rain, earnings can fall sharply because demand or serviceability drops.
- Missing even 2-3 working days can break weekly household budgets.
- Workers need predictable support, not paperwork-heavy claim processes.

---

## Persona Selection

Selected Persona: Food Delivery Workers (Zomato and Swiggy)

Why this is our best focus:

- High disruption sensitivity: weather directly affects deliveries.
- Clear, measurable triggers: rain, heat, AQI, shutdown alerts.
- Strong judge clarity: easy to understand problem and solution quickly.

Primary persona snapshot:

- Name: Rajan (representative user)
- Age: 28
- City: Pune
- Work style: 10-11 hours/day, 6 days/week
- Financial pressure: weekly earnings fund rent, food, family expenses
- Pain point: disruption days cause sudden income shock

---

## Real Problem Scenarios

### Scenario 1: Heavy Rain

Situation:

- Rainfall crosses threshold in the worker's operating zone.
- Deliveries reduce, rider either cannot work safely or gets too few orders.

Impact:

- Daily loss can be around ₹500-₹800.

GigSwift response:

- Weather trigger is detected.
- Claim is auto-initiated.
- Payout is sent without manual claim forms.

### Scenario 2: Extreme Heat

Situation:

- Temperature remains above 42°C for long hours.
- Worker cannot continue long riding shifts safely.

Impact:

- Partial day income is lost.

GigSwift response:

- Heat trigger activates partial/full support based on rule thresholds.

### Scenario 3: Curfew or Strike

Situation:

- City disruption declared by local authority.
- Deliveries pause or become inaccessible.

Impact:

- Full-day earning opportunity disappears.

GigSwift response:

- Verified civic disruption trigger activates payout logic.

---

## Parametric Trigger Framework

Parametric means payout is driven by verified external data, not subjective claim approval.

| Event | Trigger Condition | Data Source | Expected Action |
|---|---|---|---|
| Heavy Rain | Rainfall > 30-35 mm in defined period | IMD + OpenWeatherMap | Auto claim start |
| Extreme Heat | Temperature > 42°C for sustained hours | OpenWeatherMap | Heat disruption payout |
| Flood Alert | Area-level flood warning | Disaster/alert APIs | Full disruption payout |
| Air Pollution | AQI > 350 for sustained period | CPCB/AQI APIs | Partial disruption payout |
| Curfew/Strike | Verified city shutdown notice | Govt/News signal + admin check | Event-linked payout |

Core workflow:

Event detected -> Policy eligibility check -> Fraud checks -> Payout approved -> Worker notified

---

## Weekly Premium Model

Weekly pricing matches how many delivery workers think and budget.

Reference plans for concept:

| Plan | Weekly Premium | Coverage (Per Event Cap) |
|---|---:|---:|
| Basic | ₹25 | ₹500 |
| Standard | ₹40 | ₹800 |
| Pro | ₹60 | ₹1,200 |

Pricing logic:

Weekly Premium = Base Premium x Zone Risk Multiplier x Plan Multiplier

Example risk interpretation:

- Low risk zone: lower premium recommendation
- Medium risk zone: balanced premium
- High risk zone: higher premium with stronger coverage suggestion

---

## AI and ML Components

Our solution includes model strategy and design, not production model deployment.

### AI Model 1: Risk Prediction

Goal:

- Recommend fair weekly premium based on disruption exposure.

Inputs:

- Worker location and zone
- Historical weather pattern
- Flood risk characteristics
- Pollution trend
- Delivery activity density (zone-level)

Output:

- Risk score (0-100)
- Suggested plan and premium band

Candidate methods:

- Rule-based baseline in early stage
- Gradient boosting model as data matures

### AI Model 2: Fraud Detection

Goal:

- Reduce false payouts while keeping genuine worker payouts fast.

Fraud patterns considered:

- Duplicate claims for same event
- Suspicious location behavior
- GPS spoofing signals
- Claim timing anomalies

Methods:

- Rule-based hard checks
- Anomaly detection (Isolation Forest)
- Risk flags for manual review queue

---

## Platform Architecture

### Layered Architecture

| Layer | Proposed Stack | Purpose |
|---|---|---|
| Frontend | React (or Flutter alternative) | Onboarding, plans, dashboard, notifications |
| Backend | FastAPI (or Node.js alternative) | Policy, trigger, claim, payout orchestration |
| Database | PostgreSQL (or Firebase option) | Users, policies, claims, trigger logs |
| Event APIs | Weather, AQI, civic alerts | External disruption signals |
| AI Layer | Risk scoring + fraud engine | Pricing intelligence + claim quality control |
| Payments | Razorpay sandbox | Premium collection and payouts |
| Analytics | Worker/Admin dashboards | Monitoring and trust transparency |

### End-to-End Workflow

1. Worker registers with phone and location.
2. System captures city/zone and profile.
3. AI risk engine generates risk score.
4. Weekly premium options are recommended.
5. Worker selects plan and pays weekly premium.
6. System monitors disruption signals continuously.
7. Trigger event occurs and gets validated.
8. Claim process starts automatically.
9. Fraud and eligibility checks run.
10. Payout is sent and worker gets confirmation.

### Visual Flow (for judges)

```text
Worker Onboarding
    ↓
Risk Score + Weekly Plan Recommendation
    ↓
Policy Purchase (Weekly)
    ↓
Live Trigger Monitoring (Weather/AQI/City Events)
    ↓
Disruption Detected
    ↓
Auto Claim + Fraud Checks
    ↓
Instant/Quick Payout + Notification
```

---

## Prototype Concept 

Design-first prototype screens (Figma or equivalent):

1. Worker onboarding
2. Plan recommendation and selection
3. Active coverage dashboard
4. Trigger detected notification
5. Payout confirmation screen

Why this helps:

- Demonstrates user journey clarity
- Shows execution readiness without full build overhead
- Improves judge confidence on usability

---


## Team Note

We are building this with a worker-first mindset: low friction, transparent rules, and faster relief when disruptions happen. The objective is simple: protect dignity and income for people who keep cities moving.

---

## References (For Validation)

- IMD weather and rainfall datasets
- CPCB air quality data
- NITI Aayog and ILO reports on gig workers
- Platform ecosystem references (Zomato/Swiggy public reports)
- IRDAI direction on micro-insurance frameworks

---

**GigSwift**: built for the week-to-week reality of delivery workers.
