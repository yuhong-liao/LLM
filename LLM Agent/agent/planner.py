import os, json
from openai import OpenAI
from .schemas import Plan
from .prompts import SYSTEM_PROMPT

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

    raw = resp.choices[0].message.content.strip()

    # 解析 JSON + schema 驗證
    data = json.loads(raw)
    return Plan.model_validate(data)
