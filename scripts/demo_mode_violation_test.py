from core.rl_orchestrator_safe import execute_action

print("🔒 Testing DEMO_MODE protection...")

execute_action(
    action="restart",
    env="stage",
    source="manual_test"
)
