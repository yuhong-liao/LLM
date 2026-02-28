from typing import Any, Dict, List

from . import tools
from .schemas import Plan, Step


def _run_tool(step: Step, state: Dict[str, Any]) -> Dict[str, Any]:
    """依 step.tool 呼叫對應工具並回傳輸出。"""
    tool = step.tool
    args = step.args or {}

    if tool == "detect_objects":
        return {"objects": tools.detect_objects()}

    if tool == "get_3d_pose":
        obj_id = args.get("obj_id") or state.get("selected_obj_id")
        if not obj_id:
            return tools.ask_user(
                "我需要 obj_id 才能取得 3D 座標。請指定目標物（例如 obj_1 / obj_2），或描述要哪一個（紅色杯子/藍色杯子）。"
            )
        return {"pose": tools.get_3d_pose(obj_id)}

    if tool == "check_reachable":
        pose = args.get("pose") or state.get("pose")
        if pose is None:
            return {"ok": False, "reason": "Missing pose for check_reachable"}
        return {"reachability": tools.check_reachable(pose)}

    if tool == "move_ptp":
        pose = args.get("pose") or state.get("pose")
        if pose is None:
            return {"ok": False, "reason": "Missing pose for move_ptp"}
        speed = float(args.get("speed", 0.2))
        return {"move": tools.move_ptp(pose, speed=speed)}

    if tool == "gripper":
        gripper_state = args.get("state")
        if not gripper_state:
            return {"ok": False, "reason": "Missing state for gripper (expected 'open' or 'close')"}
        return {"gripper": tools.gripper(gripper_state)}

    if tool == "ask_user":
        question = args.get("question", "請提供下一步指示。")
        return tools.ask_user(question)

    return {"ok": False, "reason": f"Unknown tool: {tool}"}


def _autoselect_target(plan: Plan, state: Dict[str, Any]) -> None:
    """如果已偵測到物件且 plan.target 存在，嘗試自動挑選 selected_obj_id。"""
    if "objects" not in state or not plan.target or "selected_obj_id" in state:
        return

    objs = state["objects"]
    cls = plan.target.get("cls")
    color = plan.target.get("color")

    def match(obj: Dict[str, Any]) -> bool:
        if cls and obj.get("cls") != cls:
            return False
        if color and obj.get("color") != color:
            return False
        return True

    candidates = [obj for obj in objs if match(obj)]
    if candidates:
        state["selected_obj_id"] = candidates[0]["id"]


def run_plan(plan: Plan) -> Dict[str, Any]:
    """依序執行計畫，回傳最終 state 與每一步 logs。"""
    state: Dict[str, Any] = {}
    logs: List[Dict[str, Any]] = []

    for idx, step in enumerate(plan.steps, start=1):
        out = _run_tool(step, state)

        if isinstance(out, dict):
            state.update(out)

        _autoselect_target(plan, state)

        logs.append({"i": idx, "step": step.model_dump(), "output": out})

        if isinstance(out, dict) and out.get("need_user"):
            break

        if "reachability" in state and isinstance(state["reachability"], dict):
            if state["reachability"].get("ok") is False:
                break

    return {"state": state, "logs": logs}
