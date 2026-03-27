import os, json, argparse, requests
from openai import OpenAI

BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

def call_reset(task_id, seed):
    r = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id, "seed": seed})
    r.raise_for_status()
    return r.json()

def call_step(action):
    r = requests.post(f"{BASE_URL}/step", json=action)
    r.raise_for_status()
    return r.json()

def build_prompt_task1(obs):
    notifs = obs["notifications"]
    lines = "\n".join(f"[{n['id']}] Source: {n['source']} | Title: {n['title']} | Body: {n['body']}" for n in notifs)
    return f"""Classify each notification into exactly one category: urgent, informational, promotional, or social.\n\nNotifications:\n{lines}\n\nRespond ONLY with JSON:\n{{"labels": [{{"notification_id": "notif_000", "category": "urgent"}}]}}\n"""

def build_prompt_task2(obs):
    notifs = obs["notifications"]
    lines = "\n".join(f"[{n['id']}] Source: {n['source']} | Title: {n['title']} | Body: {n['body']}" for n in notifs)
    n = len(notifs)
    return f"""Rank these {n} notifications by urgency. Assign priority_rank 1 (most urgent) to {n} (least urgent).\n\nNotifications:\n{lines}\n\nRespond ONLY with JSON:\n{{"labels": [{{"notification_id": "notif_000", "priority_rank": 1}}]}}\n"""

def build_prompt_task3(obs):
    notifs = obs["notifications"]
    lines = "\n".join(f"[{n['id']}] Source: {n['source']} | Title: {n['title']} | Body: {n['body']}" for n in notifs)
    return f"""For each notification choose: dismiss, snooze, act_now, or escalate. For escalated ones add a 1-line summary.\n\nNotifications:\n{lines}\n\nRespond ONLY with JSON:\n{{"labels": [{{"notification_id": "notif_000", "action": "escalate", "summary": "Critical issue needs immediate attention"}},{{"notification_id": "notif_001", "action": "dismiss", "summary": null}}]}}\n"""

def run_task(client, task_id, seed, model):
    obs = call_reset(task_id, seed)
    if task_id == "task1":
        prompt = build_prompt_task1(obs)
    elif task_id == "task2":
        prompt = build_prompt_task2(obs)
    else:
        prompt = build_prompt_task3(obs)
    response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], temperature=0.0)
    raw = response.choices[0].message.content.strip()
    if raw.startswith("`"):
        raw = raw.split("`")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    parsed = json.loads(raw)
    action = {"task_id": task_id, "labels": parsed["labels"]}
    result = call_step(action)
    reward = result["reward"]
    return {"task_id": task_id, "score": reward["score"], "feedback": reward["feedback"], "partial_scores": reward.get("partial_scores", {})}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--output", choices=["table", "json"], default="table")
    args = parser.parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
    client = OpenAI(api_key=api_key)
    results = []
    for task_id in ["task1", "task2", "task3"]:
        try:
            result = run_task(client, task_id, args.seed, args.model)
            results.append(result)
        except Exception as e:
            results.append({"task_id": task_id, "score": 0.0, "feedback": str(e), "partial_scores": {}})
    if args.output == "json":
        print(json.dumps({"model": args.model, "seed": args.seed, "results": results}, indent=2))
    else:
        print("\n" + "="*60)
        print(f"  Baseline Results — model: {args.model} | seed: {args.seed}")
        print("="*60)
        total = 0.0
        for r in results:
            difficulty = {"task1": "easy", "task2": "medium", "task3": "hard"}[r["task_id"]]
            print(f"  {r['task_id']} ({difficulty:6s})  score: {r['score']:.4f}  | {r['feedback']}")
            total += r["score"]
        print("="*60)
        print(f"  Average score: {total/len(results):.4f}")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
