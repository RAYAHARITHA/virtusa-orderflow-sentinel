"""
OrderFlow Sentinel — Predict delays. Understand problems. Recover safely.
Virtusa Hackathon Prototype — Use Case 1: OrderFlow Sentinel
Built with Python, Streamlit, and Pandas.
"""

import copy
import streamlit as st
import pandas as pd
from datetime import datetime

# Import data and engine logic
from data import get_initial_orders, get_initial_audit_log
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
# Page Configuration & Clean Visual Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="OrderFlow Sentinel | Predict. Explain. Recover Safely.",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Enterprise CSS: High-contrast, clean cards, clear typography
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Top Header */
    .sentinel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .sentinel-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f2942;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sentinel-subtitle {
        font-size: 0.95rem;
        color: #475569;
        margin-top: 3px;
        font-weight: 500;
    }
    .demo-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .demo-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f2942;
        margin-top: 24px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Summary Cards */
    .summary-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .summary-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .summary-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0f2942;
        margin-top: 2px;
    }
    .summary-sub {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Selected Order Callout */
    .selected-order-banner {
        background: #ffffff;
        border-left: 5px solid #0d9488;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
    }

    /* Scenario Action Cards */
    .scenario-action-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 200px;
    }
    .card-teal {
        border-top: 4px solid #0d9488;
    }
    .card-orange {
        border-top: 4px solid #d97706;
    }
    .card-red {
        border-top: 4px solid #dc2626;
    }
    .scenario-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f2942;
        margin-bottom: 4px;
    }
    .scenario-question {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 6px;
    }
    .scenario-desc {
        font-size: 0.86rem;
        color: #64748b;
        line-height: 1.4;
        margin-bottom: 16px;
        flex-grow: 1;
    }

    /* Prominent Result Section */
    .result-container {
        background: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 12px;
        padding: 24px;
        margin-top: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 18px;
    }
    .result-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f2942;
    }

    /* Decision Badges */
    .badge-decision-green {
        background: #ecfdf5;
        color: #065f46;
        border: 2px solid #0d9488;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        display: inline-block;
    }
    .badge-decision-orange {
        background: #fffbeb;
        color: #92400e;
        border: 2px solid #d97706;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        display: inline-block;
    }
    .badge-decision-red {
        background: #fef2f2;
        color: #991b1b;
        border: 2px solid #dc2626;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 0.3px;
        display: inline-block;
    }

    /* Comparison Cards */
    .compare-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        height: 100%;
    }
    .compare-header {
        font-size: 0.92rem;
        font-weight: 700;
        color: #0f2942;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 6px;
        margin-bottom: 10px;
    }
    .compare-label {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        margin-top: 8px;
    }
    .compare-value {
        font-size: 0.9rem;
        font-weight: 600;
        color: #0f172a;
        margin-top: 1px;
    }

    /* Answers Box */
    .answers-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 18px;
        margin-top: 14px;
    }
    .answer-item-title {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569;
        margin-top: 10px;
        letter-spacing: 0.3px;
    }
    .answer-item-content {
        font-size: 0.9rem;
        color: #1e293b;
        margin-top: 2px;
        line-height: 1.45;
    }

    /* Journey Tracker */
    .journey-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .journey-steps-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
        margin-bottom: 14px;
    }
    .journey-node {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 18px;
        font-size: 0.84rem;
        font-weight: 600;
    }
    .node-completed {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .node-current {
        background: #eff6ff;
        color: #1e40af;
        border: 2px solid #3b82f6;
    }
    .node-delayed {
        background: #fffbeb;
        color: #92400e;
        border: 2px solid #d97706;
    }
    .node-blocked {
        background: #fef2f2;
        color: #991b1b;
        border: 2px solid #dc2626;
    }
    .node-pending {
        background: #f1f5f9;
        color: #64748b;
        border: 1px solid #cbd5e1;
    }
    .node-arrow {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 700;
    }
    .journey-legend {
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 0.78rem;
        color: #64748b;
        border-top: 1px solid #f1f5f9;
        padding-top: 10px;
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

if "selected_order_id" not in st.session_state:
    st.session_state.selected_order_id = "ORD-8041"

if "active_scenario_result" not in st.session_state:
    # Initialize with default API Timeout scenario pre-loaded so judges immediately see the rich layout!
    st.session_state.active_scenario_result = run_api_timeout_scenario(
        orders=st.session_state.orders,
        audit_log=st.session_state.audit_log,
        executed_idemp_keys=st.session_state.executed_idemp_keys
    )

def reset_entire_demo():
    """Restores initial state for fresh demonstration."""
    st.session_state.orders = get_initial_orders()
    st.session_state.audit_log = get_initial_audit_log()
    st.session_state.executed_idemp_keys = set()
    st.session_state.selected_order_id = "ORD-8041"
    st.session_state.active_scenario_result = None

# =========================================================
# A. HEADER
# =========================================================
st.markdown("""
<div class="sentinel-header">
    <div>
        <div class="sentinel-title">🛡️ OrderFlow Sentinel</div>
        <div class="sentinel-subtitle">Predict delays. Understand problems. Recover safely.</div>
    </div>
    <div>
        <div class="demo-badge">
            <span class="demo-dot"></span> Demo Mode — Sample Data Only
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# B. SUMMARY (3 Summary Cards Calculated from Actual Data)
# =========================================================
orders_dict = st.session_state.orders
total_orders = len(orders_dict)
in_progress_count = sum(1 for o in orders_dict.values() if o["status_code"] in ["IN_PROGRESS", "API_TIMEOUT", "API_ERROR", "SLA_RISK", "UNCERTAIN_TIMEOUT", "RETRY_PERMITTED"])
attention_count = sum(1 for o in orders_dict.values() if o["status_code"] in ["API_TIMEOUT", "API_ERROR", "SLA_RISK", "UNCERTAIN_TIMEOUT", "HUMAN_REVIEW_REQUIRED", "RETRY_BLOCKED"])

sum_col1, sum_col2, sum_col3 = st.columns(3)

with sum_col1:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-label">Total Orders Monitored</div>
        <div class="summary-value">{total_orders}</div>
        <div class="summary-sub">Synthetic B2B fleet orders</div>
    </div>
    """, unsafe_allow_html=True)

with sum_col2:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-label">Orders In Progress</div>
        <div class="summary-value" style="color: #0284c7;">{in_progress_count}</div>
        <div class="summary-sub">Actively moving through lifecycle</div>
    </div>
    """, unsafe_allow_html=True)

with sum_col3:
    st.markdown(f"""
    <div class="summary-card">
        <div class="summary-label">Orders Needing Attention</div>
        <div class="summary-value" style="color: #d97706;">{attention_count}</div>
        <div class="summary-sub">SLA breaches, timeouts & reviews</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# C. ORDER EXPLORER (Searchable & Selectable Table)
# =========================================================
st.markdown('<div class="section-title">📦 Order Explorer</div>', unsafe_allow_html=True)

# Filter / Search controls
exp_c1, exp_c2 = st.columns([1.5, 1])
with exp_c1:
    search_query = st.text_input("🔍 Search orders by Order ID, customer, or stage:", placeholder="e.g. ORD-8041, Acme, Fulfilment")
with exp_c2:
    status_filter = st.selectbox("Filter by Status:", ["All Statuses"] + sorted(list({o["status"] for o in orders_dict.values()})))

# Filtered list
filtered_oids = []
for oid, o in orders_dict.items():
    if search_query:
        q = search_query.lower()
        if q not in oid.lower() and q not in o["customer"].lower() and q not in o["current_stage"].lower():
            continue
    if status_filter != "All Statuses" and o["status"] != status_filter:
        continue
    filtered_oids.append(oid)

if not filtered_oids:
    filtered_oids = list(orders_dict.keys())

# Build Display Table
table_rows = []
for oid in filtered_oids:
    o = orders_dict[oid]
    table_rows.append({
        "Order ID": o["order_id"],
        "Customer": o["customer"],
        "Current Stage": o["current_stage"],
        "Status": o["status"],
        "Time in Stage": f"{o['elapsed_minutes']:.1f} mins",
        "SLA Limit": f"{o['sla_threshold_minutes']:.1f} mins",
        "Risk Level": o["risk_level"],
        "Next Recommended Action": o.get("recommended_next_action", "Monitor")
    })

df_orders = pd.DataFrame(table_rows)
st.dataframe(df_orders, use_container_width=True, hide_index=True)

# Order Selector
sel_col1, sel_col2 = st.columns([1.2, 2.8])
with sel_col1:
    available_choices = filtered_oids
    default_idx = available_choices.index(st.session_state.selected_order_id) if st.session_state.selected_order_id in available_choices else 0
    chosen_order_id = st.selectbox(
        "Select an order to inspect its journey & details:",
        available_choices,
        index=default_idx,
        key="order_selector"
    )
    if chosen_order_id != st.session_state.selected_order_id:
        st.session_state.selected_order_id = chosen_order_id
        st.rerun()

current_order = orders_dict[st.session_state.selected_order_id]

# Visually obvious selected order banner
with sel_col2:
    st.markdown(f"""
    <div class="selected-order-banner">
        <div>
            <span style="font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase;">Viewing Order</span>
            <div style="font-size: 1.15rem; font-weight: 800; color: #0f2942;">{current_order['order_id']} — {current_order['customer']}</div>
            <div style="font-size: 0.85rem; color: #475569;">Item: {current_order.get('item_summary', 'B2B Equipment')} | Value: <strong>${current_order.get('amount', 0):,.2f}</strong></div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.82rem; color: #64748b;">Stage: <strong>{current_order['current_stage']}</strong></div>
            <div style="font-size: 0.82rem; color: #0f2942;">Status: <strong>{current_order['status']}</strong> ({current_order['elapsed_minutes']:.1f}m spent)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# D. ORDER JOURNEY (Visual Lifecycle & Legend)
# =========================================================
st.markdown('<div class="section-title">🗺️ Order Journey</div>', unsafe_allow_html=True)

lifecycle_stages = [
    "Order Created",
    "Payment Confirmed",
    "Inventory Reserved",
    "Fulfilment Started",
    "Shipment Confirmed",
    "Completed"
]

stage_map = {
    "Order Created": 0,
    "Payment Confirmed": 1,
    "Inventory Reserved": 2,
    "Fulfilment Started": 3,
    "Shipment Requested": 3,
    "Shipment Confirmed": 4,
    "Order Completed": 5,
    "Completed": 5
}

current_stage_idx = stage_map.get(current_order.get("current_stage"), 0)
order_status_code = current_order.get("status_code", "IN_PROGRESS")
order_risk = current_order.get("risk_level", "Normal")

step_html_list = []
for idx, s_name in enumerate(lifecycle_stages):
    if idx < current_stage_idx:
        icon = "✅"
        cls = "node-completed"
    elif idx == current_stage_idx:
        if "SLA Risk" in order_risk or order_status_code == "SLA_RISK":
            icon = "⚠️"
            cls = "node-delayed"
        elif order_status_code in ["HUMAN_REVIEW_REQUIRED", "RETRY_BLOCKED"]:
            icon = "❌"
            cls = "node-blocked"
        elif order_status_code in ["API_TIMEOUT", "API_ERROR"]:
            icon = "⚠️"
            cls = "node-delayed"
        else:
            icon = "🔵"
            cls = "node-current"
    else:
        icon = "⚪"
        cls = "node-pending"

    step_html_list.append(f'<span class="journey-node {cls}">{icon} {s_name}</span>')

journey_string = ' <span class="node-arrow">➔</span> '.join(step_html_list)

st.markdown(f"""
<div class="journey-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #0f2942; text-transform: uppercase;">
            Lifecycle Progress for {current_order['order_id']}
        </span>
        <span style="font-size: 0.8rem; color: #64748b;">
            Current Stage: <strong>{current_order['current_stage']}</strong>
        </span>
    </div>
    <div class="journey-steps-row">
        {journey_string}
    </div>
    <div class="journey-legend">
        <span><strong>Legend:</strong></span>
        <span>✅ Completed stage</span>
        <span>🔵 Current normal stage</span>
        <span>⚠️ Delayed / Warning stage</span>
        <span>❌ Blocked / Review stage</span>
        <span>⚪ Pending future stage</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# E. THREE INTERACTIVE SCENARIOS
# =========================================================
st.markdown('<div class="section-title">🎯 Three Interactive Scenarios</div>', unsafe_allow_html=True)
st.markdown("<div style='font-size: 0.88rem; color: #475569; margin-bottom: 12px;'>Click any scenario button below to simulate an event and evaluate Sentinel's recovery safety logic:</div>", unsafe_allow_html=True)

card_col1, card_col2, card_col3 = st.columns(3)

with card_col1:
    st.markdown("""
    <div class="scenario-action-card card-teal">
        <div>
            <div class="scenario-name">API Timeout</div>
            <div class="scenario-question">Can we retry safely?</div>
            <div class="scenario-desc">The system did not receive a reply from the next service.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Run API Timeout Demo", key="btn_run_timeout", use_container_width=True, type="primary"):
        res = run_api_timeout_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log,
            executed_idemp_keys=st.session_state.executed_idemp_keys
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8041"
        st.rerun()

with card_col2:
    st.markdown("""
    <div class="scenario-action-card card-orange">
        <div>
            <div class="scenario-name">Delayed Order</div>
            <div class="scenario-question">Is this order taking too long?</div>
            <div class="scenario-desc">The order has taken longer than expected in fulfilment.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Run Delayed Order Demo", key="btn_run_delayed", use_container_width=True):
        res = run_delayed_order_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8042"
        st.rerun()

with card_col3:
    st.markdown("""
    <div class="scenario-action-card card-red">
        <div>
            <div class="scenario-name">Uncertain Outcome</div>
            <div class="scenario-question">Could retrying create a duplicate?</div>
            <div class="scenario-desc">The request timed out, and the final result is unknown.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Run Uncertain Outcome Demo", key="btn_run_uncertain", use_container_width=True):
        res = run_uncertain_outcome_scenario(
            orders=st.session_state.orders,
            audit_log=st.session_state.audit_log,
            executed_idemp_keys=st.session_state.executed_idemp_keys
        )
        st.session_state.active_scenario_result = res
        st.session_state.selected_order_id = "ORD-8043"
        st.rerun()

# =========================================================
# F. SCENARIO RESULT (Most Prominent Section)
# =========================================================
active_res = st.session_state.active_scenario_result

if active_res is not None:
    scenario_name = active_res["scenario_name"]
    res_details = active_res["result_details"]
    before = active_res["before_state"]
    after = active_res["after_state"]

    decision_badge_style = {
        "green": "badge-decision-green",
        "orange": "badge-decision-orange",
        "red": "badge-decision-red"
    }.get(res_details.get("decision_color", "green"), "badge-decision-green")

    st.markdown('<div class="result-container">', unsafe_allow_html=True)

    # Top result header
    res_h1, res_h2, res_h3 = st.columns([1.6, 1.4, 0.6])
    with res_h1:
        st.markdown(f'<div class="result-title">Scenario Result: {scenario_name}</div>', unsafe_allow_html=True)
    with res_h2:
        st.markdown(f'<div class="{decision_badge_style}">{res_details["decision_badge"]}</div>', unsafe_allow_html=True)
    with res_h3:
        if st.button("Reset Demo", key="btn_reset_center", use_container_width=True, help="Reset demo to initial sample state"):
            reset_entire_demo()
            st.toast("Demo state reset to initial baseline.", icon="🔄")
            st.rerun()

    # Before & After comparison cards
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    cmp_col1, cmp_col2 = st.columns(2)

    with cmp_col1:
        st.markdown(f"""
        <div class="compare-card">
            <div class="compare-header">Before (Order Status)</div>
            <div class="compare-label">Order ID</div>
            <div class="compare-value">{before['order_id']}</div>
            <div class="compare-label">Previous Stage</div>
            <div class="compare-value">{before['stage']}</div>
            <div class="compare-label">Previous Status</div>
            <div class="compare-value">{before['status']}</div>
            <div class="compare-label">What was waiting or delayed</div>
            <div class="compare-value" style="color: #475569; font-size: 0.86rem; font-weight: 500;">{before['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    with cmp_col2:
        st.markdown(f"""
        <div class="compare-card">
            <div class="compare-header">After (Order Status)</div>
            <div class="compare-label">Order ID</div>
            <div class="compare-value">{after['order_id']}</div>
            <div class="compare-label">Updated Stage</div>
            <div class="compare-value">{after['stage']}</div>
            <div class="compare-label">Updated Status</div>
            <div class="compare-value">{after['status']}</div>
            <div class="compare-label">What changed</div>
            <div class="compare-value" style="color: #475569; font-size: 0.86rem; font-weight: 500;">{after['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Six core plain-English answers
    st.markdown(f"""
    <div class="answers-box">
        <div class="answer-item-title">1. What happened?</div>
        <div class="answer-item-content">{res_details['what_happened']}</div>
        
        <div class="answer-item-title">2. Why did it happen?</div>
        <div class="answer-item-content">{res_details['why_it_happened']}</div>
        
        <div class="answer-item-title">3. What did the system check?</div>
        <div class="answer-item-content">{res_details['what_checked']}</div>
        
        <div class="answer-item-title">4. Decision</div>
        <div style="margin-top: 4px; margin-bottom: 6px;">
            <span class="{decision_badge_style}" style="font-size: 0.85rem; padding: 4px 12px;">{res_details['decision_badge']}</span>
        </div>
        
        <div class="answer-item-title">5. What changed?</div>
        <div class="answer-item-content">{res_details['what_changed']}</div>
        
        <div class="answer-item-title">6. What should happen next?</div>
        <div class="answer-item-content" style="font-weight: 600; color: #0f2942;">{res_details['next_step']}</div>
    </div>
    """, unsafe_allow_html=True)

    # In Scenario 3, provide simulated human operator resolution options
    if scenario_name == "Uncertain Outcome":
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #0f2942; text-transform: uppercase;'>Simulate Human Operator Action:</div>", unsafe_allow_html=True)
        op_col1, op_col2 = st.columns(2)
        with op_col1:
            if st.button("🤝 Verify Committed (Safe to Proceed)", key="btn_op_commit", use_container_width=True):
                run_operator_resolution(
                    orders=st.session_state.orders,
                    audit_log=st.session_state.audit_log,
                    order_id="ORD-8043",
                    resolution_type="VERIFIED_COMMITTED",
                    executed_idemp_keys=st.session_state.executed_idemp_keys
                )
                st.toast("Operator confirmed transaction was recorded downstream! Order unlocked.", icon="✅")
                st.rerun()
        with op_col2:
            if st.button("🔄 Verify Void & Safe Retry", key="btn_op_retry", use_container_width=True):
                run_operator_resolution(
                    orders=st.session_state.orders,
                    audit_log=st.session_state.audit_log,
                    order_id="ORD-8043",
                    resolution_type="VERIFIED_FAILED_RETRY",
                    executed_idemp_keys=st.session_state.executed_idemp_keys
                )
                st.toast("Operator confirmed void and authorized controlled retry!", icon="🔄")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# G. ADVANCED DETAILS (Expandable Sections at Bottom)
# =========================================================
st.markdown('<div class="section-title">⚙️ Advanced Details</div>', unsafe_allow_html=True)

# Expander 1: Technical Evidence
with st.expander("View Technical Evidence"):
    st.markdown("##### Downstream Reconciliation & Root-Cause Evidence")
    active_eval_order = active_res["order"] if active_res else current_order
    diag_info = analyze_root_cause(active_eval_order)
    
    ev_c1, ev_c2 = st.columns(2)
    with ev_c1:
        st.markdown(f"**Likely Root Cause:** `{diag_info['likely_cause']}`")
        st.markdown(f"**Confidence Level:** `{diag_info['confidence_label']}`")
        st.markdown("**Supporting Evidence:**")
        for ev_line in diag_info.get("supporting_evidence", []):
            st.markdown(f"- {ev_line}")
    with ev_c2:
        st.markdown("**Downstream Ledger Verification Details:**")
        st.json(active_eval_order.get("downstream_evidence", {}))

# Expander 2: Safety Checks
with st.expander("View Safety Checks"):
    st.markdown("##### 4-Gate Safety Checklist (“Prove Before You Retry”)")
    active_eval_order = active_res["order"] if active_res else current_order
    safety_eval = check_retry_safety(active_eval_order, executed_idemp_keys=st.session_state.executed_idemp_keys)
    
    chk_c1, chk_c2, chk_c3, chk_c4 = st.columns(4)
    chk_matrix = safety_eval["checks_matrix"]
    
    with chk_c1:
        st.markdown(f"**Gate 1: Failure Verified**")
        st.markdown(f"Status: `{'PASS ✅' if chk_matrix['failure_verified']['passed'] else 'FAIL ❌'}`")
        st.caption(chk_matrix['failure_verified']['detail'])
    with chk_c2:
        st.markdown(f"**Gate 2: Duplicate Check**")
        st.markdown(f"Status: `{'PASS ✅' if chk_matrix['duplicate_protection']['passed'] else 'FAIL ❌'}`")
        st.caption(chk_matrix['duplicate_protection']['detail'])
    with chk_c3:
        st.markdown(f"**Gate 3: Retry Budget**")
        st.markdown(f"Status: `{'PASS ✅' if chk_matrix['retry_budget']['passed'] else 'FAIL ❌'}`")
        st.caption(chk_matrix['retry_budget']['detail'])
    with chk_c4:
        st.markdown(f"**Gate 4: Recovery Policy**")
        st.markdown(f"Status: `{'PASS ✅' if chk_matrix['policy_permits']['passed'] else 'FAIL ❌'}`")
        st.caption(chk_matrix['policy_permits']['detail'])

# Expander 3: API Simulation
with st.expander("View API Simulation"):
    st.markdown("##### Simulated API Telemetry & Payload Logs")
    active_eval_order = active_res["order"] if active_res else current_order
    sim_logs = active_eval_order.get("simulated_api_logs", [])
    if sim_logs:
        for sl in sim_logs:
            st.code(
                f"[{sl.get('timestamp')}] {sl.get('method')} {sl.get('endpoint')}\n"
                f"HTTP {sl.get('status_code', 'TIMEOUT')} | Latency: {sl.get('latency_ms', 0)}ms | Level: {sl.get('log_level', 'INFO')}\n"
                f"{sl.get('message', '')}",
                language="http"
            )
    else:
        st.info("No API logs recorded for this order.")

# Expander 4: Audit Trail
with st.expander("View Audit Trail"):
    st.markdown("##### Session Decision & Action Audit Records")
    aud_df = pd.DataFrame(st.session_state.audit_log)
    st.dataframe(aud_df, use_container_width=True, hide_index=True)
    
    aud_col_left, aud_col_right = st.columns([1, 1])
    with aud_col_left:
        csv_bytes = aud_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Audit Trail (CSV)",
            data=csv_bytes,
            file_name=f"orderflow_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    with aud_col_right:
        if st.button("Reset Entire Demo State", key="btn_reset_bottom", help="Restores fresh baseline data"):
            reset_entire_demo()
            st.toast("Demo state reset to initial baseline.", icon="🔄")
            st.rerun()

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("<hr style='margin: 24px 0 10px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #94a3b8; flex-wrap: wrap;">
    <div>OrderFlow Sentinel • Virtusa Hackathon Prototype • Predict. Explain. Recover Safely.</div>
    <div>All orders, telemetry, and actions are simulated for demonstration.</div>
</div>
""", unsafe_allow_html=True)
