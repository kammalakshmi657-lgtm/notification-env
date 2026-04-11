from models import Observation, StepResult, State
from data import generate_task1_batch, generate_task2_batch, generate_task3_batch
from graders import GRADERS

# 🔥 FINAL SAFE CLAMP
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


TASKS = {
    "task1": {
        "description": "Classify notifications",
        "difficulty": "easy",
        "max_steps": 1,
        "generator": generate_task1_batch,
    },
    "task2": {
        "description": "Rank notifications",
        "difficulty": "medium",
        "max_steps": 1,
        "generator": generate_task2_batch,
    },
    "task3": {
        "description": "Triage notifications",
        "difficulty": "hard",
        "max_steps": 1,
        "generator": generate_task3_batch,
    },
}


class NotificationEnv:
    def __init__(self):
        self._task_id = None
        self._notifications = []
        self._ground_truth = {}
        self._step_count = 0
        self._done = False
        self._last_score = None

    def reset(self, task_id="task1", seed=42):
        task = TASKS[task_id]
        notifications, ground_truth = task["generator"](seed=seed)

        self._task_id = task_id
        self._notifications = notifications
        self._ground_truth = ground_truth
        self._step_count = 0
        self._done = False
        self._last_score = None

        return Observation(
            task_id=task_id,
            task_description=task["description"],
            notifications=notifications,
            step=0,
            max_steps=1,
        )

    def step(self, action):
        grader = GRADERS[self._task_id]
        reward = grader(action, self._ground_truth)

        # 🔥🔥 FINAL FIX (CRITICAL)
        safe_score = clamp_score(reward.score)
        reward.score = safe_score
        self._last_score = safe_score

        self._step_count += 1
        self._done = True

        next_obs = Observation(
            task_id=self._task_id,
            task_description=TASKS[self._task_id]["description"],
            notifications=self._notifications,
            step=self._step_count,
            max_steps=1,
        )

        return StepResult(
            observation=next_obs,
            reward=reward,
            done=True,
            info={"task_id": self._task_id},
        )

    def state(self):
        return State(
            task_id=self._task_id or "none",
            step=self._step_count,
            notifications=self._notifications,
            last_score=self._last_score,
            done=self._done,
        )