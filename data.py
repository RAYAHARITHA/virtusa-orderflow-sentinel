"""
OrderFlow Sentinel - Synthetic Data & State Management
Provides realistic synthetic order states, event logs, API telemetry,
and audit trails for hackathon demonstration.
"""

from datetime import datetime, timedelta

def get_stage_sla_limits():
    """Configured stage SLA limits in minutes for deterministic rule-based detection."""
    return {
        "Order Created": 5.0,
        "Payment Confirmed": 5.0,
        "Inventory Reserved": 8.0,
        "Fulfilment Started": 15.0,
        "Shipment Requested": 20.0,
        "Shipment Confirmed": 30.0,
        "Order Completed": 120.0
    }

def get_initial_orders():
    """
    Returns initial synthetic orders with complete timelines, API telemetry,
    and downstream state evidence. Includes at least 8 realistic orders.
    """
    now = datetime.now()
    t_minus = lambda mins: (now - timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "ORD-8041": {
            "order_id": "ORD-8041",
            "order_type": "Express B2B",
            "customer": "Acme Retail Logistics",
            "item_summary": "14x High-Speed Optical Barcode Scanners",
            "amount": 2840.00,
            "current_stage": "Payment Confirmed",
            "status": "API Error",
            "status_code": "API_ERROR",
            "elapsed_minutes": 5.4,
            "sla_threshold_minutes": 5.0,
            "latest_event": "GATEWAY_TIMEOUT (HTTP 504 on POST /v1/charges)",
            "risk_level": "Medium",
            "recommended_next_action": "Inspect downstream ledger before deciding retry",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8041-pay-v1",
            "downstream_service": "Payment Gateway (PayFlow Global API)",
            "created_at": t_minus(6),
            "last_updated": t_minus(1),
            "events": [
                {
                    "timestamp": t_minus(6),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Order created via B2B EDI connector. Customer credit terms pre-approved."
                },
                {
                    "timestamp": t_minus(5),
                    "event_name": "INVENTORY_RESERVED",
                    "stage": "Inventory Reserved",
                    "status": "SUCCESS",
                    "detail": "14 units reserved at Dallas Distribution Hub Bin #B-14."
                },
                {
                    "timestamp": t_minus(4),
                    "event_name": "PAYMENT_REQUEST_INITIATED",
                    "stage": "Payment Confirmed",
                    "status": "PENDING",
                    "detail": "Sent POST /v1/charges to PayFlow API with Idempotency-Key: idemp-ord-8041-pay-v1."
                },
                {
                    "timestamp": t_minus(1),
                    "event_name": "GATEWAY_TIMEOUT_OBSERVED",
                    "stage": "Payment Confirmed",
                    "status": "ERROR",
                    "detail": "HTTP 504 Gateway Timeout after 30,000ms. TCP connection reset by peer."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(4),
                    "method": "POST",
                    "endpoint": "https://api.payflow.internal/v1/charges",
                    "status_code": 504,
                    "latency_ms": 30005,
                    "log_level": "ERROR",
                    "message": "Gateway Timeout: Upstream banking server dropped connection after 30s. No HTTP response body."
                },
                {
                    "timestamp": t_minus(1),
                    "method": "GET",
                    "endpoint": "https://api.payflow.internal/v1/reconcile/idemp-ord-8041-pay-v1",
                    "status_code": 404,
                    "latency_ms": 142,
                    "log_level": "INFO",
                    "message": "Reconciliation check: {'status': 'NOT_FOUND_IN_LEDGER', 'authorized': false, 'lock_acquired': false}."
                }
            ],
            "downstream_evidence": {
                "source": "PayFlow Central Reconciliation Ledger",
                "inquiry_type": "Idempotency Lookup via Query Endpoint",
                "transaction_found_in_ledger": False,
                "fund_authorization_lock": "NOT_ACQUIRED",
                "downstream_confirmed_executed": False,
                "duplicate_charge_risk": "ZERO (Safe - Idempotency key verified unused)",
                "idempotency_key_active": True,
                "retry_budget_remaining": 2,
                "verification_status": "FAILURE_VERIFIED"
            }
        },

        "ORD-8042": {
            "order_id": "ORD-8042",
            "order_type": "Priority Enterprise",
            "customer": "Global Express Direct",
            "item_summary": "45x Rugged Android Handheld Terminals",
            "amount": 9120.00,
            "current_stage": "Fulfilment Started",
            "status": "SLA Risk",
            "status_code": "SLA_RISK",
            "elapsed_minutes": 48.0,
            "sla_threshold_minutes": 15.0,
            "latest_event": "MISSING_CONFIRMATION_ALERT (WMS pick scan missing for 48m)",
            "risk_level": "Critical SLA Risk",
            "recommended_next_action": "Investigate WMS queue & notify ops supervisor",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8042-wms-v1",
            "downstream_service": "Warehouse Management System (WMS Node #4)",
            "created_at": t_minus(52),
            "last_updated": t_minus(2),
            "events": [
                {
                    "timestamp": t_minus(52),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Enterprise purchase order validated. Contract SLA: same-day dispatch."
                },
                {
                    "timestamp": t_minus(50),
                    "event_name": "PAYMENT_CONFIRMED",
                    "stage": "Payment Confirmed",
                    "status": "SUCCESS",
                    "detail": "Corporate line of credit verified. Authorization #PAY-99211."
                },
                {
                    "timestamp": t_minus(48),
                    "event_name": "PICK_TASK_DISPATCHED",
                    "stage": "Fulfilment Started",
                    "status": "PENDING",
                    "detail": "Picking ticket dispatched to WMS Node #4 (Zone B, Aisle 14). Configured stage SLA: 15 mins."
                },
                {
                    "timestamp": t_minus(1),
                    "event_name": "MISSING_CONFIRMATION_ALERT",
                    "stage": "Fulfilment Started",
                    "status": "WARNING",
                    "detail": "[MISSING EVENT] Pick confirmation not received after 48 minutes (Threshold: 15m. Exceeded by +33m)."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(48),
                    "method": "POST",
                    "endpoint": "https://wms-node4.warehouse.internal/api/pick/tasks",
                    "status_code": 202,
                    "latency_ms": 280,
                    "log_level": "INFO",
                    "message": "Task queued: {'task_id': 'PICK-8042', 'status': 'QUEUED', 'assigned_operator': 'UNASSIGNED'}."
                },
                {
                    "timestamp": t_minus(20),
                    "method": "GET",
                    "endpoint": "https://wms-node4.warehouse.internal/api/queue/health",
                    "status_code": 200,
                    "latency_ms": 95,
                    "log_level": "WARN",
                    "message": "Node 4 telemetry alert: Operator RF scanner subnet degraded; queue depth 142 items."
                }
            ],
            "downstream_evidence": {
                "source": "WMS Fulfillment Telemetry",
                "inquiry_type": "Stage Duration Audit",
                "stage_name": "Fulfilment Started",
                "elapsed_minutes": 48.0,
                "sla_threshold_minutes": 15.0,
                "breach_percentage": "320% of allowed stage SLA",
                "missing_event": "PICK_CONFIRMATION_ACK",
                "root_cause_indicator": "WMS Node #4 worker terminal disconnection / queue backlog",
                "recommended_action": "Notify Warehouse Supervisor & Re-route pick task to Node #2 (Zone A)"
            }
        },

        "ORD-8043": {
            "order_id": "ORD-8043",
            "order_type": "Cold-Chain Medical",
            "customer": "Apex Healthcare Supplies",
            "item_summary": "500x Sterile Cryo-Vial Cold Storage Units",
            "amount": 16750.00,
            "current_stage": "Inventory Reserved",
            "status": "Human Review Required",
            "status_code": "HUMAN_REVIEW_REQUIRED",
            "elapsed_minutes": 4.1,
            "sla_threshold_minutes": 8.0,
            "latest_event": "INCONCLUSIVE_TIMEOUT (POST /v2/inventory/commit returned 504, ledger status 502 INDETERMINATE)",
            "risk_level": "High Uncertainty",
            "recommended_next_action": "Manual operator ledger reconciliation before any retry",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8043-inv-res",
            "downstream_service": "Global Cold-Chain Inventory & Ledger System",
            "created_at": t_minus(5),
            "last_updated": t_minus(1),
            "events": [
                {
                    "timestamp": t_minus(5),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Priority medical supplies intake verified with temperature compliance flags."
                },
                {
                    "timestamp": t_minus(4),
                    "event_name": "CREDIT_HELD",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Hospital procurement pre-authorization hold secured for $16,750.00."
                },
                {
                    "timestamp": t_minus(3),
                    "event_name": "INVENTORY_COMMIT_CALL",
                    "stage": "Inventory Reserved",
                    "status": "PENDING",
                    "detail": "Called POST /v2/inventory/commit-coldchain to reserve 500 Cryo units."
                },
                {
                    "timestamp": t_minus(1),
                    "event_name": "INCONCLUSIVE_TIMEOUT",
                    "stage": "Inventory Reserved",
                    "status": "ERROR",
                    "detail": "Gateway 504 Timeout occurred during commit phase. Downstream state ambiguous."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(3),
                    "method": "POST",
                    "endpoint": "https://inv-ledger.pharma.internal/v2/inventory/commit-coldchain",
                    "status_code": 504,
                    "latency_ms": 30000,
                    "log_level": "ERROR",
                    "message": "Gateway Timeout: upstream partner connection dropped mid-packet transfer."
                },
                {
                    "timestamp": t_minus(1),
                    "method": "GET",
                    "endpoint": "https://inv-ledger.pharma.internal/v2/inventory/check-status/idemp-ord-8043-inv-res",
                    "status_code": 502,
                    "latency_ms": 1150,
                    "log_level": "CRITICAL",
                    "message": "HTTP 502 Bad Gateway: Upstream ledger database partition. Status returned: 'INDETERMINATE / IN_PROGRESS'."
                }
            ],
            "downstream_evidence": {
                "source": "Cold-Chain Inventory Ledger Query Endpoint",
                "inquiry_type": "Multi-Region Ledger Consistency Audit",
                "transaction_found_in_ledger": "UNKNOWN / AMBIGUOUS",
                "fund_authorization_lock": "PARTIALLY_PROCESSED_OR_ORPHANED",
                "downstream_confirmed_executed": None,
                "duplicate_charge_risk": "EXTREME (May double-reserve limited medical vaccine stock)",
                "idempotency_key_active": "UNCONFIRMED_BY_SERVER",
                "retry_budget_remaining": 2,
                "verification_status": "FAILURE_UNVERIFIED"
            }
        },

        "ORD-8044": {
            "order_id": "ORD-8044",
            "order_type": "Standard Ground",
            "customer": "Nexus Dynamics Corp",
            "item_summary": "2x Industrial Server Cabinets",
            "amount": 11400.00,
            "current_stage": "Shipment Requested",
            "status": "In Progress",
            "status_code": "IN_PROGRESS",
            "elapsed_minutes": 8.5,
            "sla_threshold_minutes": 20.0,
            "latest_event": "CARRIER_DISPATCH_SUBMITTED (Atlas Freight dispatch)",
            "risk_level": "Low",
            "recommended_next_action": "Monitor carrier API webhook for pickup confirmation",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8044-trk-v1",
            "downstream_service": "Freight Carrier API (Atlas Freight)",
            "created_at": t_minus(35),
            "last_updated": t_minus(8),
            "events": [
                {
                    "timestamp": t_minus(35),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "High-value freight scheduled."
                },
                {
                    "timestamp": t_minus(25),
                    "event_name": "PAYMENT_CONFIRMED",
                    "stage": "Payment Confirmed",
                    "status": "SUCCESS",
                    "detail": "Wire transfer validated."
                },
                {
                    "timestamp": t_minus(12),
                    "event_name": "FULFILMENT_COMPLETED",
                    "stage": "Fulfilment Started",
                    "status": "SUCCESS",
                    "detail": "Crated and staged at Loading Bay 2."
                },
                {
                    "timestamp": t_minus(8),
                    "event_name": "DISPATCH_REQUESTED",
                    "stage": "Shipment Requested",
                    "status": "PENDING",
                    "detail": "Pickup manifest dispatched to Atlas Freight."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(8),
                    "method": "POST",
                    "endpoint": "https://carrier.atlasfreight.internal/api/v1/shipments",
                    "status_code": 201,
                    "latency_ms": 410,
                    "log_level": "INFO",
                    "message": "Waybill issued: WB-441209. Driver assigned: Unit 82."
                }
            ],
            "downstream_evidence": {
                "source": "Carrier Telematics API",
                "inquiry_type": "Route Status",
                "downstream_confirmed_executed": True,
                "duplicate_charge_risk": "None",
                "notes": "Truck arrival estimated in 12 minutes."
            }
        },

        "ORD-8045": {
            "order_id": "ORD-8045",
            "order_type": "Same-Day Delivery",
            "customer": "BlueHorizon Biotech",
            "item_summary": "8x Laboratory Centrifuges",
            "amount": 5600.00,
            "current_stage": "Shipment Confirmed",
            "status": "In Progress",
            "status_code": "IN_PROGRESS",
            "elapsed_minutes": 25.0,
            "sla_threshold_minutes": 30.0,
            "latest_event": "CARRIER_PICKUP_ACK (Driver en route to hub)",
            "risk_level": "Low",
            "recommended_next_action": "Track telematics route progress",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8045-dlv-v1",
            "downstream_service": "Courier Transit Telematics",
            "created_at": t_minus(40),
            "last_updated": t_minus(5),
            "events": [
                {
                    "timestamp": t_minus(40),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Same-day biomedical transit initialized."
                },
                {
                    "timestamp": t_minus(30),
                    "event_name": "FULFILMENT_COMPLETED",
                    "stage": "Fulfilment Started",
                    "status": "SUCCESS",
                    "detail": "Inspected and packed in shock-proof casing."
                },
                {
                    "timestamp": t_minus(5),
                    "event_name": "PICKUP_CONFIRMED",
                    "stage": "Shipment Confirmed",
                    "status": "SUCCESS",
                    "detail": "Driver scanned package barcode at facility gate."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(5),
                    "method": "POST",
                    "endpoint": "https://courier.internal/v1/scan",
                    "status_code": 200,
                    "latency_ms": 110,
                    "log_level": "INFO",
                    "message": "Scan confirmed: custody transferred to Driver #D-502."
                }
            ],
            "downstream_evidence": {
                "source": "Courier Telematics",
                "inquiry_type": "Custody Check",
                "downstream_confirmed_executed": True,
                "duplicate_charge_risk": "None",
                "notes": "Custody transfer complete."
            }
        },

        "ORD-8046": {
            "order_id": "ORD-8046",
            "order_type": "Standard Ground",
            "customer": "Summit Industrial Parts",
            "item_summary": "120x Precision Roller Bearings",
            "amount": 3410.00,
            "current_stage": "Order Created",
            "status": "In Progress",
            "status_code": "IN_PROGRESS",
            "elapsed_minutes": 1.5,
            "sla_threshold_minutes": 5.0,
            "latest_event": "EDI_INGESTION_SUCCESS (Order validated)",
            "risk_level": "Normal",
            "recommended_next_action": "Awaiting automatic payment pre-authorization",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8046-std-v1",
            "downstream_service": "EDI Gateway",
            "created_at": t_minus(2),
            "last_updated": t_minus(1),
            "events": [
                {
                    "timestamp": t_minus(2),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "EDI 850 Purchase Order parsed and validated."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(2),
                    "method": "POST",
                    "endpoint": "https://edi.internal/v1/orders",
                    "status_code": 201,
                    "latency_ms": 130,
                    "log_level": "INFO",
                    "message": "EDI Document parsed without validation warnings."
                }
            ],
            "downstream_evidence": {
                "source": "EDI Validation Service",
                "inquiry_type": "Schema Check",
                "downstream_confirmed_executed": True,
                "duplicate_charge_risk": "None",
                "notes": "Ready for payment stage."
            }
        },

        "ORD-8047": {
            "order_id": "ORD-8047",
            "order_type": "Express B2B",
            "customer": "OmniTech Solutions",
            "item_summary": "60x Cat-6a Shielded Network Patch Panels",
            "amount": 4200.00,
            "current_stage": "Order Completed",
            "status": "Normal",
            "status_code": "NORMAL",
            "elapsed_minutes": 42.0,
            "sla_threshold_minutes": 120.0,
            "latest_event": "DELIVERY_SIGNATURE_CAPTURED",
            "risk_level": "Normal",
            "recommended_next_action": "Archived. No action required.",
            "retry_count": 0,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8047-cmp-v1",
            "downstream_service": "ePOD Sign-off Service",
            "created_at": t_minus(60),
            "last_updated": t_minus(5),
            "events": [
                {
                    "timestamp": t_minus(60),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Order placed via customer web portal."
                },
                {
                    "timestamp": t_minus(50),
                    "event_name": "PAYMENT_CONFIRMED",
                    "stage": "Payment Confirmed",
                    "status": "SUCCESS",
                    "detail": "Credit card pre-authorization settled."
                },
                {
                    "timestamp": t_minus(30),
                    "event_name": "FULFILMENT_COMPLETED",
                    "stage": "Fulfilment Started",
                    "status": "SUCCESS",
                    "detail": "Picking and packing completed in 11 minutes."
                },
                {
                    "timestamp": t_minus(5),
                    "event_name": "DELIVERY_SIGNATURE_CAPTURED",
                    "stage": "Order Completed",
                    "status": "SUCCESS",
                    "detail": "Customer signed on glass. Proof of delivery uploaded."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(5),
                    "method": "POST",
                    "endpoint": "https://epod.delivery.internal/api/v1/signatures",
                    "status_code": 200,
                    "latency_ms": 180,
                    "log_level": "INFO",
                    "message": "Signature uploaded and verified against badge ID #7721."
                }
            ],
            "downstream_evidence": {
                "source": "ePOD Cloud Verification",
                "inquiry_type": "Sign-off Audit",
                "downstream_confirmed_executed": True,
                "duplicate_charge_risk": "None",
                "notes": "Order closed with zero defects."
            }
        },

        "ORD-8048": {
            "order_id": "ORD-8048",
            "order_type": "Bulk Wholesale",
            "customer": "Vanguard Electrical Distributors",
            "item_summary": "200x Smart Sub-Panel Meters",
            "amount": 22400.00,
            "current_stage": "Payment Confirmed",
            "status": "Retry Blocked",
            "status_code": "RETRY_BLOCKED",
            "elapsed_minutes": 6.8,
            "sla_threshold_minutes": 5.0,
            "latest_event": "RETRY_LIMIT_EXCEEDED (2 of 2 retries exhausted)",
            "risk_level": "High",
            "recommended_next_action": "Escalate to financial operations team",
            "retry_count": 2,
            "max_retries": 2,
            "idempotency_key": "idemp-ord-8048-exhausted",
            "downstream_service": "Corporate Wire Transfer Gateway",
            "created_at": t_minus(10),
            "last_updated": t_minus(2),
            "events": [
                {
                    "timestamp": t_minus(10),
                    "event_name": "ORDER_CREATED",
                    "stage": "Order Created",
                    "status": "SUCCESS",
                    "detail": "Large wholesale batch order generated."
                },
                {
                    "timestamp": t_minus(8),
                    "event_name": "PAYMENT_ATTEMPT_1",
                    "stage": "Payment Confirmed",
                    "status": "ERROR",
                    "detail": "First payment dispatch failed with connection drop."
                },
                {
                    "timestamp": t_minus(5),
                    "event_name": "PAYMENT_RETRY_1",
                    "stage": "Payment Confirmed",
                    "status": "ERROR",
                    "detail": "Retry attempt 1 failed with connection timeout."
                },
                {
                    "timestamp": t_minus(2),
                    "event_name": "RETRY_LIMIT_EXCEEDED",
                    "stage": "Payment Confirmed",
                    "status": "ERROR",
                    "detail": "Retry count reached ceiling (2/2). Sentinel policy blocks automatic recovery."
                }
            ],
            "simulated_api_logs": [
                {
                    "timestamp": t_minus(5),
                    "method": "POST",
                    "endpoint": "https://wire.gateway.internal/v1/transfer",
                    "status_code": 503,
                    "latency_ms": 15000,
                    "log_level": "ERROR",
                    "message": "Service Unavailable: Downstream bank switch in scheduled maintenance."
                }
            ],
            "downstream_evidence": {
                "source": "Wire Gateway Status",
                "inquiry_type": "Retry Budget Audit",
                "current_retries": 2,
                "max_retries": 2,
                "budget_exhausted": True,
                "policy_rule": "Policy POL-RETRY-02 forbids auto-retry when retries >= max_retries",
                "recommended_action": "Manual intervention required by Financial Ops"
            }
        }
    }

def get_initial_audit_log():
    """Initial seeded audit log records."""
    t_minus = lambda mins: (datetime.now() - timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")
    return [
        {
            "timestamp": t_minus(120),
            "scenario": "System Baseline",
            "order_id": "SYSTEM_CORE",
            "evidence_checked": "Policy rulebook v2.4 loaded & SLA config active",
            "safety_decision": "POLICY_INITIALIZED",
            "reason": "All stage SLA limits and safe recovery constraints primed.",
            "action_taken": "Sentinel Watchdog Active",
            "simulated_outcome": "Monitoring 8 synthetic fleet orders"
        },
        {
            "timestamp": t_minus(15),
            "scenario": "Standard Verification",
            "order_id": "ORD-8047",
            "evidence_checked": "Proof of delivery signature & GPS coordinates",
            "safety_decision": "ORDER_FINALIZED",
            "reason": "Delivery successfully completed within configured SLA window.",
            "action_taken": "Archive Order State",
            "simulated_outcome": "Order marked COMPLETED"
        }
    ]
