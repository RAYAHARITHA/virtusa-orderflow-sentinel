"""
OrderFlow Sentinel - Core Diagnostic, Safety, and Safe Recovery Engine
Implements:
1. Order Digital Twin unified state evaluation
2. Transparent rule-based SLA risk detection
3. Evidence-based root cause analysis
4. Risk-based safe recovery decision engine ("Prove Before You Retry")
5. Audit trail recording and interactive scenario execution
"""

from datetime import datetime

def calculate_sla_risk(order):
    """
    Evaluates elapsed stage time against configured threshold.
    Transparent rule-based risk detection without unverified ML claims.
    """
    elapsed = float(order.get("elapsed_minutes", 0.0))
    threshold = float(order.get("sla_threshold_minutes", 5.0))
    consumption_pct = (elapsed / threshold) * 100.0 if threshold > 0 else 0.0

    if consumption_pct > 100.0:
        overdue_mins = elapsed - threshold
        status = "CRITICAL_SLA_RISK"
        risk_level = "Critical SLA Risk"
        badge = "SLA RISK DETECTED"
        message = (
            f"SLA RISK DETECTED — this order has spent {elapsed:.1f}m in '{order.get('current_stage')}', "
            f"exceeding the configured threshold of {threshold:.1f}m by +{overdue_mins:.1f}m "
            f"({consumption_pct:.0f}% of SLA consumed)."
        )
        recommendation = "Investigate downstream subsystem queues, notify operations supervisor, and re-route task."
    elif consumption_pct >= 75.0:
        status = "APPROACHING_THRESHOLD"
        risk_level = "Medium"
        badge = "APPROACHING SLA"
        message = (
            f"APPROACHING SLA THRESHOLD — order has consumed {consumption_pct:.0f}% of stage SLA "
            f"({elapsed:.1f}m / {threshold:.1f}m)."
        )
        recommendation = "Monitor next event confirmation closely to prevent breach."
    else:
        status = "NORMAL"
        risk_level = "Normal"
        badge = "HEALTHY"
        message = (
            f"NORMAL EXECUTION — order stage time {elapsed:.1f}m is well within SLA threshold {threshold:.1f}m "
            f"({consumption_pct:.0f}% consumed)."
        )
        recommendation = "Routine pipeline monitoring active."

    return {
        "status": status,
        "risk_level": risk_level,
        "badge": badge,
        "elapsed_minutes": elapsed,
        "threshold_minutes": threshold,
        "consumption_pct": consumption_pct,
        "message": message,
        "recommendation": recommendation,
        "rule_applied": "Deterministic Stage Threshold Rule: elapsed_time > stage_sla_limit"
    }

def analyze_root_cause(order):
    """
    Analyzes synthetic order events, API telemetry logs, and downstream evidence.
    Returns transparent diagnostic reasoning, supporting evidence, and confidence rating.
    """
    evidence = order.get("downstream_evidence", {})
    api_logs = order.get("simulated_api_logs", [])
    order_id = order.get("order_id", "UNKNOWN")
    stage = order.get("current_stage", "UNKNOWN")

    # Check 1: Uncertain API Outcome (Ambiguous downstream state)
    if evidence.get("verification_status") == "FAILURE_UNVERIFIED" or evidence.get("transaction_found_in_ledger") == "UNKNOWN / AMBIGUOUS":
        return {
            "order_id": order_id,
            "likely_cause": "Uncertain API Outcome (Downstream State Ambiguous)",
            "category": "AMBIGUOUS_API_TIMEOUT",
            "supporting_evidence": [
                f"HTTP 504 Gateway Timeout observed during POST to downstream service: {order.get('downstream_service')}.",
                "Upstream socket closed mid-packet transfer; response body never received.",
                "Downstream reconciliation query returned HTTP 502 with status: 'INDETERMINATE / IN_PROGRESS'.",
                "Lock status is PARTIALLY_PROCESSED_OR_ORPHANED in distributed database."
            ],
            "missing_evidence": [
                "Definitive commit acknowledgment (ACK) or clean abort rollback from the downstream ledger.",
                "Valid bank/ledger transaction reference number."
            ],
            "confidence_label": "High Confidence in Uncertainty",
            "rule_rationale": (
                "Rule: When an API request times out and the downstream ledger state is indeterminate, "
                "the operation cannot be proven to have failed. A blind retry creates severe risk of double-mutation."
            ),
            "recommended_next_action": (
                "BLOCK AUTOMATIC RETRY. Require manual operator reconciliation against banking/ledger settlement portal."
            )
        }

    # Check 2: Verified API Failure (Safe for retry consideration)
    if evidence.get("verification_status") == "FAILURE_VERIFIED" or evidence.get("transaction_found_in_ledger") is False:
        return {
            "order_id": order_id,
            "likely_cause": "Network / Gateway Read Timeout (Verified Non-Execution)",
            "category": "VERIFIED_API_TIMEOUT",
            "supporting_evidence": [
                f"Client read timeout after 30,000ms on POST to {order.get('downstream_service')}.",
                "Downstream query to Central Reconciliation Ledger returned HTTP 404.",
                "Ledger report confirms: transaction_found=False, authorized=False, lock_acquired=False.",
                f"Idempotency key '{order.get('idempotency_key')}' is registered and verified uncommitted."
            ],
            "missing_evidence": [
                "None. Downstream non-existence is conclusively verified by reconciliation telemetry."
            ],
            "confidence_label": "High Confidence",
            "rule_rationale": (
                "Rule: Downstream ledger reconciliation conclusively proves the request was dropped before "
                "any mutation occurred. With duplicate protection active, a controlled retry is safe."
            ),
            "recommended_next_action": (
                "Permit a single controlled simulated retry using the original idempotency key with exponential backoff."
            )
        }

    # Check 3: SLA Delay / Missing Confirmation
    if order.get("status_code") == "SLA_RISK" or evidence.get("missing_event"):
        return {
            "order_id": order_id,
            "likely_cause": "Downstream Subsystem Backlog & Missing Confirmation",
            "category": "SLA_BREACH",
            "supporting_evidence": [
                f"Order elapsed time ({order.get('elapsed_minutes')}m) exceeds stage limit ({order.get('sla_threshold_minutes')}m).",
                f"Missing expected confirmation event: '{evidence.get('missing_event', 'CONFIRMATION_ACK')}'.",
                f"Downstream telemetry alert: {evidence.get('root_cause_indicator', 'Subsystem backlog detected')}."
            ],
            "missing_evidence": [
                f"Operator barcode scan confirmation from {order.get('downstream_service')}."
            ],
            "confidence_label": "High Confidence",
            "rule_rationale": (
                "Rule: Deterministic stage SLA exceeded by >100%. Handheld/worker telemetry shows subsystem disconnect."
            ),
            "recommended_next_action": (
                f"Issue immediate operations alert. {evidence.get('recommended_action', 'Re-route ticket to alternate queue.')}"
            )
        }

    # Check 4: Retry Limit Exceeded
    if order.get("retry_count", 0) >= order.get("max_retries", 2):
        return {
            "order_id": order_id,
            "likely_cause": "Configured Retry Limit Exhausted",
            "category": "RETRY_BUDGET_EXHAUSTED",
            "supporting_evidence": [
                f"Retry count ({order.get('retry_count')}) has reached configured maximum ({order.get('max_retries')}).",
                "Repeated upstream HTTP 503 Service Unavailable errors."
            ],
            "missing_evidence": ["Healthy downstream service endpoint."],
            "confidence_label": "High Confidence",
            "rule_rationale": "Safety policy forbids automatic retries once retry budget is consumed.",
            "recommended_next_action": "Escalate to engineering on-call and suspend automated pipeline for this order."
        }

    # Check 5: Healthy Order
    return {
        "order_id": order_id,
        "likely_cause": "Healthy Pipeline Progression",
        "category": "HEALTHY",
        "supporting_evidence": [
            f"All pipeline stages executing within configured SLA parameters.",
            f"Stage '{stage}' elapsed time ({order.get('elapsed_minutes')}m) is normal."
        ],
        "missing_evidence": ["No anomalous events detected."],
        "confidence_label": "High Confidence",
        "rule_rationale": "All health checks and telemetry heartbeats conform to expected baselines.",
        "recommended_next_action": "Continue normal Sentinel monitoring."
    }

def check_retry_safety(order, failure_verified=None, duplicate_protection_passed=None,
                       retry_count=None, max_retries=None, policy_permits=None,
                       executed_idemp_keys=None):
    """
    Core Safe Recovery Decision Function ("Prove Before You Retry").
    Evaluates the 4 strict safety gates:
    1. Failure verified by available evidence?
    2. Duplicate protection passes (idempotency key valid and not already executed)?
    3. Retry count remains below configured limit?
    4. Recovery policy permits the action?
    """
    evidence = order.get("downstream_evidence", {})
    idemp_key = order.get("idempotency_key", "idemp-generic")
    
    # 1. Failure verified check
    if failure_verified is None:
        failure_verified = (evidence.get("verification_status") == "FAILURE_VERIFIED")

    # 2. Duplicate protection check
    if duplicate_protection_passed is None:
        if executed_idemp_keys and idemp_key in executed_idemp_keys:
            duplicate_protection_passed = False
            dup_detail = f"Idempotency key '{idemp_key}' was ALREADY executed. Duplicate transaction blocked."
        elif evidence.get("duplicate_charge_risk") == "ZERO (Safe - Idempotency key verified unused)":
            duplicate_protection_passed = True
            dup_detail = f"Idempotency key '{idemp_key}' active, unique, and verified uncommitted."
        elif evidence.get("verification_status") == "FAILURE_UNVERIFIED":
            duplicate_protection_passed = False
            dup_detail = "Downstream state ambiguous; duplicate protection CANNOT be guaranteed."
        else:
            duplicate_protection_passed = True
            dup_detail = f"Key '{idemp_key}' checked against session registry."
    else:
        dup_detail = "Explicit safety test parameter evaluated."

    # 3. Retry budget check
    if retry_count is None:
        retry_count = int(order.get("retry_count", 0))
    if max_retries is None:
        max_retries = int(order.get("max_retries", 2))
    
    retry_budget_passed = (retry_count < max_retries)
    retry_detail = f"Current retries: {retry_count} / Allowed limit: {max_retries}"

    # 4. Policy check
    if policy_permits is None:
        policy_permits = True  # Standard baseline policy allows safe retry if conditions 1-3 pass
    policy_detail = "Policy POL-RECOVER-SAFE permits auto-recovery only when gates 1-3 pass."

    # Build Checks Matrix
    checks_matrix = {
        "failure_verified": {
            "name": "Gate 1: Downstream Failure Conclusively Verified",
            "passed": failure_verified,
            "status": "PASS" if failure_verified else "FAIL",
            "detail": (
                "Verified via downstream reconciliation query: 0 ledger entries found, no fund locks."
                if failure_verified else
                "UNVERIFIED / UNCERTAIN. Downstream inquiry returned ambiguous status (502 Indeterminate)."
            )
        },
        "duplicate_protection": {
            "name": "Gate 2: Duplicate Protection & Idempotency",
            "passed": duplicate_protection_passed,
            "status": "PASS" if duplicate_protection_passed else "FAIL",
            "detail": dup_detail
        },
        "retry_budget": {
            "name": "Gate 3: Retry Budget within Limit",
            "passed": retry_budget_passed,
            "status": "PASS" if retry_budget_passed else "FAIL",
            "detail": retry_detail
        },
        "policy_permits": {
            "name": "Gate 4: Recovery Policy Authorization",
            "passed": policy_permits,
            "status": "PASS" if policy_permits else "FAIL",
            "detail": policy_detail
        }
    }

    all_passed = (failure_verified and duplicate_protection_passed and retry_budget_passed and policy_permits)

    if all_passed:
        decision = "RETRY_PERMITTED"
        status_label = "SAFE SIMULATED RETRY PERMITTED"
        reason = (
            "All 4 safety gates verified: Downstream failure is confirmed by ledger inquiry, "
            f"idempotency key '{idemp_key}' prevents duplicate mutation, retry count ({retry_count}/{max_retries}) "
            "is within budget, and recovery policy approves automated recovery."
        )
        recommended_action = "Execute controlled simulated retry with backoff and record transaction."
    elif not failure_verified:
        decision = "HUMAN_REVIEW_REQUIRED"
        status_label = "HUMAN REVIEW REQUIRED (Retry Blocked)"
        reason = (
            "PROVE BEFORE YOU RETRY: An API timeout alone does not prove downstream failure. "
            "Downstream outcome is ambiguous (HTTP 502 / Indeterminate). Automatic retry is BLOCKED "
            "to prevent duplicate mutation or financial double-charge."
        )
        recommended_action = (
            "Freeze automated retries. Alert operations specialist to reconcile the transaction "
            "directly with the downstream partner ledger portal."
        )
    else:
        decision = "RETRY_BLOCKED"
        status_label = "RETRY BLOCKED"
        failures = []
        if not duplicate_protection_passed:
            failures.append("Duplicate protection check failed")
        if not retry_budget_passed:
            failures.append(f"Retry limit exceeded ({retry_count}/{max_retries})")
        if not policy_permits:
            failures.append("Policy authorization denied")
        reason = f"Safety constraints violated: {', '.join(failures)}."
        recommended_action = "Escalate to engineering operations for manual intervention."

    return {
        "all_passed": all_passed,
        "decision": decision,
        "status_label": status_label,
        "reason": reason,
        "recommended_action": recommended_action,
        "checks_matrix": checks_matrix,
        "order_id": order.get("order_id")
    }

def add_audit_event(audit_log, scenario, order_id, evidence_checked,
                    safety_decision, reason, action_taken, simulated_outcome):
    """Appends an immutable audit log record to session state."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "scenario": scenario,
        "order_id": order_id,
        "evidence_checked": evidence_checked,
        "safety_decision": safety_decision,
        "reason": reason,
        "action_taken": action_taken,
        "simulated_outcome": simulated_outcome
    }
    audit_log.insert(0, entry)
    return entry

def run_api_timeout_scenario(orders, audit_log, executed_idemp_keys):
    """
    Executes Scenario 1: API Timeout — Safe Simulated Retry.
    Demonstrates evidence-based safe recovery when all safety gates pass.
    """
    order = orders["ORD-8041"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Run strict safety checks
    safety_result = check_retry_safety(order, executed_idemp_keys=executed_idemp_keys)

    if safety_result["all_passed"]:
        # Simulate safe recovery action
        order["retry_count"] += 1
        order["status"] = "Retry Permitted"
        order["status_code"] = "RETRY_PERMITTED"
        order["risk_level"] = "Low"
        order["current_stage"] = "Fulfilment Started"
        order["latest_event"] = f"SIMULATED_RETRY_SUCCESS (Attempt {order['retry_count']}/2)"
        order["recommended_next_action"] = "Proceed with warehouse picking dispatch"

        # Record idempotency execution
        executed_idemp_keys.add(order["idempotency_key"])

        # Append new timeline events
        order["events"].append({
            "timestamp": now_str,
            "event_name": f"SIMULATED_SAFE_RETRY_DISPATCHED",
            "stage": "Payment Confirmed",
            "status": "SUCCESS",
            "detail": f"Dispatched simulated retry with Idempotency-Key '{order['idempotency_key']}'. Safe backoff: 500ms."
        })
        order["events"].append({
            "timestamp": now_str,
            "event_name": "PAYMENT_CONFIRMED_RECOVERED",
            "stage": "Payment Confirmed",
            "status": "SUCCESS",
            "detail": "Simulated PayFlow API returned HTTP 200: {'status': 'CAPTURED', 'auth_code': 'REC-8041-A'}."
        })

        # Append API log
        order["simulated_api_logs"].append({
            "timestamp": now_str,
            "method": "POST",
            "endpoint": "https://api.payflow.internal/v1/charges",
            "status_code": 200,
            "latency_ms": 210,
            "log_level": "INFO",
            "message": "Simulated Retry Succeeded: Payment captured via Idempotency-Key. Tx #REC-8041-A."
        })

        # Record in Audit Trail
        add_audit_event(
            audit_log=audit_log,
            scenario="Scenario 1: API Timeout & Safe Recovery",
            order_id="ORD-8041",
            evidence_checked="PayFlow ledger 404 (NOT_FOUND), lock_acquired=false, idempotency key validated",
            safety_decision="RETRY_PERMITTED",
            reason=safety_result["reason"],
            action_taken="Simulated Safe Retry Dispatched (Attempt 1/2)",
            simulated_outcome="Payment confirmed; Order stage transitioned to 'Fulfilment Started'"
        )

        simulated_action_result = {
            "success": True,
            "title": "SAFE SIMULATED RETRY PERMITTED — all required checks passed.",
            "action_executed": "Simulated POST /v1/charges with verified Idempotency-Key",
            "simulated_response": "HTTP 200 OK | {'status': 'CAPTURED', 'auth_code': 'REC-8041-A'}",
            "order_stage_transition": "Payment Confirmed ➔ Fulfilment Started",
            "audit_logged": True
        }
    else:
        simulated_action_result = {
            "success": False,
            "title": "RETRY BLOCKED — Safety conditions not met.",
            "action_executed": "None (Execution halted by Sentinel Safety Engine)",
            "simulated_response": "N/A",
            "order_stage_transition": "Stage unchanged",
            "audit_logged": True
        }
        add_audit_event(
            audit_log=audit_log,
            scenario="Scenario 1: API Timeout & Safe Recovery",
            order_id="ORD-8041",
            evidence_checked="Downstream state checks",
            safety_decision=safety_result["decision"],
            reason=safety_result["reason"],
            action_taken="Auto-retry blocked",
            simulated_outcome="Order remains in current stage awaiting intervention"
        )

    return {
        "scenario_name": "Scenario 1: API Timeout and Safe Recovery",
        "order": order,
        "safety_result": safety_result,
        "simulated_action_result": simulated_action_result
    }

def run_delayed_order_scenario(orders, audit_log):
    """
    Executes Scenario 2: Delayed Order — Predictive SLA Alert.
    Demonstrates transparent rule-based SLA detection and root cause breakdown.
    """
    order = orders["ORD-8042"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Evaluate SLA Risk
    sla_result = calculate_sla_risk(order)
    root_cause = analyze_root_cause(order)

    # Update order state
    order["status"] = "SLA Risk"
    order["status_code"] = "SLA_RISK"
    order["risk_level"] = "Critical SLA Risk"
    order["latest_event"] = "SLA_BREACH_ALERT_TRIGGERED (Exceeded by +33m / 320% consumed)"
    order["recommended_next_action"] = "Supervisor dispatch: Re-route picking task to Node #2 (Zone A)"

    # Append timeline event
    order["events"].append({
        "timestamp": now_str,
        "event_name": "SLA_BREACH_ALERT_TRIGGERED",
        "stage": "Fulfilment Started",
        "status": "WARNING",
        "detail": (
            f"Sentinel Rule Engine triggered SLA Alert: {order['elapsed_minutes']}m spent in "
            f"'{order['current_stage']}' vs threshold {order['sla_threshold_minutes']}m (+33m breach)."
        )
    })

    # Record in Audit Trail
    add_audit_event(
        audit_log=audit_log,
        scenario="Scenario 2: Delayed Order & SLA Alert",
        order_id="ORD-8042",
        evidence_checked=f"Elapsed stage time ({order['elapsed_minutes']}m) > threshold ({order['sla_threshold_minutes']}m); missing pick confirmation",
        safety_decision="SLA_RISK_ALERT_RAISED",
        reason="Rule-based stage threshold breached by +33 mins. WMS queue telemetry indicates RF terminal disconnect.",
        action_taken="Simulated Ops Alert & Re-route Ticket Created",
        simulated_outcome="Operations supervisor alerted; re-route recommendation pushed to warehouse console"
    )

    return {
        "scenario_name": "Scenario 2: Delayed Order and SLA Alert",
        "order": order,
        "sla_result": sla_result,
        "root_cause": root_cause,
        "alert_title": "SLA RISK DETECTED — this order has exceeded the configured time threshold for its current stage.",
        "simulated_action_result": {
            "success": True,
            "action_executed": "Simulated Ops Ticket #OPS-8042-SLA dispatched to WMS Floor Supervisor",
            "simulated_response": "ACK: Ticket assigned to Floor Lead (Zone B). Re-route proposal generated.",
            "order_stage_transition": "Stage maintained at 'Fulfilment Started' with High Priority Escalation flag",
            "audit_logged": True
        }
    }

def run_uncertain_outcome_scenario(orders, audit_log, executed_idemp_keys):
    """
    Executes Scenario 3: Uncertain API Outcome — Block Unsafe Retry.
    Visibly proves key differentiator: 'PROVE BEFORE YOU RETRY'.
    """
    order = orders["ORD-8043"]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Run safety checks on uncertain order
    safety_result = check_retry_safety(order, executed_idemp_keys=executed_idemp_keys)
    root_cause = analyze_root_cause(order)

    # Update order state
    order["status"] = "Human Review Required"
    order["status_code"] = "HUMAN_REVIEW_REQUIRED"
    order["risk_level"] = "High Uncertainty"
    order["latest_event"] = "RETRY_BLOCKED_UNCONFIRMED_STATE (Human Review Required)"
    order["recommended_next_action"] = "Manual operator ledger reconciliation before any retry"

    # Append timeline event
    order["events"].append({
        "timestamp": now_str,
        "event_name": "RETRY_BLOCKED_BY_SAFETY_ENGINE",
        "stage": "Inventory Reserved",
        "status": "ERROR",
        "detail": (
            "PROVE BEFORE YOU RETRY: Gateway 504 Timeout occurred but downstream ledger status is 502 INDETERMINATE. "
            "Automatic retry BLOCKED to prevent catastrophic double-reservation of cold-chain medical stock."
        )
    })

    # Record in Audit Trail
    add_audit_event(
        audit_log=audit_log,
        scenario="Scenario 3: Uncertain Outcome & Human Review",
        order_id="ORD-8043",
        evidence_checked="HTTP 504 on POST; downstream ledger status 502 INDETERMINATE; lock state ambiguous",
        safety_decision="HUMAN_REVIEW_REQUIRED",
        reason=safety_result["reason"],
        action_taken="Automatic Retry Blocked — Human Review Required",
        simulated_outcome="Order locked in safety escrow; incident escalated for operator ledger verification"
    )

    return {
        "scenario_name": "Scenario 3: Uncertain Outcome and Human Review",
        "order": order,
        "safety_result": safety_result,
        "root_cause": root_cause,
        "core_differentiator": "PROVE BEFORE YOU RETRY",
        "alert_title": "HUMAN REVIEW REQUIRED",
        "simulated_action_result": {
            "success": True,
            "action_executed": "Simulated Safety Escrow Lock engaged; Escalation notification pushed to Operator Portal",
            "simulated_response": "Escrow Lock #ESC-8043-SAFE active. Automatic retry disabled for order ORD-8043.",
            "order_stage_transition": "Stage held at 'Inventory Reserved' awaiting manual reconciliation",
            "audit_logged": True
        }
    }

def run_operator_resolution(orders, audit_log, order_id, resolution_type, executed_idemp_keys):
    """
    Simulates manual human operator intervention for orders requiring review.
    Demonstrates the completed human-in-the-loop lifecycle.
    """
    order = orders.get(order_id)
    if not order:
        return False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if resolution_type == "VERIFIED_COMMITTED":
        # Operator confirmed with partner that the operation actually succeeded
        order["status"] = "Normal"
        order["status_code"] = "NORMAL"
        order["risk_level"] = "Normal"
        order["current_stage"] = "Fulfilment Started"
        order["latest_event"] = "OPERATOR_RECONCILED_SUCCESS (Ledger Verified Committed)"
        order["recommended_next_action"] = "Resume automated pipeline workflow"
        order["events"].append({
            "timestamp": now_str,
            "event_name": "OPERATOR_MANUAL_RECONCILIATION",
            "stage": order["current_stage"],
            "status": "SUCCESS",
            "detail": "Operator verified with partner bank ledger: reservation #INV-8043-COMMITTED was recorded. Safe to proceed."
        })
        add_audit_event(
            audit_log=audit_log,
            scenario="Manual Human Operator Intervention",
            order_id=order_id,
            evidence_checked="Operator manual ledger lookup confirmed transaction existence",
            safety_decision="HUMAN_VERIFIED_SUCCESS",
            reason="Operator confirmed transaction was captured downstream despite timeout.",
            action_taken="Manual Reconciliation: State Synchronized",
            simulated_outcome="Order unlocked and progressed to Fulfilment Started"
        )
    elif resolution_type == "VERIFIED_FAILED_RETRY":
        # Operator confirmed transaction never happened, safe to retry
        executed_idemp_keys.discard(order["idempotency_key"])
        order["retry_count"] += 1
        order["status"] = "Retry Permitted"
        order["status_code"] = "RETRY_PERMITTED"
        order["risk_level"] = "Low"
        order["current_stage"] = "Fulfilment Started"
        order["latest_event"] = f"OPERATOR_AUTHORIZED_RETRY (Attempt {order['retry_count']}/2)"
        order["recommended_next_action"] = "Proceed with fulfilment"
        order["events"].append({
            "timestamp": now_str,
            "event_name": "OPERATOR_MANUAL_RETRY_AUTHORIZED",
            "stage": order["current_stage"],
            "status": "SUCCESS",
            "detail": "Operator confirmed upstream void. Manual simulated retry authorized with clean idempotency key."
        })
        add_audit_event(
            audit_log=audit_log,
            scenario="Manual Human Operator Intervention",
            order_id=order_id,
            evidence_checked="Operator verified absence of downstream reservation lock",
            safety_decision="OPERATOR_RETRY_AUTHORIZED",
            reason="Operator confirmed partner ledger was empty. Retry authorized with human oversight.",
            action_taken="Operator-Authorized Controlled Retry",
            simulated_outcome="Inventory reserved safely; Order progressed to Fulfilment Started"
        )
    return True
