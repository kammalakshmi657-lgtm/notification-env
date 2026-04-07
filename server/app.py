from fastapi import FastAPI, HTTPException
from models import Action, Observation, StepResult, State
from env import NotificationEnv, TASKS

app = FastAPI(title="Notification Prioritization Environment", version="1.0.0")
env = NotificationEnv()

class ResetRequest:
    pass

from pydantic import BaseModel

from typing import Optional
class ResetReq(BaseModel):
    task_id: Optional[str] = "task1"
    seed: Optional[int] = 42
@app.get("/")
def root():
    return {"status": "ok", "env": "notification-prioritization", "version": "1.0.0"}

@app.post("/reset")
def reset(req: Optional[ResetReq] = None):
    if req is None:
        req = ResetReq()
    try:
        obs = env.reset(task_id=req.task_id, seed=req.seed)
        return obs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/step")
def step(action: Action):
    try:
        result = env.step(action)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def state():
    return env.state()

@app.get("/tasks")
def get_tasks():
    return {"tasks": [{"task_id": tid, "description": TASKS[tid]["description"], "difficulty": TASKS[tid]["difficulty"], "action_schema": {"task_id": "string", "labels": [{"notification_id": "string", "category": "urgent|informational|promotional|social [Task1]", "priority_rank": "integer 1-N [Task2]", "action": "dismiss|snooze|act_now|escalate [Task3]", "summary": "string for escalated [Task3]"}]}} for tid in TASKS]}

@app.post("/grader")
def grader():
    s = env.state()
    if not s.done:
        raise HTTPException(status_code=400, detail="Episode not completed yet. Call /step first.")
    return {"task_id": s.task_id, "score": s.last_score, "done": s.done}
@app.get("/validate")
def validate():
    results = []
    for tid in TASKS:
        try:
            env.reset(task_id=tid, seed=42)
            results.append({"task_id": tid, "status": "ok"})
        except Exception as e:
            results.append({"task_id": tid, "status": "error", "detail": str(e)})
    return {"validation": results}

@app.post("/baseline")
def baseline():
    import subprocess, sys, json, os
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not set.")
    try:
        result = subprocess.run([sys.executable, "baseline.py", "--output", "json"], capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Baseline script timed out.")
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
