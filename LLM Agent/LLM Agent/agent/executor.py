from typing import Any, Dict, List
from .schemas import Plan, Step
from . import tools

def _run_tool(step: Step, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    依 step.tool 呼叫對應工具。
    state 用來存放中間結果，讓後續步驟可以用得到。
    """
    tool = step.tool
    args = step.args or {}

    if tool == "detect_objects":
        return {"objects": tools.detect_objects()}

    if tool == "get_3d_pose":
        obj_id = args.get("obj_id") or state.get("selected_obj_id")
        if not obj_id:
            # 沒有 obj_id 就請使用者選擇
            return tools.ask_user("我需要 obj_id 才能取得 3D 座標。請指定目標物（例如 obj_1 / obj_2），或描述要哪一個（紅色杯子/藍色杯子）。")
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
        return {"gripper": tools.gripper(args["state"])}

    if tool == "ask_user":
        return tools.ask_user(args["question"])

    return {"ok": False, "reason": f"Unknown tool: {tool}"}


def run_plan(plan: Plan) -> Dict[str, Any]:
    """
    執行一個 Plan：
    - 依序跑 steps
    - 收集 logs
    - 遇到 need_user 就停
    """
    state: Dict[str, Any] = {}
    logs: List[Dict[str, Any]] = []

    for idx, step in enumerate(plan.steps, start=1):
        out = _run_tool(step, state)

        # 更新 state（把關鍵輸出存起來給後續用）
        # 這裡用 update 是簡化版；你之後可以更嚴謹地管理 state
        if isinstance(out, dict):
            state.update(out)

        # 自動選目標（簡化版）：若有 objects 且 plan.target 有顏色/類別，就幫你挑一個 obj_id
        if "objects" in state and plan.target:
            objs = state["objects"]
            cls = plan.target.get("cls")
            color = plan.target.get("color")

            def match(o):
                if cls and o.get("cls") != cls:
                    return False
                if color and o.get("color") != color:
                    return False
                return True

            candidates = [o for o in objs if match(o)]
            if candidates and "selected_obj_id" not in state:
                state["selected_obj_id"] = candidates[0]["id"]

        

        logs.append({"i": idx, "step": step.model_dump(), "output": out})

        # 若 ask_user 回傳 need_user，就停下來
        if isinstance(out, dict) and out.get("need_user"):
            break

        # 若有 reachability 檢查失敗，也可以停（示範）
        if "reachability" in state and isinstance(state["reachability"], dict):
            if state["reachability"].get("ok") is False:
                break

    return {"state": state, "logs": logs}
