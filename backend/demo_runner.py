"""
NagarikAI Platform — End-to-End Demo Runner (Task 7.2)

Runs all five demo scenarios programmatically to verify the full demo flow.
Requires the backend to be running: uvicorn main:app --reload

Usage:
    cd backend
    python demo_runner.py
"""
import sys
import json
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    msg = f"  {status}  {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    results.append((label, condition))
    return condition


def post(path: str, payload: dict) -> dict | None:
    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        print(f"\n  ⚠️  Cannot connect to {BASE_URL}. Is the server running?")
        sys.exit(1)
    except Exception as exc:
        print(f"\n  ⚠️  Request failed: {exc}")
        return None


def get(path: str) -> dict | None:
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"\n  ⚠️  GET {path} failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Scenario 1: Widow Pension Beneficiary Discovery
# ---------------------------------------------------------------------------

def scenario_1_beneficiary_discovery() -> None:
    header("Scenario 1: Widow Pension Beneficiary Discovery")
    print("  Submitting death record for राम कुमार शर्मा (CDR001, Raipur)...")

    payload = {
        "record_id": "CDR001",
        "name": "राम कुमार शर्मा",
        "father_name": "श्री मोहन लाल शर्मा",
        "date_of_death": "2023-03-15",
        "age": 67,
        "gender": "M",
        "district": "रायपुर",
        "village": "खमतराई",
    }

    data = post("/api/beneficiary/discover", payload)
    if data is None:
        check("API responded", False)
        return

    print(f"\n  Response message: {data.get('message')}")
    print(f"  Total beneficiaries found: {data.get('total_found', 0)}")

    check("API success flag is True", data.get("success") is True)
    check("At least one beneficiary found", data.get("total_found", 0) >= 1)

    beneficiaries = data.get("beneficiaries", [])
    if beneficiaries:
        scores = [b["confidence_score"] for b in beneficiaries]
        check(
            "Beneficiaries ranked by confidence (descending)",
            all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)),
            f"Scores: {[f'{s:.2f}' for s in scores]}",
        )
        check(
            "All confidence scores in [0, 1]",
            all(0.0 <= s <= 1.0 for s in scores),
        )
        for b in beneficiaries:
            print(
                f"    • {b['beneficiary_name']} | scheme={b['scheme_type']}"
                f" | confidence={b['confidence_score']:.2%}"
            )


# ---------------------------------------------------------------------------
# Scenario 2: Grievance Classification — Pension (Hindi)
# ---------------------------------------------------------------------------

def scenario_2_grievance_pension() -> None:
    header("Scenario 2: Grievance Classification — Widow Pension (Hindi)")
    print("  Submitting Hindi grievance about missing pension payment...")

    payload = {
        "citizen_id": "CIT_DEMO_001",
        "text": (
            "मेरी विधवा पेंशन तीन महीने से नहीं आई है। "
            "बैंक में पूछा तो कहा कि विभाग से पैसा नहीं आया। "
            "मैं बहुत परेशान हूं, कृपया जल्दी कार्रवाई करें।"
        ),
        "language": "hi",
    }

    data = post("/api/grievance/submit", payload)
    if data is None:
        check("API responded", False)
        return

    grievance = data.get("grievance", {})
    print(f"\n  Grievance ID : {grievance.get('grievance_id')}")
    print(f"  Category     : {grievance.get('category')}")
    print(f"  Confidence   : {grievance.get('classification_confidence', 0):.2%}")
    print(f"  Predicted SLA: {grievance.get('predicted_sla')} hours")
    print(f"  Status       : {grievance.get('status')}")

    check("API success flag is True", data.get("success") is True)
    check("Grievance ID assigned", bool(grievance.get("grievance_id")))
    check("Category is non-empty", bool(grievance.get("category")))
    check(
        "Classification confidence in [0, 1]",
        0.0 <= grievance.get("classification_confidence", -1) <= 1.0,
    )
    check("Predicted SLA > 0", (grievance.get("predicted_sla") or 0) > 0)
    check("Status is 'submitted'", grievance.get("status") == "submitted")
    check("SLA deadline set", bool(grievance.get("sla_deadline")))


# ---------------------------------------------------------------------------
# Scenario 3: Grievance Classification — Health (Hindi)
# ---------------------------------------------------------------------------

def scenario_3_grievance_health() -> None:
    header("Scenario 3: Grievance Classification — Health Department (Hindi)")
    print("  Submitting Hindi grievance about hospital medicine shortage...")

    payload = {
        "citizen_id": "CIT_DEMO_002",
        "text": (
            "सरकारी अस्पताल में दवाइयां नहीं मिल रही हैं। "
            "डॉक्टर भी समय पर नहीं आते। "
            "मरीजों को बहुत परेशानी हो रही है।"
        ),
        "language": "hi",
    }

    data = post("/api/grievance/submit", payload)
    if data is None:
        check("API responded", False)
        return

    grievance = data.get("grievance", {})
    print(f"\n  Grievance ID : {grievance.get('grievance_id')}")
    print(f"  Category     : {grievance.get('category')}")
    print(f"  Confidence   : {grievance.get('classification_confidence', 0):.2%}")
    print(f"  Predicted SLA: {grievance.get('predicted_sla')} hours")

    check("API success flag is True", data.get("success") is True)
    check("Category is non-empty", bool(grievance.get("category")))
    check(
        "Classification confidence in [0, 1]",
        0.0 <= grievance.get("classification_confidence", -1) <= 1.0,
    )
    check("Predicted SLA > 0", (grievance.get("predicted_sla") or 0) > 0)


# ---------------------------------------------------------------------------
# Scenario 4: Application Validation — High Risk (Disability Pension)
# ---------------------------------------------------------------------------

def scenario_4_high_risk_application() -> None:
    header("Scenario 4: Application Validation — High Risk (Disability Pension)")
    print("  Submitting application with multiple validation issues...")

    payload = {
        "application_id": "APP_DEMO_HIGH_RISK",
        "scheme_type": "disability_pension",
        "operator_id": "OP_CSC_RAIPUR_01",
        "application_data": {
            "applicant_name": "Mohan Singh",
            "date_of_birth": "2010-01-01",   # age ~14, below 18 minimum
            "address": "Village Raigarh, District Raigarh",
            "bank_account": "123",            # invalid format
            "aadhaar_number": "12345",        # invalid format
            "disability_percentage": 30,      # below 40% minimum
            "annual_income": 200000,          # above threshold
        },
    }

    data = post("/api/application/validate", payload)
    if data is None:
        check("API responded", False)
        return

    validation = data.get("validation", {})
    risk_score = validation.get("rejection_risk_score", 0)
    issues = validation.get("validation_issues", [])
    guidance = validation.get("corrective_guidance", [])

    print(f"\n  Risk Score   : {risk_score:.2f}")
    print(f"  Issues found : {len(issues)}")
    print(f"  Guidance items: {len(guidance)}")
    for issue in issues:
        print(
            f"    • [{issue.get('severity', '?').upper()}] "
            f"{issue.get('field_name')} — {issue.get('issue_type')}"
        )

    check("API success flag is True", data.get("success") is True)
    check(
        "Risk score in [0, 1]",
        0.0 <= risk_score <= 1.0,
        f"Score: {risk_score:.2f}",
    )
    check(
        "High risk score (≥ 0.5) detected",
        risk_score >= 0.5,
        f"Score: {risk_score:.2f}",
    )
    check("At least one validation issue found", len(issues) >= 1)
    check(
        "Corrective guidance provided",
        len(guidance) >= 1,
    )
    # Verify bilingual guidance
    if guidance:
        g = guidance[0]
        check(
            "Guidance has Hindi text",
            bool(g.get("guidance_text_hindi")),
        )
        check(
            "Guidance has English text",
            bool(g.get("guidance_text_english")),
        )


# ---------------------------------------------------------------------------
# Scenario 5: Application Validation — Clean Application (Widow Pension)
# ---------------------------------------------------------------------------

def scenario_5_clean_application() -> None:
    header("Scenario 5: Application Validation — Clean Application (Widow Pension)")
    print("  Submitting a complete, valid widow pension application...")

    payload = {
        "application_id": "APP_DEMO_CLEAN",
        "scheme_type": "widow_pension",
        "operator_id": "OP_CSC_RAIPUR_01",
        "application_data": {
            "applicant_name": "Sunita Devi",
            "date_of_birth": "1985-03-15",
            "spouse_death_certificate": "DEATH_CERT_2024_001",
            "address": "Village Raipur, Block Dhamtari, District Raipur, PIN 492001",
            "bank_account": "1234567890123456",
            "aadhaar_number": "123456789012",
            "annual_income": 50000,
        },
    }

    data = post("/api/application/validate", payload)
    if data is None:
        check("API responded", False)
        return

    validation = data.get("validation", {})
    risk_score = validation.get("rejection_risk_score", 1)
    issues = validation.get("validation_issues", [])

    print(f"\n  Risk Score   : {risk_score:.2f}")
    print(f"  Issues found : {len(issues)}")
    print(f"  Message      : {data.get('message')}")

    check("API success flag is True", data.get("success") is True)
    check(
        "Risk score in [0, 1]",
        0.0 <= risk_score <= 1.0,
        f"Score: {risk_score:.2f}",
    )
    check(
        "Low risk score (< 0.3) for clean application",
        risk_score < 0.3,
        f"Score: {risk_score:.2f}",
    )
    check("No critical issues on clean application", len(issues) == 0)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def check_server_health() -> bool:
    header("Server Health Check")
    data = get("/api/health")
    if data is None:
        print("  ⚠️  Server is not reachable. Start it with:")
        print("      cd backend && uvicorn main:app --reload")
        return False
    print(f"  Status : {data.get('status')}")
    print(f"  Version: {data.get('version', 'n/a')}")
    check("Server is healthy", data.get("status") == "healthy")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 70)
    print("  NagarikAI Platform — End-to-End Demo Runner")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if not check_server_health():
        sys.exit(1)

    scenario_1_beneficiary_discovery()
    scenario_2_grievance_pension()
    scenario_3_grievance_health()
    scenario_4_high_risk_application()
    scenario_5_clean_application()

    # Summary
    header("Demo Results Summary")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n  {passed}/{total} checks passed\n")
    for label, ok in results:
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {label}")

    print()
    if passed == total:
        print("  🎉 All checks passed — demo is ready!")
    else:
        failed = total - passed
        print(f"  ⚠️  {failed} check(s) failed — review output above.")
    print()


if __name__ == "__main__":
    main()
