"""
OrderFlow Sentinel - Automated Verification Test Suite
Tests all 7 required conditions:
- Test A: Safe simulated retry for verified API timeout
- Test B: SLA risk alert on delayed order exceeding threshold
- Test C: Uncertain API outcome blocks retry and triggers HUMAN REVIEW REQUIRED
- Test D: Duplicate protection failing blocks retry
- Test E: Retry count at or above limit blocks retry
- Test F: Reset demo restores original synthetic data
- Test G: All three scenarios work in integrated state
"""

import copy
from data import get_initial_orders, get_initial_audit_log, get_stage_sla_limits
from engine import (
    calculate_sla_risk,
    analyze_root_cause,
    check_retry_safety,
    run_api_timeout_scenario,
    run_delayed_order_scenario,
    run_uncertain_outcome_scenario
)

def test_all():
    print("==================================================")
    print("ORDERFLOW SENTINEL - AUTOMATED TEST SUITE")
    print("==================================================")

    # 1. Test Baseline Data
    orders = get_initial_orders()
    audit_log = get_initial_audit_log()
    executed_keys = set()
    assert len(orders) >= 8, f"Expected >= 8 orders, got {len(orders)}"
    print("[PASS] Baseline: 8 synthetic orders loaded successfully.")

    # 2. Test A: Safe simulated retry when verified failure, duplicate protection passes, retry within limit
    print("\n--- Running Test A: Safe API Timeout Recovery ---")
    res_a = run_api_timeout_scenario(orders, audit_log, executed_keys)
    safety_a = res_a["safety_result"]
    assert safety_a["all_passed"] is True, "Test A expected all safety gates to pass"
    assert safety_a["decision"] == "RETRY_PERMITTED", f"Expected RETRY_PERMITTED, got {safety_a['decision']}"
    assert orders["ORD-8041"]["retry_count"] == 1, "Retry count should increment to 1"
    assert orders["ORD-8041"]["status"] == "Retry Permitted"
    assert "SAFE SIMULATED RETRY PERMITTED" in res_a["simulated_action_result"]["title"]
    print("[PASS] Test A Passed: Safe simulated retry permitted with all 4 safety gates passing.")

    # 3. Test B: Delayed order exceeding threshold displays SLA risk alert
    print("\n--- Running Test B: Delayed Order & SLA Alert ---")
    res_b = run_delayed_order_scenario(orders, audit_log)
    sla_b = res_b["sla_result"]
    assert sla_b["status"] == "CRITICAL_SLA_RISK", f"Expected CRITICAL_SLA_RISK, got {sla_b['status']}"
    assert sla_b["consumption_pct"] > 100.0, "Consumption percentage should exceed 100%"
    assert orders["ORD-8042"]["status"] == "SLA Risk"
    assert "SLA RISK DETECTED" in res_b["alert_title"]
    print(f"[PASS] Test B Passed: SLA Risk correctly detected ({sla_b['consumption_pct']:.0f}% consumed, +{sla_b['elapsed_minutes'] - sla_b['threshold_minutes']:.1f}m breach).")

    # 4. Test C: Uncertain API outcome blocks retry and triggers HUMAN REVIEW REQUIRED
    print("\n--- Running Test C: Uncertain API Outcome & Human Review ---")
    res_c = run_uncertain_outcome_scenario(orders, audit_log, executed_keys)
    safety_c = res_c["safety_result"]
    assert safety_c["all_passed"] is False, "Test C should fail all_passed check"
    assert safety_c["decision"] == "HUMAN_REVIEW_REQUIRED", f"Expected HUMAN_REVIEW_REQUIRED, got {safety_c['decision']}"
    assert orders["ORD-8043"]["status"] == "Human Review Required"
    assert "PROVE BEFORE YOU RETRY" in safety_c["reason"]
    print("[PASS] Test C Passed: Uncertain API outcome blocked retry and flagged 'HUMAN REVIEW REQUIRED'.")

    # 5. Test D: Duplicate protection failure blocks retry
    print("\n--- Running Test D: Duplicate Protection Gate Failure ---")
    mock_order = copy.deepcopy(orders["ORD-8041"])
    # Simulate duplicate key already in executed set
    test_d_keys = {"idemp-ord-8041-pay-v1"}
    safety_d = check_retry_safety(mock_order, executed_idemp_keys=test_d_keys)
    assert safety_d["all_passed"] is False, "Duplicate key should fail all_passed"
    assert safety_d["decision"] == "RETRY_BLOCKED", f"Expected RETRY_BLOCKED, got {safety_d['decision']}"
    assert safety_d["checks_matrix"]["duplicate_protection"]["passed"] is False
    print("[PASS] Test D Passed: Duplicate key correctly blocked from executing twice.")

    # 6. Test E: Retry count at or above limit blocks retry
    print("\n--- Running Test E: Retry Budget Exhaustion ---")
    mock_order_e = copy.deepcopy(orders["ORD-8041"])
    mock_order_e["retry_count"] = 2
    mock_order_e["max_retries"] = 2
    safety_e = check_retry_safety(mock_order_e, retry_count=2, max_retries=2)
    assert safety_e["all_passed"] is False, "Exhausted retry budget should fail all_passed"
    assert safety_e["decision"] == "RETRY_BLOCKED", f"Expected RETRY_BLOCKED, got {safety_e['decision']}"
    assert safety_e["checks_matrix"]["retry_budget"]["passed"] is False
    print("[PASS] Test E Passed: Retry count at limit (2/2) successfully blocked.")

    # 7. Test F: Reset demo restores original synthetic data
    print("\n--- Running Test F: Reset Demo State ---")
    orders_fresh = get_initial_orders()
    assert orders_fresh["ORD-8041"]["retry_count"] == 0, "Fresh state should have retry_count 0"
    assert orders_fresh["ORD-8041"]["status"] == "API Error", "Fresh state should have original status"
    assert orders_fresh["ORD-8042"]["status"] == "SLA Risk", "Fresh state should have original status"
    print("[PASS] Test F Passed: Reset restores fresh deep-copy of initial synthetic data.")

    # 8. Test G: All three scenarios work in the integrated state
    print("\n--- Running Test G: Integrated Scenarios in Single State ---")
    test_orders = get_initial_orders()
    test_audit = get_initial_audit_log()
    test_keys = set()

    initial_audit_len = len(test_audit)
    run_api_timeout_scenario(test_orders, test_audit, test_keys)
    run_delayed_order_scenario(test_orders, test_audit)
    run_uncertain_outcome_scenario(test_orders, test_audit, test_keys)

    assert len(test_audit) == initial_audit_len + 3, f"Expected 3 new audit entries, got {len(test_audit) - initial_audit_len}"
    assert test_orders["ORD-8041"]["status"] == "Retry Permitted"
    assert test_orders["ORD-8042"]["status"] == "SLA Risk"
    assert test_orders["ORD-8043"]["status"] == "Human Review Required"
    print("[PASS] Test G Passed: All 3 scenarios run seamlessly in one integrated session.")

    print("\n==================================================")
    print("ALL 7 TESTS PASSED SUCCESSFULLY! (100% PASS RATE)")
    print("==================================================")

if __name__ == "__main__":
    test_all()
