"""
OrderFlow Sentinel — Predict. Explain. Recover Safely.
Virtusa Hackathon Prototype — Use Case 1: OrderFlow Sentinel
Built with Python, Streamlit, and Pandas.
"""

import copy
import streamlit as st
import pandas as pd
from datetime import datetime

# Import modular data and engine components
from data import get_initial_orders, get_initial_audit_log, get_stage_sla_limits
from engine import (
    calculate_sla_risk,
    analyze_root_cause,
    check_retry_safety,
    run_api_timeout_scenario,
    run_delayed_order_scenario,
    run_uncertain_outcome_scenario,
    run_operator_resolution
)

# ---------------------------------------------------------
# Page Configuration & Modern Enterprise Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="OrderFlow Sentinel | Predict. Explain. Recover Safely.",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS: Navy Blue, Teal, White, and Subtle Gray
st.markdown("""
<style>
    /* Global Theme & Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container background */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header Container */
    .sentinel-header {
        background: linear-gradient(135deg, #0a192f 0%, #0f3460 50%, #172a45 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(10, 25, 47, 0.15);
        border-left: 6px solid #00b4d8;
    }
    .sentinel-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #ffffff;
    }
    .sentinel-subtitle {
        font-size: 1.15rem;
        font-weight: 500;
        color: #64ffda;
        margin-top: 4px;
        letter-spacing: 0.5px;
    }
    .sentinel-desc {
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-top: 8px;
        max-width: 900px;
        line-height: 1.45;
    }
    .sentinel-tag {
        display: inline-block;
        background: rgba(0, 180, 216, 0.2);
        color: #00b4d8;
        border: 1px solid #00b4d8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 10px;
    }

    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #64748b;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Scenario Launch Bar */
    .scenario-bar-container {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* Decision Alert Banners */
    .decision-banner-safe {
        background: #ecfdf5;
        border: 2px solid #10b981;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 16px 0;
    }
    .decision-banner-blocked {
        background: #fef2f2;
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 16px 0;
    }
    .decision-banner-warning {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 16px 0;
    }
    .decision-banner-review {
        background: #f5f3ff;
        border: 2px solid #7c3aed;
        border-radius: 10px;
        padding: 18px 22px;
        margin: 16px 0;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 14px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
    }
    .badge-success { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .badge-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .badge-warning { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .badge-info { background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }
    .badge-purple { background: #ede9fe; color: #6d28d9; border: 1px solid #c4b5fd; }
    .badge-neutral { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* Timeline styling */
    .timeline-node {
        border-left: 3px solid #00b4d8;
        padding-left: 16px;
        margin-left: 8px;
        margin-bottom: 14px;
        position: relative;
    }
    .timeline-node::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 2px;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #00b4d8;
        border: 2px solid #ffffff;
    }

    /* Gate Card */
    .gate-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization (In-Memory Session State)
# ---------------------------------------------------------
if "orders" not in st.session_state:
    st.session_state.orders = get_initial_orders()

if "audit_log" not in st.session_state:
    st.session_state.audit_log = get_initial_audit_log()

if "executed_idemp_keys" not in st.session_state:
    st.session_state.executed_idemp_keys = set()

if "active_scenario_result" not in st.session_state:
    st.session_state.active_scenario_result = None

if "selected_order_id" not in st.session_state:
    st.session_state.selected_order_id = "ORD-8041"

def reset_entire_demo():
    """Restores initial state for fresh demonstration."""
    st.session_state.orders = get_initial_orders()
    st.session_state.audit_log = get_initial_audit_log()
    st.session_state.executed_idemp_keys = set()
    st.session_state.active_scenario_result = None
    st.session_state.selected_order_id = "ORD-8041"

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown("""
<div class="sentinel-header">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
            <h1 class="sentinel-title">🛡️ OrderFlow Sentinel</h1>
            <div class="sentinel-subtitle">Predict. Explain. Recover Safely.</div>
            <div class="sentinel-desc">
                Monitor order health, detect SLA risks, investigate failures, and demonstrate evidence-based recovery.
                Core Differentiator: <strong>“Prove Before You Retry”</strong> — never blindly retry on API timeout.
            </div>
        </div>
        <div>
            <span class="sentinel-tag">Virtusa Hackathon Prototype • Use Case 1</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dynamic Top KPI Metrics
# ---------------------------------------------------------
orders_dict = st.session_state.orders
total_orders = len(orders_dict)
in_progress_count = sum(1 for o in orders_dict.values() if o["status_code"] in ["IN_PROGRESS", "API_TIMEOUT", "API_ERROR", "SLA_RISK", "UNCERTAIN_TIMEOUT", "RETRY_PERMITTED", "RETRY_BLOCKED", "HUMAN_REVIEW_REQUIRED"])
sla_risk_count = sum(1 for o in orders_dict.values() if o["status_code"] == "SLA_RISK" or "SLA Risk" in o["risk_level"])
human_review_count = sum(1 for o in orders_dict.values() if o["status_code"] == "HUMAN_REVIEW_REQUIRED" or o["status"] == "Human Review Required")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #00b4d8;">
        <div class="metric-label">Total Monitored Orders</div>
        <div class="metric-value">{total_orders}</div>
        <div class="metric-sub">Across 7 lifecycle stages</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #0284c7;">
        <div class="metric-label">Orders in Progress</div>
        <div class="metric-value">{in_progress_count}</div>
        <div class="metric-sub">Active pipeline transactions</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #f59e0b;">
        <div class="metric-label">Orders at SLA Risk</div>
        <div class="metric-value" style="color: #b45309;">{sla_risk_count}</div>
        <div class="metric-sub">Deterministic stage threshold breach</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #7c3aed;">
        <div class="metric-label">Human Review Required</div>
        <div class="metric-value" style="color: #6d28d9;">{human_review_count}</div>
        <div class="metric-sub">Uncertain outcome / Safety lock</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Prominent Scenario Launch Bar
# ---------------------------------------------------------
st.markdown("### 🎯 Interactive Demo Scenarios")
st.markdown("""
<div style="font-size: 0.9rem; color: #475569; margin-bottom: 10px;">
    Click any scenario button below to simulate live telemetry and evaluate the Sentinel Safety Engine:
</div>
""", unsafe_allow_html=True)

btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1.2, 1.2, 1.3, 0.8])

with btn_c1:
    if st.button("⚡ Run API Timeout Scenario", use_container_width=True, type="primary"):
        res = run_api_timeout_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log,
            executed_idemp_keys=st.session_state.executed_idemp_keys
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8041"
        st.toast("Scenario 1 Executed: Safe simulated retry permitted!", icon="⚡")

with btn_c2:
    if st.button("⏱️ Run Delayed Order Scenario", use_container_width=True):
        res = run_delayed_order_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8042"
        st.toast("Scenario 2 Executed: SLA risk alert raised!", icon="⏱️")

with btn_c3:
    if st.button("🛡️ Run Uncertain Outcome Scenario", use_container_width=True):
        res = run_uncertain_outcome_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log,
            executed_idemp_keys=st.session_state.executed_idemp_keys
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8043"
        st.toast("Scenario 3 Executed: Retry blocked — Human Review Required!", icon="🛡️")

with btn_c4:
    if st.button("🔄 Reset Demo", use_container_width=True, help="Restore original synthetic order data and audit state"):
        reset_entire_demo()
        st.toast("Demo state reset to initial synthetic baseline.", icon="🔄")
        st.rerun()

st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Tabs Navigation
# ---------------------------------------------------------
tab_scenario, tab_fleet, tab_edge, tab_audit, tab_guide = st.tabs([
    "🚀 Active Scenario & Recovery Console",
    "📦 Order Digital Twin & Fleet Dashboard",
    "🔬 Safety Gates & Edge-Case Lab",
    "📜 Immutable Audit Trail",
    "🎓 Presentation & Architecture Guide"
])

# =========================================================
# TAB 1: ACTIVE SCENARIO & RECOVERY CONSOLE
# =========================================================
with tab_scenario:
    active_res = st.session_state.active_scenario_result

    if active_res is None:
        st.info("👆 **Select and run one of the three scenarios above** (or inspect existing sample orders in Tab 2).")
        st.markdown("""
        #### Demonstrable Scenarios Overview:
        - **Scenario 1: API Timeout & Safe Simulated Retry**
          - Simulates a payment gateway timeout where downstream ledger reconciliation proves the transaction was never created. All 4 safety gates pass. Simulated safe retry is authorized and executed.
        - **Scenario 2: Delayed Order & Predictive SLA Alert**
          - Simulates a warehouse picking task that has stalled for 48 minutes against a 15-minute threshold. Transparent rule-based SLA risk alert raised with root-cause telemetry.
        - **Scenario 3: Uncertain API Outcome & Human Review ("Prove Before You Retry")**
          - Simulates an inventory commit timeout where the downstream ledger is indeterminate (HTTP 502). Automatic retry is strictly blocked to prevent double-reservation.
        """)
    else:
        scenario_name = active_res["scenario_name"]
        order = active_res["order"]
        order_id = order["order_id"]

        st.markdown(f"### 📍 Execution Result: {scenario_name}")

        # Top order summary pill
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 20px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <strong style="color: #0f172a; font-size: 1.1rem;">Order: {order_id}</strong>
                <span style="color: #64748b; margin-left: 10px;">| Customer: {order['customer']}</span>
                <span style="color: #64748b; margin-left: 10px;">| Value: ${order['amount']:,.2f}</span>
            </div>
            <div>
                <span class="badge badge-info">{order['current_stage']}</span>
                <span class="badge badge-warning" style="margin-left: 6px;">{order['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # SCENARIO 1 RENDER
        if "Scenario 1" in scenario_name:
            safety = active_res["safety_result"]
            action = active_res["simulated_action_result"]

            st.markdown(f"""
            <div class="decision-banner-safe">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.8rem;">✅</span>
                    <div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #065f46;">
                            {action['title']}
                        </div>
                        <div style="font-size: 0.95rem; color: #047857; margin-top: 4px;">
                            {safety['reason']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sc1_col1, sc1_col2 = st.columns([1.1, 0.9])

            with sc1_col1:
                st.markdown("#### 🔍 Evidence Inspected & Downstream Telemetry")
                st.markdown("""
                - **Simulated Event:** Client observed `HTTP 504 Gateway Timeout` after 30,000ms.
                - **Downstream Inquiry:** Sent verification query to `PayFlow Central Reconciliation Ledger`.
                - **Ledger Verification:** Returned `HTTP 404 (NOT_FOUND_IN_LEDGER)` with `lock_acquired=False`.
                - **Conclusion:** Conclusively proven that request dropped before downstream execution.
                """)

                st.markdown("#### 🛡️ 4-Gate Safety Checklist")
                for key, gate in safety["checks_matrix"].items():
                    icon = "✅" if gate["status"] == "PASS" else "❌"
                    badge_cls = "badge-success" if gate["status"] == "PASS" else "badge-danger"
                    st.markdown(f"""
                    <div class="gate-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{icon} {gate['name']}</strong>
                            <span class="badge {badge_cls}">{gate['status']}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">{gate['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with sc1_col2:
                st.markdown("#### ⚡ Safe Simulated Recovery Action")
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-weight: 600; color: #0f172a;">Executed Action:</div>
                    <div style="font-family: monospace; font-size: 0.88rem; background: #f1f5f9; padding: 8px; border-radius: 4px; margin-top: 4px;">
                        {action['action_executed']}
                    </div>
                    <div style="font-weight: 600; color: #0f172a; margin-top: 10px;">Simulated API Response:</div>
                    <div style="font-family: monospace; font-size: 0.85rem; color: #166534; background: #dcfce7; padding: 8px; border-radius: 4px; margin-top: 4px;">
                        {action['simulated_response']}
                    </div>
                    <div style="font-weight: 600; color: #0f172a; margin-top: 10px;">Order State Transition:</div>
                    <div style="font-size: 0.9rem; font-weight: 600; color: #0284c7; margin-top: 2px;">
                        {action['order_stage_transition']}
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 8px;">
                        ℹ️ <em>Clearly labeled: This is a controlled in-memory simulation. No real money moved.</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # SCENARIO 2 RENDER
        elif "Scenario 2" in scenario_name:
            sla_info = active_res["sla_result"]
            root_cause = active_res["root_cause"]
            action = active_res["simulated_action_result"]

            st.markdown(f"""
            <div class="decision-banner-warning">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.8rem;">⚠️</span>
                    <div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #92400e;">
                            {active_res['alert_title']}
                        </div>
                        <div style="font-size: 0.95rem; color: #b45309; margin-top: 4px;">
                            {sla_info['message']}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sc2_col1, sc2_col2 = st.columns([1.1, 0.9])

            with sc2_col1:
                st.markdown("#### ⏱️ Stage Duration vs. SLA Threshold")
                st.progress(min(1.0, sla_info['consumption_pct'] / 100.0))
                st.markdown(f"""
                - **Current Stage:** `{order['current_stage']}`
                - **Elapsed Time:** `{sla_info['elapsed_minutes']:.1f} mins`
                - **Configured SLA Limit:** `{sla_info['threshold_minutes']:.1f} mins`
                - **Consumption Ratio:** `{(sla_info['consumption_pct']):.0f}% of allowed budget`
                - **Breach Status:** Exceeded threshold by `+{sla_info['elapsed_minutes'] - sla_info['threshold_minutes']:.1f} minutes`
                """)

                st.markdown("#### 🔍 Root-Cause Telemetry & Missing Confirmation")
                st.markdown(f"**Likely Cause:** {root_cause['likely_cause']}")
                for ev in root_cause["supporting_evidence"]:
                    st.markdown(f"- 📄 {ev}")
                st.markdown(f"- ⚠️ **Missing Event:** {', '.join(root_cause['missing_evidence'])}")

            with sc2_col2:
                st.markdown("#### 💡 Transparent Rule-Based Diagnosis")
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
                    <div style="font-weight: 600; color: #0f172a;">Rule Applied:</div>
                    <div style="font-size: 0.85rem; color: #475569; background: #f8fafc; padding: 8px; border-radius: 4px; margin-top: 4px;">
                        <code>{sla_info['rule_applied']}</code>
                    </div>
                    <div style="font-weight: 600; color: #0f172a; margin-top: 10px;">Confidence:</div>
                    <div style="font-size: 0.88rem; color: #059669; font-weight: 600;">{root_cause['confidence_label']}</div>
                    <div style="font-weight: 600; color: #0f172a; margin-top: 10px;">Recommended Next Action:</div>
                    <div style="font-size: 0.88rem; color: #b45309;">{sla_info['recommendation']}</div>
                    <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                        <span class="badge badge-warning">Simulated Action Dispatched</span>
                        <div style="font-size: 0.82rem; color: #475569; margin-top: 4px;">{action['action_executed']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # SCENARIO 3 RENDER
        elif "Scenario 3" in scenario_name:
            safety = active_res["safety_result"]
            root_cause = active_res["root_cause"]
            action = active_res["simulated_action_result"]

            st.markdown(f"""
            <div class="decision-banner-review">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 2rem;">🛑</span>
                        <div>
                            <div style="font-size: 1.3rem; font-weight: 800; color: #581c87;">
                                {active_res['alert_title']}
                            </div>
                            <div style="font-size: 0.95rem; color: #6b21a8; margin-top: 4px;">
                                {safety['reason']}
                            </div>
                        </div>
                    </div>
                    <div>
                        <span class="badge badge-purple" style="font-size: 0.9rem; padding: 6px 14px;">
                            ⭐ {active_res['core_differentiator']}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sc3_col1, sc3_col2 = st.columns([1.1, 0.9])

            with sc3_col1:
                st.markdown("#### 🚨 Why Blind Retry is BLOCKED")
                st.markdown("""
                - **The Golden Rule:** An API timeout does **NOT** equal failure!
                - **The Hazard:** The downstream cold-chain ledger received the commit request before the socket timed out.
                - **Reconciliation Status:** Upstream ledger returned `HTTP 502 Bad Gateway (INDETERMINATE / IN_PROGRESS)`.
                - **Double-Mutation Risk:** Blindly retrying now could duplicate reservation of 500 scarce medical units or double-charge $16,750!
                - **Safety Action:** Automatic retries suspended. Safety Escrow Lock engaged.
                """)

                st.markdown("#### 🛡️ 4-Gate Safety Checklist")
                for key, gate in safety["checks_matrix"].items():
                    icon = "✅" if gate["status"] == "PASS" else "❌"
                    badge_cls = "badge-success" if gate["status"] == "PASS" else "badge-danger"
                    st.markdown(f"""
                    <div class="gate-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{icon} {gate['name']}</strong>
                            <span class="badge {badge_cls}">{gate['status']}</span>
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">{gate['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with sc3_col2:
                st.markdown("#### 👤 Complete the Human-in-the-Loop Lifecycle")
                st.markdown("""
                As an authorized operator, simulate manual ledger verification to safely resolve this order:
                """)

                op_col1, op_col2 = st.columns(2)
                with op_col1:
                    if st.button("🤝 Verify Committed (Safe)", use_container_width=True, help="Operator confirmed transaction succeeded downstream"):
                        run_operator_resolution(
                            orders=st.session_state.orders,
                            audit_log=st.session_state.audit_log,
                            order_id="ORD-8043",
                            resolution_type="VERIFIED_COMMITTED",
                            executed_idemp_keys=st.session_state.executed_idemp_keys
                        )
                        st.toast("Operator verified transaction was committed! Order unlocked.", icon="✅")
                        st.rerun()

                with op_col2:
                    if st.button("🔄 Verify Failed & Retry", use_container_width=True, help="Operator confirmed downstream was voided, safe to retry"):
                        run_operator_resolution(
                            orders=st.session_state.orders,
                            audit_log=st.session_state.audit_log,
                            order_id="ORD-8043",
                            resolution_type="VERIFIED_FAILED_RETRY",
                            executed_idemp_keys=st.session_state.executed_idemp_keys
                        )
                        st.toast("Operator confirmed void and authorized controlled retry!", icon="🔄")
                        st.rerun()

                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; margin-top: 14px;">
                    <div style="font-weight: 600; color: #0f172a;">Simulated Safety Escrow:</div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                        {action['action_executed']}
                    </div>
                    <div style="font-family: monospace; font-size: 0.82rem; color: #6b21a8; background: #f5f3ff; padding: 6px; border-radius: 4px; margin-top: 6px;">
                        {action['simulated_response']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Common Event Timeline for Target Order
        st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown(f"#### 📜 Updated Event Timeline for `{order_id}`")

        for ev in reversed(order["events"]):
            st_badge = {
                "SUCCESS": "badge-success",
                "WARNING": "badge-warning",
                "ERROR": "badge-danger",
                "PENDING": "badge-info"
            }.get(ev.get("status", "SUCCESS"), "badge-neutral")

            st.markdown(f"""
            <div class="timeline-node">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #0f172a;">{ev['event_name']}</strong>
                    <span style="font-size: 0.8rem; color: #64748b;">{ev['timestamp']}</span>
                </div>
                <div style="margin-top: 2px;">
                    <span class="badge {st_badge}">{ev.get('stage', 'Stage')}</span>
                    <span style="font-size: 0.85rem; color: #334155; margin-left: 8px;">{ev['detail']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# TAB 2: ORDER DIGITAL TWIN & FLEET DASHBOARD
# =========================================================
with tab_fleet:
    st.markdown("### 📦 Fleet-Wide Order Digital Twins")
    st.markdown("Select any synthetic order to inspect its unified state, timeline, telemetry logs, and diagnostic evaluation.")

    # Search and Filter Controls
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.2, 1.2])
    with f_col1:
        search_query = st.text_input("🔍 Search by Order ID, Customer, or Item", placeholder="e.g. ORD-8041, Acme, Scanners")
    with f_col2:
        status_filter = st.selectbox("Filter by Status", ["All Statuses"] + sorted(list({o["status"] for o in orders_dict.values()})))
    with f_col3:
        risk_filter = st.selectbox("Filter by Risk Level", ["All Risks"] + sorted(list({o["risk_level"] for o in orders_dict.values()})))

    # Filter Orders
    filtered_orders = []
    for oid, o in orders_dict.items():
        if search_query:
            q = search_query.lower()
            if q not in oid.lower() and q not in o["customer"].lower() and q not in o["item_summary"].lower():
                continue
        if status_filter != "All Statuses" and o["status"] != status_filter:
            continue
        if risk_filter != "All Risks" and o["risk_level"] != risk_filter:
            continue
        filtered_orders.append(o)

    # Convert to Display DataFrame
    df_rows = []
    for o in filtered_orders:
        df_rows.append({
            "Order ID": o["order_id"],
            "Customer": o["customer"],
            "Order Type": o.get("order_type", "Standard"),
            "Current Stage": o["current_stage"],
            "Status": o["status"],
            "Elapsed Time": f"{o['elapsed_minutes']:.1f}m",
            "SLA Limit": f"{o['sla_threshold_minutes']:.1f}m",
            "Risk Level": o["risk_level"],
            "Latest Event": o.get("latest_event", "N/A"),
            "Recommended Next Action": o.get("recommended_next_action", "N/A")
        })

    df_display = pd.DataFrame(df_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # Digital Twin Inspector
    st.markdown("### 🔬 Order Digital Twin Inspector")
    available_ids = [o["order_id"] for o in filtered_orders] or list(orders_dict.keys())
    default_idx = available_ids.index(st.session_state.selected_order_id) if st.session_state.selected_order_id in available_ids else 0

    selected_oid = st.selectbox("Select Order to inspect unified state:", available_ids, index=default_idx)
    st.session_state.selected_order_id = selected_oid
    sel_order = orders_dict[selected_oid]

    # Twin Overview Tiles
    dt_c1, dt_c2, dt_c3, dt_c4 = st.columns(4)
    dt_c1.metric("Order ID", sel_order["order_id"], delta=sel_order.get("order_type", "Standard"))
    dt_c2.metric("Current Stage", sel_order["current_stage"])
    dt_c3.metric("Elapsed / SLA Limit", f"{sel_order['elapsed_minutes']:.1f}m / {sel_order['sla_threshold_minutes']:.1f}m")
    dt_c4.metric("Risk Level", sel_order["risk_level"])

    # Two column inspector: Left = Timeline & Logs, Right = Evidence & Diagnosis
    twin_col1, twin_col2 = st.columns([1.1, 0.9])

    with twin_col1:
        st.markdown("#### 📜 Event Timeline")
        for ev in reversed(sel_order["events"]):
            st_badge = {
                "SUCCESS": "badge-success",
                "WARNING": "badge-warning",
                "ERROR": "badge-danger",
                "PENDING": "badge-info"
            }.get(ev.get("status", "SUCCESS"), "badge-neutral")

            st.markdown(f"""
            <div class="timeline-node">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #0f172a;">{ev['event_name']}</strong>
                    <span style="font-size: 0.78rem; color: #64748b;">{ev['timestamp']}</span>
                </div>
                <div style="margin-top: 2px;">
                    <span class="badge {st_badge}">{ev.get('stage', 'Stage')}</span>
                    <span style="font-size: 0.85rem; color: #334155; margin-left: 6px;">{ev['detail']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📡 Simulated API Telemetry Logs")
        api_logs = sel_order.get("simulated_api_logs", [])
        if api_logs:
            for log in api_logs:
                log_color = {
                    "INFO": "#0284c7",
                    "WARN": "#d97706",
                    "ERROR": "#dc2626",
                    "CRITICAL": "#7c3aed"
                }.get(log.get("log_level", "INFO"), "#475569")

                st.markdown(f"""
                <div style="background: #ffffff; border-left: 4px solid {log_color}; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b;">
                        <span>{log['timestamp']} • <strong>{log['method']}</strong> {log['endpoint']}</span>
                        <span>HTTP {log.get('status_code', 'TIMEOUT')} • {log.get('latency_ms', 0)}ms</span>
                    </div>
                    <div style="font-family: monospace; font-size: 0.82rem; color: #1e293b; margin-top: 4px;">
                        {log.get('message', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No API telemetry events recorded for this order.")

    with twin_col2:
        st.markdown("#### 🔍 Evidence-Based Root Cause Diagnosis")
        diag = analyze_root_cause(sel_order)

        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px;">
            <div style="font-size: 0.82rem; text-transform: uppercase; color: #64748b; font-weight: 600;">Likely Cause</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 2px;">{diag['likely_cause']}</div>
            
            <div style="margin-top: 12px; font-weight: 600; font-size: 0.88rem; color: #334155;">Supporting Evidence:</div>
            <ul style="margin-top: 4px; padding-left: 20px; font-size: 0.85rem; color: #475569;">
                {''.join([f"<li>{ev}</li>" for ev in diag['supporting_evidence']])}
            </ul>

            <div style="margin-top: 10px; font-weight: 600; font-size: 0.88rem; color: #334155;">Missing Evidence:</div>
            <ul style="margin-top: 4px; padding-left: 20px; font-size: 0.85rem; color: #475569;">
                {''.join([f"<li>{ev}</li>" for ev in diag['missing_evidence']])}
            </ul>

            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #e2e8f0;">
                <div style="font-size: 0.82rem; color: #64748b;">Confidence Rating:</div>
                <div style="font-weight: 600; color: #0284c7;">{diag['confidence_label']}</div>
            </div>

            <div style="margin-top: 10px;">
                <div style="font-size: 0.82rem; color: #64748b;">Rule Applied:</div>
                <div style="font-size: 0.8rem; color: #334155; background: #f8fafc; padding: 6px; border-radius: 4px;">{diag['rule_rationale']}</div>
            </div>

            <div style="margin-top: 10px;">
                <div style="font-size: 0.82rem; color: #64748b;">Recommended Next Action:</div>
                <div style="font-size: 0.88rem; font-weight: 600; color: #b45309;">{diag['recommended_next_action']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🛡️ Downstream State & Safety Matrix")
        d_ev = sel_order.get("downstream_evidence", {})
        st.json(d_ev)


# =========================================================
# TAB 3: SAFETY GATES & EDGE-CASE LAB
# =========================================================
with tab_edge:
    st.markdown("### 🔬 Safety Gate & Edge-Case Testing Lab")
    st.markdown("""
    This interactive lab allows hackathon judges to verify the **4 strict safety gates** and test boundary edge cases:
    - **Test D:** What if duplicate protection fails (e.g. replay attack or key reused)?
    - **Test E:** What if the retry budget limit has been reached?
    - **Policy Gate:** What if policy forbids automatic recovery?
    """)

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    edge_col1, edge_col2 = st.columns([1, 1.2])

    with edge_col1:
        st.markdown("#### ⚙️ Configure Edge-Case Parameters")
        target_oid = st.selectbox("Select Target Order for Edge Test:", list(orders_dict.keys()), key="edge_oid")
        target_order = copy.deepcopy(orders_dict[target_oid])

        gate1_verified = st.toggle("Gate 1: Downstream Failure Conclusively Verified?", value=True)
        gate2_dup_pass = st.toggle("Gate 2: Duplicate Protection / Idempotency Valid?", value=True, help="Toggle to False to simulate Test D: Duplicate Key Conflict")
        gate3_retries = st.slider("Gate 3: Current Retry Count (Max = 2)", min_value=0, max_value=3, value=0, help="Set to 2 or 3 to simulate Test E: Retry Budget Exhausted")
        gate4_policy = st.toggle("Gate 4: Recovery Policy Authorizes Action?", value=True)

        evaluate_edge = st.button("🚀 Evaluate Safety Gates Live", use_container_width=True, type="primary")

    with edge_col2:
        st.markdown("#### 📊 Live Sentinel Safety Evaluation")
        
        # Run test
        edge_result = check_retry_safety(
            order=target_order,
            failure_verified=gate1_verified,
            duplicate_protection_passed=gate2_dup_pass,
            retry_count=gate3_retries,
            max_retries=2,
            policy_permits=gate4_policy
        )

        if edge_result["all_passed"]:
            st.markdown(f"""
            <div class="decision-banner-safe">
                <div style="font-size: 1.2rem; font-weight: 700; color: #065f46;">
                    ✅ {edge_result['status_label']}
                </div>
                <div style="font-size: 0.9rem; color: #047857; margin-top: 4px;">
                    {edge_result['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif not gate1_verified:
            st.markdown(f"""
            <div class="decision-banner-review">
                <div style="font-size: 1.2rem; font-weight: 700; color: #581c87;">
                    🛑 {edge_result['status_label']}
                </div>
                <div style="font-size: 0.9rem; color: #6b21a8; margin-top: 4px;">
                    {edge_result['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="decision-banner-blocked">
                <div style="font-size: 1.2rem; font-weight: 700; color: #991b1b;">
                    🛑 {edge_result['status_label']}
                </div>
                <div style="font-size: 0.9rem; color: #b91c1c; margin-top: 4px;">
                    {edge_result['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### Detailed Gate Breakdown:")
        for key, g in edge_result["checks_matrix"].items():
            icon = "✅" if g["passed"] else "❌"
            badge_cls = "badge-success" if g["passed"] else "badge-danger"
            st.markdown(f"""
            <div class="gate-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{icon} {g['name']}</strong>
                    <span class="badge {badge_cls}">{g['status']}</span>
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px;">{g['detail']}</div>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# TAB 4: IMMUTABLE AUDIT TRAIL
# =========================================================
with tab_audit:
    st.markdown("### 📜 Immutable Audit Trail")
    st.markdown("""
    Every diagnostic deduction, safety gate evaluation, and simulated recovery action is permanently recorded
    in the session audit trail to ensure 100% enterprise accountability.
    """)

    audit_records = st.session_state.audit_log

    # Audit Filter
    aud_col1, aud_col2 = st.columns([1.5, 1])
    with aud_col1:
        aud_search = st.text_input("Filter audit trail by Order ID or Keyword:", placeholder="e.g. ORD-8041, RETRY_PERMITTED")
    with aud_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        df_audit = pd.DataFrame(audit_records)
        csv_data = df_audit.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Trail (CSV)",
            data=csv_data,
            file_name=f"orderflow_sentinel_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Filter records
    filtered_audit = []
    for r in audit_records:
        if aud_search:
            q = aud_search.lower()
            match = (
                q in r["order_id"].lower() or
                q in r["scenario"].lower() or
                q in r["safety_decision"].lower() or
                q in r["reason"].lower()
            )
            if not match:
                continue
        filtered_audit.append(r)

    st.markdown(f"**Displaying {len(filtered_audit)} audit event records:**")
    st.dataframe(pd.DataFrame(filtered_audit), use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">
        ℹ️ <strong>System Architecture Note:</strong> For this hackathon prototype, the audit trail is maintained in session memory and can be exported as CSV. In production, this ledger streams to an append-only distributed event bus (Kafka/Kinesis) and an immutable data lake.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# TAB 5: PRESENTATION & ARCHITECTURE GUIDE
# =========================================================
with tab_guide:
    st.markdown("### 🎓 Virtusa Hackathon Presentation & Architecture Guide")
    st.markdown("Use this section to confidently explain OrderFlow Sentinel to hackathon judges.")

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown("#### 🏛️ The Four Core Capabilities")
        st.markdown("""
        1. **Order Digital Twin:**
           - A unified, real-time representation of an order's lifecycle, stages, events, API telemetry, and expected next step across disconnected enterprise systems.
        2. **Predictive SLA Alerts:**
           - Proactively catches stalled orders before contractual SLA breach using deterministic stage-time threshold monitoring (`elapsed_time > stage_limit`).
        3. **Evidence-Based Root Cause:**
           - Eliminates guesswork by inspecting telemetry logs and downstream reconciliation records to verify *why* a failure occurred.
        4. **Risk-Based Safe Auto-Healing:**
           - Enforces strict safety gates. Auto-retry is permitted *only* when failure is proven, duplicate protection passes, retry budget remains, and policy approves.
        """)

        st.markdown("#### ⭐ The Key Differentiator: *Prove Before You Retry*")
        st.markdown("""
        In distributed enterprise architectures, an **API Timeout (HTTP 504) does NOT mean failure**.
        - The request may have reached the bank switch and charged the customer before the response connection dropped.
        - Blindly retrying can cause **double-charging** or **double inventory depletion**.
        - OrderFlow Sentinel *proves* non-execution via downstream reconciliation ledger before authorizing any retry. If ambiguous, it enforces **Human Review Required**.
        """)

    with p_col2:
        st.markdown("#### 🎤 2-Minute Judge Pitch Script")
        st.markdown("""
        > *"Good morning judges! We are presenting **OrderFlow Sentinel — Predict, Explain, Recover Safely**.*
        >
        > *In modern enterprise commerce, orders traverse dozens of microservices, payment gateways, and warehouse systems. When an API call times out, systems traditionally do one of two bad things: they fail silently, or they blindly retry—risking duplicate charges and inventory chaos.*
        >
        > *OrderFlow Sentinel introduces our golden rule: **'Prove Before You Retry'**.*
        >
        > *1. In **Scenario 1**, an API timeout occurs, but our sentinel queries the downstream ledger, verifies zero fund locks, checks duplicate protection, and safely auto-recovers the order.*
        > *2. In **Scenario 2**, our deterministic SLA engine detects an order stalling in the warehouse, explains the RF terminal disconnect root cause, and alerts operations.*
        > *3. In **Scenario 3**, when downstream state is ambiguous, Sentinel **blocks the blind retry** and triggers **Human Review Required** to protect business assets.*
        >
        > *Everything is tracked in an immutable audit trail for full compliance."*
        """)

        st.markdown("#### 🔬 What is Implemented vs. Simulated")
        st.markdown("""
        - **Implemented:** Full diagnostic rule engine, 4-gate safety logic, deterministic SLA calculation, session state management, interactive operator controls, and CSV audit export.
        - **Simulated:** Downstream banking API switches, warehouse RF scanner networks, and external database partitions (to enable standalone, zero-dependency, safe local & cloud deployment).
        """)

st.markdown("<hr style='margin: 24px 0 12px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; font-size: 0.82rem; color: #94a3b8;">
    OrderFlow Sentinel • Virtusa Hackathon Solution • Predict. Explain. Recover Safely.
</div>
""", unsafe_allow_html=True)
