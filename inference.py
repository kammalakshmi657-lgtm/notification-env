import os, json, requests

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

def get_mock_labels(task_id, obs):
    notifs = obs.get("notifications", [])
    if task_id == "task1":
        return [{"notification_id": n["id"], "category": "informational"} for n in notifs]
    elif task_id == "task2":
        return [{"notification_id": n["id"], "priority_rank": i+1} for i, n in enumerate(notifs)]
    else:
        return [{"notification_id": n["id"], "action": "dismiss", "summary": None} for n in notifs]

def run_task(task_id, seed=42):
    obs = call_reset(task_id, seed)
    labels = get_mock_labels(task_id, obs)
    action = {"task_id": task_id, "labels": labels}

    print(f"[START] task={task_id}", flush=True)

    result = call_step(action)
    reward = result["reward"]
    score = reward["score"]

    print(f"[STEP] step=1 reward={score}", flush=True)
    print(f"[END] task={task_id} score={score} steps=1", flush=True)

    return {"task_id": task_id, "score": score, "feedback": reward["feedback"]}

if __name__ == "__main__":
    results = []
    for task_id in ["task1", "task2", "task3"]:
        try:
            result = run_task(task_id)
            results.append(result)
        except Exception as e:
            print(f"[START] task={task_id}", flush=True)
            print(f"[STEP] step=1 reward=0.0", flush=True)
            print(f"[END] task={task_id} score=0.0 steps=1", flush=True)
            results.append({"task_id": task_id, "score": 0.0, "feedback": str(e)})
    print(json.dumps({"model": MODEL_NAME, "results": results}, indent=2), flush=True)