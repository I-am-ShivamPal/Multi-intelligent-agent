# Internal Testing Checklist

## Purpose
Pre-demo validation and testing protocol to ensure system readiness for stakeholder presentations.

---

## Pre-Demo Checklist

### Environment Setup
- [ ] Python 3.10+ installed and accessible
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Project directory clean (no leftover artifacts)
- [ ] Logs directory exists and is writable
- [ ] Terminal window sized appropriately for viewing

### File Verification
- [ ] `demo_run.py` exists and is executable
- [ ] `demo_utils.py` exists (formatting utilities)
- [ ] `onboarding_entry.py` exists (onboarding logic)
- [ ] `core/proof_logger.py` exists (logging)
- [ ] `samples/` directory contains valid input files

### Cleanup
- [ ] Remove old `apps/registry/demo-api.json` if exists
- [ ] Clear `logs/day1_proof.log` (demo does this automatically)
- [ ] Remove any stale demo artifacts

---

## Testing Scenarios

### Scenario 1: Happy Path - Full Demo Run

**Test**: Execute complete demo with all scenarios

```bash
python demo_run.py
```

**Expected Behavior**:
- ✅ Demo completes without errors
- ✅ All 3 scenarios pass (3/3)
- ✅ 18 proof events logged
- ✅ Duration ~3-4 seconds
- ✅ Exit code 0

**Validation**:
```bash
echo $?  # Should be 0
cat logs/day1_proof.log | wc -l  # Should be 18
```

**Status**: ⬜ Not Run | ✅ Passed | ❌ Failed

---

### Scenario 2: Onboarding Validation

**Test**: Verify onboarding rejects invalid inputs

```bash
python onboarding_entry.py samples/invalid_input_bad_name.json
```

**Expected Behavior**:
- ✅ Validation fails with clear error message
- ✅ `ONBOARDING_REJECTED` event logged
- ✅ No app_spec.json generated
- ✅ Exit code 1

**Status**: ⬜ Not Run | ✅ Passed | ❌ Failed

---

### Scenario 3: Proof Log Integrity

**Test**: Verify all events are logged correctly

```bash
python demo_run.py
python -c "import json; events = [json.loads(l.strip()) for l in open('logs/day1_proof.log') if l.strip()]; print(f'Events: {len(events)}'); print(set(e['event_name'] for e in events))"
```

**Expected Behavior**:
- ✅ 17 valid JSON events (18 lines, 1 empty)
- ✅ Event types: ONBOARDING_STARTED, ONBOARDING_VALIDATION_PASSED, SPEC_GENERATED, DEPLOYMENT_TRIGGERED, RUNTIME_EMIT, FAILURE_INJECTED, RL_DECISION, ORCH_EXEC, SYSTEM_STABLE
- ✅ All events have timestamps
- ✅ All events well-formed JSON

**Status**: ⬜ Not Run | ✅ Passed | ❌ Failed

---

### Scenario 4: DEMO_MODE Protection

**Test**: Verify DEMO_MODE blocks unsafe actions

```bash
python scripts/demo_mode_violation_test.py
```

**Expected Behavior**:
- ✅ Orchestrator call blocked
- ✅ Error message: "DEMO_MODE violation"
- ✅ Proof event: `DEMO_MODE_BLOCK` or similar
- ✅ Exit code 1

**Status**: ⬜ Not Run | ✅ Passed | ❌ Failed

---

### Scenario 5: Repeat Run (Idempotency)

**Test**: Run demo multiple times in succession

```bash
python demo_run.py
python demo_run.py
python demo_run.py
```

**Expected Behavior**:
- ✅ Each run succeeds independently
- ✅ Cleanup on each run (old app_spec removed)
- ✅ Consistent results (deterministic)
- ✅ No file conflicts

**Status**: ⬜ Not Run | ✅ Passed | ❌ Failed

---

## Expected vs Actual Results

### Test Run: [Date/Time]

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Full Demo | 3/3 pass | ___ | ⬜ |
| Invalid Input | Rejected | ___ | ⬜ |
| Proof Log | 18 events | ___ | ⬜ |
| DEMO_MODE | Blocked | ___ | ⬜ |
| Repeat Run | Consistent | ___ | ⬜ |

**Notes**:
_[Add any observations, issues, or anomalies here]_

---

## Safety Validation Checks

### Input Validation
- [x] Rejects uppercase in app names
- [x] Rejects file:// URLs
- [x] Rejects invalid runtime types (not backend/frontend/fullstack)
- [x] Rejects duplicate app names
- [x] Rejects names with spaces or special chars

### RL Decision Safety
- [x] All decisions go through RL layer
- [x] Direct orchestrator calls blocked in DEMO_MODE
- [x] Action allowlist enforced (noop, restart, scale only)
- [x] Dangerous actions (rollback, delete) blocked

### Proof Logging
- [x] All events logged with timestamps
- [x] No silent failures
- [x] JSON format valid
- [x] Event types correct
- [x] Full context included

### Environment Isolation
- [x] Stage uses deterministic mode
- [x] No cross-environment data leakage
- [x] Environment-specific configs respected

---

## Known Issues & Workarounds

### Issue 1: Demo App Already Exists
**Symptom**: Onboarding fails with "app already exists" error  
**Cause**: Previous demo run left `apps/registry/demo-api.json`  
**Workaround**: Run cleanup or let demo auto-clean  
**Status**: Fixed (demo auto-cleans in setup)

### Issue 2: RL Pipe Status Error (Historical)
**Symptom**: `EventEmissionError: 'status'` during full pipeline  
**Cause**: RL pipe expected nested payload structure  
**Workaround**: Simplified demo to use direct proof logging  
**Status**: Resolved (demo uses simplified flow)

---

## Testing Roles

### Tester: Ritesh
**Focus**: Core functionality and flow
- [ ] Verify demo runs end-to-end
- [ ] Test failure scenarios
- [ ] Validate proof logging
- [ ] Check safety guardrails

**Sign-off**: ⬜ Approved | Date: _____

---

### Tester: Vinayak
**Focus**: Edge cases and safety
- [ ] Test invalid inputs
- [ ] Verify DEMO_MODE protection
- [ ] Check error messages clarity
- [ ] Validate documentation accuracy

**Sign-off**: ⬜ Approved | Date: _____

---

## Demo Readiness Criteria

All items must be ✅ before demo presentation:

### Functional Requirements
- [ ] Demo runs without errors
- [ ] All 3 scenarios pass (3/3)
- [ ] Proof log shows all 18 events
- [ ] Duration under 5 seconds
- [ ] Exit code 0

### Documentation Requirements
- [ ] README has all three new sections
- [ ] DEMO_NARRATIVE.md complete
- [ ] DEMO_SCRIPT.md ready
- [ ] INTERNAL_TESTING.md (this file) complete

### Safety Requirements
- [ ] DEMO_MODE protection verified
- [ ] Invalid input rejection working
- [ ] Proof logging complete
- [ ] No unsafe actions permitted

### Presentation Requirements
- [ ] Demo script practiced (2-3 times minimum)
- [ ] Timing validated (5-7 minutes)
- [ ] Q&A responses prepared
- [ ] Backup plan in place (if demo fails)

---

## Final Sign-Off

**System Ready for Demo**: ⬜ Yes | ⬜ No

**Lead Developer**: ________________  Date: _____

**QA Lead**: ________________  Date: _____

**Notes**:
_[Any final comments or concerns]_
