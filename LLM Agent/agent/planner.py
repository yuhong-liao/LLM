import json
import os

from openai import OpenAI
from pydantic import ValidationError

from .prompts import SYSTEM_PROMPT
from .schemas import Plan


def make_plan(user_text: str) -> Plan:
    # 這裡才讀環境變數（確保 main.py 已 load_dotenv）
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("planner.py 找不到 OPENAI_API_KEY，請確認 main.py 有先 load_dotenv() 且 .env 正確。")

    client = OpenAI(api_key=api_key)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.2,
    )

    raw = (resp.choices[0].message.content or "").strip()
    if not raw:
        raise RuntimeError("LLM 回傳空內容，無法產生計畫。")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM 回傳非 JSON 格式內容：{raw}") from exc

    try:
        return Plan.model_validate(data)
    except ValidationError as exc:
        raise RuntimeError(f"LLM 回傳 JSON 結構不符合 Plan schema：{data}") from exc
