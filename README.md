# 🛡️ OrderFlow Sentinel — Predict delays. Understand problems. Recover safely.

> **Virtusa Hackathon 2026 — Use Case 1: OrderFlow Sentinel**  
> *A production-grade, interactive dashboard demonstrating predictive SLA monitoring, evidence-based root-cause diagnosis, and risk-controlled safe auto-recovery.*  
> **GitHub Repository:** [https://github.com/RAYAHARITHA/virtusa-orderflow-sentinel](https://github.com/RAYAHARITHA/virtusa-orderflow-sentinel)

---

## 🌟 Executive Summary & Key Differentiator

In modern enterprise commerce and supply chain architectures, orders traverse dozens of microservices, payment gateways, warehouse management systems (WMS), and carrier APIs. When a network connection drops or an API request times out (HTTP 504), traditional architectures make one of two catastrophic mistakes:
1. **They fail silently** — resulting in delayed fulfillment and contractual SLA penalties.
2. **They blindly retry** — risking **duplicate charges** to customer accounts or **duplicate inventory deductions**.

### ⭐ Our Golden Rule: **“PROVE BEFORE YOU RETRY”**
An API timeout **does not prove failure**. The request may have reached the payment switch or database before the response connection was dropped. **OrderFlow Sentinel** inspects downstream evidence, verifies reconciliation records, validates idempotency duplicate protection, and evaluates safety budgets *before* authorizing any simulated recovery action.

---

## 🎨 Dashboard Design & Layout Overview

The dashboard matches the reference layout with high contrast, clear cards, and plain English explanations:

```text
+-----------------------------------------------------------------------------------------+
| 🛡️ OrderFlow Sentinel                                                   🟢 Demo Mode     |
| Predict delays. Understand problems. Recover safely.                                    |
+-----------------------------------------------------------------------------------------+
| [Total Orders: 8]   [Orders in Progress: 5]   [Orders Needing Attention: 3]   [Journey] |
+-----------------------------------------------------------------------------------------+
| [ Card 1: API Timeout ]       [ Card 2: Delayed Order ]       [ Card 3: Uncertain ]     |
| Can we retry safely?          Is this order at risk?          Could retry duplicate?    |
| [ Run Demo: API Timeout ]     [ Run Demo: Delayed Order ]     [ Run Demo: Uncertain ]   |
+-----------------------------------------------------------------------------------------+
| Visual Order Journey: ✅ Created ➔ ✅ Paid ➔ 🔵 Inventory ➔ ⚪ Fulfilment ➔ ⚪ Completed   |
+-----------------------------------------------------------------------------------------+
| Interactive Demo Result Section:                                                        |
| Scenario Name                     [ DECISION BADGE ]                       [Reset Demo] |
|                                                                                         |
|  Before (Order Status)     |       Result (6 Core Explanations)     |  After Status     |
|  - Order ID                |       - What happened?                 |  - Updated Stage  |
|  - Previous Stage          |       - Why did it happen?             |  - Updated Status |
|  - Previous Status         |       - What did system check?         |  - What changed   |
|  - What was waiting        |       - Decision                       |                   |
|                            |       - What changed?                  |                   |
|                            |       - Next step                      |                   |
+-----------------------------------------------------------------------------------------+
| ▼ See Technical Details   ▼ See Safety Checks   ▼ See Audit Trail   ▼ See All Orders    |
+-----------------------------------------------------------------------------------------+
```

---

## 🏛️ The Four Core Capabilities

| Capability | How It Is Implemented | Business Value |
| :--- | :--- | :--- |
| **1. Order Digital Twin** | Unified view combining order state, horizontal stage journey, event logs, API telemetry, and downstream evidence. | Eliminates swivel-chair investigations across fragmented subsystems. |
| **2. Predictive SLA Alerts** | Deterministic stage-duration threshold rule engine (`elapsed_time > stage_sla_limit`). Transparent and auditable without false ML claims. | Proactively alerts operators before contractual SLA breaches occur. |
| **3. Evidence-Based Root Cause** | Diagnostic analyzer that extracts telemetry evidence, missing events, and confidence levels to explain *why* an anomaly occurred. | Cuts Mean Time to Detect (MTTD) and eliminates guesswork. |
| **4. Risk-Based Safe Auto-Healing** | 4-Gate Safety Engine (Failure Verification, Duplicate Protection, Retry Budget, Recovery Policy). | Permits automated recovery only when provably safe; escalates ambiguous cases to human operators. |

---

## 🎯 Three Demonstrable Scenarios

All three scenarios are built into **one unified application** and executed via the three top cards:

### ⚡ Card 1 — API Timeout: Safe Simulated Retry
- **Question:** *Can we retry safely?*
- **Explanation:** *The system did not receive a reply from the next service.*
- **Button:** `Run Demo: API Timeout`
- **Target Order:** `ORD-8041` (Acme Retail Logistics, $2,840.00)
- **What happened?** The payment gateway timed out after 30 seconds without returning a confirmation.
- **Why did it happen?** A network drop occurred during the API call. Downstream reconciliation confirmed zero transactions were logged.
- **What did the system check?** Verified failure via downstream ledger; confirmed unique idempotency key; checked retry limit (0/2 used); verified recovery policy.
- **Decision:** **`SAFE RETRY ALLOWED`** (Green Badge)
- **What changed?** Simulated safe retry was dispatched with key `idemp-ord-8041-pay-v1`. Payment succeeded ($2,840.00) and order advanced to Fulfilment Started.
- **Next step:** Proceed with warehouse picking and packing.

### ⏱️ Card 2 — Delayed Order: SLA Alert
- **Question:** *Is this order at risk of missing its target?*
- **Explanation:** *The order has taken longer than expected.*
- **Button:** `Run Demo: Delayed Order`
- **Target Order:** `ORD-8042` (Global Express Direct, $9,120.00)
- **What happened?** The order has been in fulfilment for 48 minutes, exceeding the configured limit of 15 minutes by 33 minutes.
- **Why did it happen?** Warehouse Node #4 RF scanner disconnected, causing pick tickets to queue without scanner confirmation.
- **What did the system check?** Checked elapsed stage duration (48m) against allowed threshold (15m); verified missing pick confirmation scan.
- **Decision:** **`DELAY RISK DETECTED`** (Orange Badge)
- **What changed?** Order was flagged with an SLA breach alert (+33m over limit) and a priority re-route ticket was dispatched to warehouse ops.
- **Next step:** Check the fulfilment status and re-route the picking task to warehouse Node #2 (Zone A).

### 🛡️ Card 3 — Uncertain Outcome: Block Unsafe Retry
- **Question:** *Could retrying create a duplicate?*
- **Explanation:** *The request timed out, and the final result is unknown.*
- **Button:** `Run Demo: Uncertain Outcome`
- **Target Order:** `ORD-8043` (Apex Healthcare Supplies, $16,750.00)
- **What happened?** The request timed out, and the final result is unknown.
- **Why did it happen?** The commit request reached the upstream network before the connection dropped. The ledger cannot confirm whether stock was reserved.
- **What did the system check?** Downstream ledger query (returned HTTP 502 Indeterminate); duplicate protection check (failed due to ambiguity); safety policy.
- **Decision:** **`HUMAN REVIEW REQUIRED — RETRY BLOCKED`** (Red Badge)
- **What changed?** Automatic retry was strictly BLOCKED to prevent duplicate allocation of critical medical vaccines. Order locked in safety escrow.
- **Next step:** Check the order in the other system before deciding whether to retry.
- **Interactive Operator Actions:** Includes simulated operator reconciliation buttons (`Verify Committed (Safe)` and `Verify Void & Safe Retry`) to complete the human-in-the-loop lifecycle.

---

## 📁 Project Structure

```text
c:\virtusa\
├── app.py                # Main Streamlit web application matching reference design
├── data.py               # Synthetic orders dataset (8 orders), stage SLAs, initial audit log
├── engine.py             # SLA risk evaluator, root cause analyzer, 4-gate safety engine
├── test_sentinel.py      # Automated verification suite (Tests A through G)
├── requirements.txt      # Python dependencies (streamlit, pandas)
└── README.md             # Complete setup, demonstration, and deployment guide
```

---

## 🚀 Local Setup Instructions (Windows)

### Step 1: Open PowerShell or Command Prompt
```powershell
cd C:\virtusa
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run the Application
```powershell
python -m streamlit run app.py
```

Streamlit will launch locally in your browser at:  
👉 **`http://localhost:8501`**

---

## 🧪 Automated Test Verification

Run the test suite:
```powershell
python test_sentinel.py
```

### Test Results Summary:
| Test ID | Condition Tested | Result | Verification Detail |
| :--- | :--- | :---: | :--- |
| **Test A** | Safe simulated retry on verified failure | **PASS** | 4 safety gates pass $\rightarrow$ `RETRY_PERMITTED` $\rightarrow$ Stage advanced |
| **Test B** | Delayed order exceeding stage threshold | **PASS** | `CRITICAL_SLA_RISK` detected (+33m breach, 320% consumed) |
| **Test C** | Uncertain API outcome blocks retry | **PASS** | `HUMAN_REVIEW_REQUIRED` displayed; blind retry blocked |
| **Test D** | Duplicate protection failure | **PASS** | Reused idempotency key strictly blocked |
| **Test E** | Retry count at or above limit | **PASS** | Retries $\ge 2$ blocked by budget constraint |
| **Test F** | Reset Demo state restoration | **PASS** | In-memory session state restored to baseline |
| **Test G** | Integrated execution in single session | **PASS** | All 3 scenarios execute without interference |
| **OVERALL** | **7 of 7 Tests Passed** | **100%** | **Ready for Hackathon Judging** |

---

## 📤 Commands to Upload Changes to GitHub

To commit and push all updates to your repository:

```powershell
cd C:\virtusa
git add app.py data.py engine.py test_sentinel.py requirements.txt README.md
git commit -m "Enhance UI/UX to match reference dashboard design: 4 summary cards, 3 scenario cards, 3-column result layout, and visual journey tracker"
git push origin main
```

Your repository: [https://github.com/RAYAHARITHA/virtusa-orderflow-sentinel](https://github.com/RAYAHARITHA/virtusa-orderflow-sentinel)

---

## ☁️ Deployment Instructions for Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Click **"New app"** (or find your existing app).
3. Repository: `RAYAHARITHA/virtusa-orderflow-sentinel`
4. Branch: `main`
5. Main file path: `app.py`
6. Click **"Deploy"**.
7. Share the public URL with hackathon judges! (No external database or API keys required).

---

## 🔬 Implementation vs. Simulation Transparency

| Component | Status | Details |
| :--- | :---: | :--- |
| **Diagnostic Decision Engine** | **Implemented** | Real rule-based root cause analysis and SLA risk calculations. |
| **4-Gate Safety Engine** | **Implemented** | Strict logic gates evaluating failure evidence, idempotency, retry budgets, and policy. |
| **State & Fleet Management** | **Implemented** | Session-state persistence supporting 8 realistic orders, search, filters, and dynamic KPIs. |
| **Interactive Human-in-the-Loop** | **Implemented** | Operator verification actions and live edge-case parameter toggles. |
| **Audit Trail & CSV Export** | **Implemented** | Structured event logging with one-click CSV download. |
| **Downstream Payment & WMS APIs** | **Simulated** | Realistic synthetic HTTP telemetry and responses without real financial or physical movements. |

---

## 🏆 Aligned with Virtusa Hackathon Criteria
- **Business Impact:** Prevents costly duplicate transactions and eliminates SLA breach fines.
- **Explainability:** Clear English reasons and evidence checklists for every automated decision.
- **Safety First:** "Prove Before You Retry" prevents catastrophic double-allocations.
- **Judge-Ready:** Zero setup friction, 100% reproducible via Reset, and ready for cloud deployment.
