import os
from dotenv import load_dotenv
from agent.planner import make_plan
from agent.executor import run_plan

def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("找不到 OPENAI_API_KEY，請確認 .env。")

    while True:
        user = input("你：").strip()
        if user.lower() in ["exit", "quit"]:
            break

        plan = make_plan(user)
        print("\n[PLAN JSON]")
        print(plan.model_dump_json(indent=2, ensure_ascii=False))

        result = run_plan(plan)
        print("\n[EXECUTION LOG]")
        for item in result["logs"]:
            print(item)

        # 如果需要澄清，顯示問題
        if plan.need_clarification:
            print("\n[NEED CLARIFICATION]")
            print(plan.question)

        print()

if __name__ == "__main__":
    main()
