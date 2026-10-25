# 🛡️ OrderFlow Sentinel — Predict. Explain. Recover Safely.

> **Virtusa Hackathon 2026 — Use Case 1: OrderFlow Sentinel**  
> *A production-grade, interactive prototype demonstrating predictive SLA monitoring, evidence-based root-cause diagnosis, and risk-controlled safe auto-recovery.*

---

## 🌟 Executive Summary & Key Differentiator

In modern enterprise commerce and supply chain architectures, orders traverse dozens of microservices, payment gateways, warehouse management systems (WMS), and carrier APIs. When a network connection drops or an API request times out (HTTP 504), traditional architectures make one of two catastrophic mistakes:
1. **They fail silently** — resulting in delayed fulfillment and SLA penalties.
2. **They blindly retry** — risking **double charges** to customer accounts or **double inventory deductions**.

### ⭐ Our Golden Rule: **“PROVE BEFORE YOU RETRY”**
An API timeout **does not prove failure**. The request may have reached the payment switch or database before the response connection was dropped. **OrderFlow Sentinel** inspects downstream evidence, verifies reconciliation records, validates idempotency duplicate protection, and evaluates safety budgets *before* authorizing any simulated recovery action.

---

## 🏛️ The Four Core Capabilities

| Capability | How It Is Implemented | Business Value |
| :--- | :--- | :--- |
| **1. Order Digital Twin** | Unified view combining order state, stage progression, event logs, API telemetry, and downstream evidence. | Eliminates swivel-chair investigations across fragmented subsystems. |
| **2. Predictive SLA Alerts** | Deterministic stage-duration threshold rule engine (`elapsed_time > stage_sla_limit`). Transparent and auditable without false ML claims. | Proactively alerts operators before contractual SLA breaches occur. |
| **3. Evidence-Based Root Cause** | Diagnostic analyzer that extracts telemetry evidence, missing events, and confidence levels to explain *why* an anomaly occurred. | Cuts Mean Time to Detect (MTTD) and eliminates guesswork. |
| **4. Risk-Based Safe Auto-Healing** | 4-Gate Safety Engine (Failure Verification, Duplicate Protection, Retry Budget, Recovery Policy). | Permits automated recovery only when provably safe; escalates ambiguous cases to human operators. |

---

## 🎯 Three Demonstrable Scenarios

All three scenarios are built into **one unified application** and accessible via prominent action buttons:

### ⚡ Scenario 1: API Timeout — Safe Simulated Retry
- **Target Order:** `ORD-8041` (Acme Retail Logistics, $2,840.00)
- **Situation:** POST `/v1/charges` to PayFlow API times out after 30,000ms.
- **Evidence Inspected:** Central Reconciliation Ledger query returns HTTP 404 (`NOT_FOUND_IN_LEDGER`, `lock_acquired=False`).
- **Safety Gates Evaluated:**
  1. Failure Verified: **PASS** (Zero ledger mutations found)
  2. Duplicate Protection: **PASS** (Idempotency key `idemp-ord-8041-pay-v1` verified active and unused)
  3. Retry Budget: **PASS** (Attempt 0/2 within limit)
  4. Policy Approval: **PASS** (Policy `POL-RECOVER-SAFE` permits retry)
- **Decision:** `SAFE SIMULATED RETRY PERMITTED`
- **Simulated Action:** Dispatches controlled simulated retry with idempotency key $\rightarrow$ HTTP 200 Captured $\rightarrow$ Order stage transitions to `Fulfilment Started`.

### ⏱️ Scenario 2: Delayed Order — Predictive SLA Alert
- **Target Order:** `ORD-8042` (Global Express Direct, $9,120.00)
- **Situation:** Order has stalled in `Fulfilment Started` (Warehouse Picking) for 48 minutes against a configured 15-minute SLA limit (320% consumed, +33m breach).
- **Evidence Inspected:** Missing event `PICK_CONFIRMATION_ACK` from WMS. Downstream telemetry indicates WMS Node #4 RF scanner subnet disconnect and queue backlog (142 items).
- **Rule Applied:** Deterministic Stage Threshold Rule (`elapsed_time > stage_sla_limit`).
- **Decision:** `SLA RISK DETECTED`
- **Simulated Action:** Automated priority dispatch ticket `#OPS-8042-SLA` issued to Warehouse Floor Supervisor proposing to re-route picking to Node #2 (Zone A).

### 🛡️ Scenario 3: Uncertain API Outcome — Block Unsafe Retry
- **Target Order:** `ORD-8043` (Apex Healthcare Supplies, $16,750.00)
- **Situation:** Priority cold-chain medical supply reservation times out during POST `/v2/inventory/commit-coldchain`. Downstream ledger query returns `HTTP 502 Bad Gateway (INDETERMINATE / IN_PROGRESS)`.
- **The Hazard:** Retrying blindly could duplicate reservation of scarce vaccine vials or double-charge $16,750!
- **Safety Gates Evaluated:**
  1. Failure Verified: **FAIL** (Downstream state unconfirmed)
  2. Duplicate Protection: **FAIL** (Server state ambiguous)
- **Decision:** `RETRY BLOCKED 🛑 — HUMAN REVIEW REQUIRED`
- **Human-in-the-Loop Simulation:** Provides interactive operator buttons:
  - `🤝 Verify Committed (Safe)`: Operator reconciles with banking switch, verifies transaction existed, and safely advances order.
  - `🔄 Verify Failed & Retry`: Operator verifies void, authorizes clean retry with human oversight.

---

## 📁 Project Structure

```text
c:\virtusa\
├── app.py                # Main Streamlit enterprise web application
├── data.py               # Synthetic orders dataset (8 orders), stage SLAs, initial audit log
├── engine.py             # SLA risk evaluator, root cause analyzer, 4-gate safety engine
├── test_sentinel.py      # Automated verification suite (Tests A through G)
├── requirements.txt      # Python dependencies (streamlit, pandas)
└── README.md             # Complete setup, demonstration, and deployment guide
```

---

## 🚀 Quickstart: Running Locally on Windows

### Prerequisites
- Python 3.10+ installed
- Command Prompt (`cmd`) or PowerShell

### Step 1: Clone or Navigate to the Workspace
```powershell
cd c:\virtusa
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Launch the Application
```powershell
python -m streamlit run app.py
```

Streamlit will launch locally at:
👉 **`http://localhost:8501`**

---

## 🧪 Automated Test Verification

OrderFlow Sentinel includes an automated verification suite covering all 7 test cases.

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

## ☁️ Public Deployment to Streamlit Community Cloud

To share one public URL with Virtusa hackathon judges:

1. **Push the Workspace to GitHub**:
   - Initialize git and push `c:\virtusa` to a new GitHub repository (e.g., `github.com/your-username/orderflow-sentinel`).
   ```bash
   git init
   git add .
   git commit -m "Initial commit of OrderFlow Sentinel Hackathon Prototype"
   git branch -M main
   git remote add origin https://github.com/your-username/orderflow-sentinel.git
   git push -u origin main
   ```
2. **Sign in to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. **Deploy New App**:
   - Click **"Create app"** $\rightarrow$ **"Deploy a public app from GitHub"**.
   - Select your repository: `your-username/orderflow-sentinel`.
   - Branch: `main`.
   - Main file path: `app.py`.
4. **Launch & Share**:
   - Click **"Deploy"**. Streamlit will install dependencies from `requirements.txt` and launch your app.
   - Copy the generated public URL (e.g. `https://orderflow-sentinel.streamlit.app`) and share it with the judges!

> **No API keys or databases required:** The application is self-contained with zero external credentials needed.

---

## 🎤 Hackathon Judge Demo Walkthrough (3 Minutes)

1. **Introduction (30s):**
   - Point out the navy blue / teal enterprise header and the 4 live KPI metric cards (Total Orders: 8, Orders at SLA Risk, Human Review Required).
   - Explain our core philosophy: **“Prove Before You Retry”**.

2. **Demonstrate Scenario 1 — Safe Recovery (45s):**
   - Click **`⚡ Run API Timeout Scenario`**.
   - Show the green banner: `SAFE SIMULATED RETRY PERMITTED`.
   - Highlight the **4-Gate Safety Checklist** showing all green checkmarks.
   - Point out how the simulated retry updated order `ORD-8041` from `Payment Confirmed` to `Fulfilment Started`.

3. **Demonstrate Scenario 2 — Predictive SLA Alert (45s):**
   - Click **`⏱️ Run Delayed Order Scenario`**.
   - Show the amber alert: `SLA RISK DETECTED (320% consumed, +33m overdue)`.
   - Explain the missing scan event and WMS RF scanner telemetry.
   - Emphasize our transparent rule-based detection (no black-box fake ML).

4. **Demonstrate Scenario 3 — Uncertain Outcome (45s):**
   - Click **`🛡️ Run Uncertain Outcome Scenario`**.
   - Show the purple banner: `🛑 HUMAN REVIEW REQUIRED`.
   - Explain why: The API timed out, but the downstream ledger is indeterminate (HTTP 502). Retrying blindly could duplicate medical vaccine reservations.
   - Click **`🤝 Verify Committed (Safe)`** or **`🔄 Verify Failed & Retry`** to show full human-in-the-loop closure!

5. **Fleet View, Edge-Case Lab & Audit Trail (30s):**
   - Switch to **Tab 2 (Order Digital Twin)**: Show the search bar, 8 orders, event timeline, and raw API telemetry logs.
   - Switch to **Tab 3 (Edge-Case Lab)**: Show judges how toggling off duplicate protection or sliding retry count to 2 immediately triggers **RETRY BLOCKED**.
   - Switch to **Tab 4 (Audit Trail)**: Show the immutable event log and click **Download Audit Trail (CSV)**.
   - Click **`🔄 Reset Demo`** to demonstrate reproducibility!

---

## 🔬 Implementation vs. Simulation Transparency

| Component | Status | Details |
| :--- | :---: | :--- |
| **Diagnostic Decision Engine** | **Implemented** | Real rule-based root cause analysis and SLA risk calculations. |
| **4-Gate Safety Engine** | **Implemented** | Strict logic gates evaluating failure evidence, idempotency, retry budgets, and policy. |
| **State & Fleet Management** | **Implemented** | Session-state persistence supporting 8 realistic orders, search, filters, and dynamic KPIs. |
| **Interactive Human-in-the-Loop** | **Implemented** | Operator verification workflows and live edge-case testing playground. |
| **Audit Trail & CSV Export** | **Implemented** | Structured event logging with one-click CSV download. |
| **Downstream Payment & WMS APIs** | **Simulated** | Realistic HTTP telemetry and responses without real financial or physical movements. |

---

## 🏆 Aligned with Virtusa Hackathon Criteria
- **Business Impact:** Prevents costly duplicate transactions and eliminates SLA breach fines.
- **Explainability:** Clear English reasons and evidence checklists for every automated decision.
- **Safety First:** "Prove Before You Retry" prevents catastrophic double-allocations.
- **Judge-Ready:** Zero setup friction, 100% reproducible via Reset, and ready for cloud deployment.
