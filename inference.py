import os, json, requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://kammalakshmi-notification-prioritization-env.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

def call_reset(task_id, seed=42):
    r = requests.post(f"{API_BASE_URL}/reset", json={"task_id": task_id, "seed": seed})
    r.raise_for_status()
    return r.json()

def call_step(action):
    r = requests.post(f"{API_BASE_URL}/step", json=action)
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
    return f"""For each notification choose: dismiss, snooze, act_now, or escalate.\n\nNotifications:\n{lines}\n\nRespond ONLY with JSON:\n{{"labels": [{{"notification_id": "notif_000", "action": "escalate", "summary": "Critical issue"}},{{"notification_id": "notif_001", "action": "dismiss", "summary": null}}]}}\n"""

def run_task(client, task_id, seed=42):
    obs = call_reset(task_id, seed)
    if task_id == "task1":
        prompt = build_prompt_task1(obs)
    elif task_id == "task2":
        prompt = build_prompt_task2(obs)
    else:
        prompt = build_prompt_task3(obs)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("`"):
        raw = raw.split("`")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    parsed = json.loads(raw.strip())
    action = {"task_id": task_id, "labels": parsed["labels"]}
    result = call_step(action)
    reward = result["reward"]
    return {"task_id": task_id, "score": reward["score"], "feedback": reward["feedback"]}

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    results = []
    for task_id in ["task1", "task2", "task3"]:
        try:
            result = run_task(client, task_id)
            results.append(result)
        except Exception as e:
            results.append({"task_id": task_id, "score": 0.0, "feedback": str(e)})
    print(json.dumps({"model": MODEL_NAME, "results": results}, indent=2))