#!/usr/bin/env python3
"""
Cleanup Script - Remove Non-Essential Files

Removes documentation, old demo scripts, test files, and utilities
that are not required for core system operation.
"""

import os
import shutil

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Files to delete
FILES_TO_DELETE = [
    # Documentation & Summary Files
    "BUG_CHECK_SUMMARY.md",
    "DATASET_GUIDE.md",
    "DAY2_DEMO_SUMMARY.md",
    "DAY2_IMPLEMENTATION_SUMMARY.md",
    "DEMO_CHECKLIST.md",
    "DEMO_FREEZE_PROOF_SUMMARY.md",
    "DEMO_HARDENING_COMPLETE.md",
    "FEBRUARY_SHOWCASE_SCRIPT.md",
    "FINAL_TASK_STATUS.md",
    "MIGRATION_GUIDE.md",
    "NORMALIZATION_SUMMARY.md",
    "PRODUCTION_CHECKLIST.md",
    "PROD_SAFETY_TEST_RESULTS.md",
    "QA_FLOW.md",
    "QA_INTEGRATION_SUMMARY.md",
    "QUICKSTART_NEW_DATASETS.md",
    "QUICK_REFERENCE.md",
    "README_CORE.md",
    "README_DEMO_READY.md",
    "REFLECTION.md",
    "RL_VERIFICATION_GUIDE.md",
    "SCENARIO_TEST_GUIDE.md",
    "STAGE_DETERMINISM_SUMMARY.md",
    "TEST_FIXES_SUMMARY.md",
    "apps/INTEGRATION_SYNC.md",
    
    # Old Demo Scripts
    "day1_fixed_demo.py",
    "day2_closed_loop_demo.py",
    "day2_onboarding_rl_demo.py",
    "demo_hardened_flow.py",
    "demo_onboarding.py",
    "demo_prod_safety_in_stage.py",
    "demo_proof_orchestrator.py",
    "demo_universal_devops.py",
    "generate_demo_output.py",
    "run_quick_demo.py",
    
    # Test & Verification Scripts
    "DAY6_TEST.py",
    "day6_end_to_end_test.py",
    "day6_multi_app_test.py",
    "day6_scenario_test.py",
    "env_matrix_test.py",
    "run_day6_test.py",
    "test_build_deploy.py",
    "test_datasets.py",
    "test_day2_demo.py",
    "test_false_alarm.py",
    "test_false_alarm_clean.py",
    "test_fix3_simple.py",
    "test_payload_validation.py",
    "test_prod_safety_in_stage.py",
    "test_refusal_clean.py",
    "test_runtime_rl_wiring.py",
    "test_safe_execution.py",
    "test_stage_determinism.py",
    "test_stage_runtime_determinism.py",
    "test_structured_proof.py",
    "test_system_stabilization.py",
    "test_whitelist_enforcement.py",
    "verify_day2_deps.py",
    "verify_demo_freeze.py",
    "verify_failure_injection.py",
    "verify_fix4.py",
    "verify_fix5_comprehensive.py",
    "verify_fix5_final.py",
    "verify_onboarding.py",
    "verify_rl_orchestrator_task.py",
    "verify_rl_policy.py",
    "comprehensive_validation.py",
    "final_validation.py",
    "final_verification.py",
    "simple_task_verification.py",
    
    # Cleanup & Utility Scripts
    "cleanup_day7.py",
    "update_imports.py",
    "normalize_logs.py",
    "extract_proof.py",
    "file_proof.py",
    "generate_proof.py",
    "check_event_schema.py",
    
    # Sample/Example Files
    "example_invalid_input.json",
    "example_valid_input.json",
    "ritesh_automation_data.json",
    
    # Old Config Files
    "demo_freeze_config.py",
    "run_3_scenarios.py",
]

# Directories to delete
DIRS_TO_DELETE = [
    "demo_artifacts/demo_20260121_155125",
    "demo_artifacts/demo_20260122_151733",
    "demo_artifacts/demo_20260122_153339",
]

def delete_file(filepath):
    """Delete a single file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Deleted: {filepath}")
            return True
        else:
            print(f"⚠️  Not found: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {filepath}: {e}")
        return False

def delete_directory(dirpath):
    """Delete a directory and all its contents."""
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            print(f"✅ Deleted directory: {dirpath}")
            return True
        else:
            print(f"⚠️  Not found: {dirpath}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {dirpath}: {e}")
        return False

def main():
    """Main cleanup function."""
    print("=" * 79)
    print("CLEANUP SCRIPT - Removing Non-Essential Files")
    print("=" * 79)
    print()
    
    os.chdir(PROJECT_ROOT)
    
    deleted_files = 0
    deleted_dirs = 0
    not_found = 0
    errors = 0
    
    # Delete files
    print("Deleting files...")
    print("-" * 79)
    for file in FILES_TO_DELETE:
        filepath = os.path.join(PROJECT_ROOT, file)
        result = delete_file(filepath)
        if result:
            deleted_files += 1
        elif not os.path.exists(filepath):
            not_found += 1
        else:
            errors += 1
    
    print()
    
    # Delete directories
    print("Deleting directories...")
    print("-" * 79)
    for dir in DIRS_TO_DELETE:
        dirpath = os.path.join(PROJECT_ROOT, dir)
        result = delete_directory(dirpath)
        if result:
            deleted_dirs += 1
        elif not os.path.exists(dirpath):
            not_found += 1
        else:
            errors += 1
    
    print()
    print("=" * 79)
    print("CLEANUP SUMMARY")
    print("=" * 79)
    print(f"Files deleted: {deleted_files}")
    print(f"Directories deleted: {deleted_dirs}")
    print(f"Not found: {not_found}")
    print(f"Errors: {errors}")
    print()
    print(f"Total items processed: {len(FILES_TO_DELETE) + len(DIRS_TO_DELETE)}")
    print("=" * 79)
    
    if errors > 0:
        print(f"\n⚠️  WARNING: {errors} items could not be deleted due to errors")
        return 1
    else:
        print("\n✅ Cleanup completed successfully!")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
