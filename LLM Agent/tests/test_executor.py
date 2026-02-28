from agent.executor import run_plan
from agent.schemas import Plan


def test_run_plan_autoselects_target_object():
    plan = Plan.model_validate(
        {
            "intent": "pick red cup",
            "steps": [
                {"tool": "detect_objects"},
                {"tool": "get_3d_pose"},
            ],
            "target": {"cls": "cup", "color": "red"},
        }
    )

    result = run_plan(plan)

    assert result["state"]["selected_obj_id"] == "obj_1"
    assert result["state"]["pose"]["obj_id"] == "obj_1"


def test_run_plan_gripper_missing_state_returns_error():
    plan = Plan.model_validate(
        {
            "intent": "close gripper",
            "steps": [
                {"tool": "gripper", "args": {}},
            ],
        }
    )

    result = run_plan(plan)

    assert result["logs"][0]["output"]["ok"] is False
    assert "Missing state for gripper" in result["logs"][0]["output"]["reason"]
