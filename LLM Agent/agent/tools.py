from typing import Any, Dict, List


def detect_objects() -> List[Dict[str, Any]]:
    # 先用假資料：模擬視覺偵測結果
    return [
        {"id": "obj_1", "cls": "cup", "color": "red"},
        {"id": "obj_2", "cls": "cup", "color": "blue"},
        {"id": "obj_3", "cls": "sponge", "color": "yellow"},
    ]


def get_3d_pose(obj_id: str) -> Dict[str, Any]:
    # 假資料：模擬 3D 座標
    return {"obj_id": obj_id, "x": 0.30, "y": 0.10, "z": 0.20, "frame": "base"}


def check_reachable(pose: Dict[str, Any]) -> Dict[str, Any]:
    # 假資料：永遠可達(之後你可改成 IK/工作空間檢查)
    return {"ok": True, "reason": ""}


def move_ptp(pose: Dict[str, Any], speed: float = 0.2) -> Dict[str, Any]:
    # 假資料：模擬機械手臂移動
    return {"ok": True, "log": f"Moved to {pose} at speed={speed}"}


def gripper(state: str) -> Dict[str, Any]:
    # state: "open" / "close"
    if state not in {"open", "close"}:
        return {"ok": False, "reason": "Invalid gripper state, expected 'open' or 'close'."}
    return {"ok": True, "state": state}


def ask_user(question: str) -> Dict[str, Any]:
    # 這個工具代表「需要人回覆」
    return {"need_user": True, "question": question}
