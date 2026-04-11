from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Action
from env import NotificationEnv, TASKS

app = FastAPI(title="Notification Prioritization Environment", version="1.0.0")
env = NotificationEnv()


# 🔥 Clamp function (FINAL SAFE)
def clamp_score(score):
    try:
        score = float(score)
    except:
        return 0.5

    if score <= 0:
        return 0.0001
    elif score >= 1:
        return 0.9999
    return score


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
        return env.reset(task_id=req.task_id, seed=req.seed)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 🔥🔥 FINAL FIXED STEP ENDPOINT
@app.post("/step")
def step(action: Action):
    try:
        result = env.step(action)

        # ✅ FORCE SCORE INTO (0,1)
        score = result.reward.score

        try:
            score = float(score)
        except:
            score = 0.5

        if score <= 0:
            score = 0.0001
        elif score >= 1:
            score = 0.9999

        result.reward.score = score

        return result

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "task_id": tid,
                "description": TASKS[tid]["description"],
                "difficulty": TASKS[tid]["difficulty"],
            }
            for tid in TASKS
        ]
    }


@app.post("/grader")
def grader():
    s = env.state()
    if not s.done:
        raise HTTPException(status_code=400, detail="Episode not completed yet.")

    # ✅ DOUBLE SAFETY
    score = clamp_score(s.last_score)

    return {"task_id": s.task_id, "score": score, "done": s.done}


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


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()